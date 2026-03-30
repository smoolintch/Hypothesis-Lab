from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .errors import InvalidMarketDatasetError, MarketDatasetNotFoundError
from .models import BacktestRange, Candle, LoadedMarketDataset, MarketDatasetMetadata


DEFAULT_SOURCE = "fixture"
REPO_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_MARKET_DATA_DIR = REPO_ROOT / "data" / "market"
REQUIRED_COLUMNS = ("ts", "open", "high", "low", "close", "volume")
SUPPORTED_TIMEFRAME_DELTAS = {
    "4H": timedelta(hours=4),
    "1D": timedelta(days=1),
}


def load_market_candles(
    *,
    symbol: str,
    timeframe: str,
    version: str,
    backtest_range: BacktestRange | None = None,
    source: str = DEFAULT_SOURCE,
    market_data_dir: str | Path | None = None,
) -> LoadedMarketDataset:
    market_data_root = _resolve_market_data_root(market_data_dir)
    dataset_dir = _resolve_dataset_dir(
        market_data_root=market_data_root,
        source=source,
        symbol=symbol,
        timeframe=timeframe,
        version=version,
    )
    manifest = _load_manifest(dataset_dir)
    metadata = _build_metadata(dataset_dir, market_data_root, manifest)
    candles = _load_candles(dataset_dir, metadata)
    filtered_candles = _filter_candles(candles, backtest_range)
    return LoadedMarketDataset(metadata=metadata, candles=filtered_candles)


def _resolve_market_data_root(market_data_dir: str | Path | None) -> Path:
    if market_data_dir is not None:
        return _resolve_repo_relative_path(market_data_dir)

    env_value = os.getenv("MARKET_DATA_DIR")
    if env_value:
        return _resolve_repo_relative_path(env_value)

    return DEFAULT_MARKET_DATA_DIR


def _resolve_dataset_dir(
    *,
    market_data_root: Path,
    source: str,
    symbol: str,
    timeframe: str,
    version: str,
) -> Path:
    dataset_dir = market_data_root / source / symbol / timeframe / version
    if not dataset_dir.exists():
        raise MarketDatasetNotFoundError(
            f"Market dataset not found for source={source}, symbol={symbol}, timeframe={timeframe}, version={version}"
        )
    return dataset_dir


def _load_manifest(dataset_dir: Path) -> dict:
    manifest_path = dataset_dir / "manifest.json"
    if not manifest_path.exists():
        raise InvalidMarketDatasetError(f"Missing manifest.json in {dataset_dir}")

    with manifest_path.open("r", encoding="utf-8") as fh:
        manifest = json.load(fh)

    required_fields = {
        "id",
        "source",
        "symbol",
        "timeframe",
        "version",
        "coverage_start_at",
        "coverage_end_at",
        "candle_count",
        "storage_uri",
        "created_at",
        "timezone",
        "sort_order",
        "columns",
    }
    missing = sorted(required_fields - set(manifest.keys()))
    if missing:
        raise InvalidMarketDatasetError(
            f"{manifest_path} is missing required fields: {', '.join(missing)}"
        )

    return manifest


def _build_metadata(
    dataset_dir: Path,
    market_data_root: Path,
    manifest: dict,
) -> MarketDatasetMetadata:
    source, symbol, timeframe, version = dataset_dir.parts[-4:]
    comparisons = {
        "source": source,
        "symbol": symbol,
        "timeframe": timeframe,
        "version": version,
    }
    for key, expected in comparisons.items():
        actual = manifest[key]
        if actual != expected:
            raise InvalidMarketDatasetError(
                f"{dataset_dir / 'manifest.json'} has {key}={actual!r}, expected {expected!r}"
            )

    if manifest["timezone"] != "UTC":
        raise InvalidMarketDatasetError(f"{dataset_dir / 'manifest.json'} timezone must be UTC")

    if manifest["sort_order"] != "ts_asc":
        raise InvalidMarketDatasetError(f"{dataset_dir / 'manifest.json'} sort_order must be ts_asc")

    columns = tuple(manifest["columns"])
    if columns != REQUIRED_COLUMNS:
        raise InvalidMarketDatasetError(
            f"{dataset_dir / 'manifest.json'} columns must equal {list(REQUIRED_COLUMNS)}"
        )

    if timeframe not in SUPPORTED_TIMEFRAME_DELTAS:
        raise InvalidMarketDatasetError(f"Unsupported timeframe {timeframe!r}")

    storage_uri = Path(manifest["storage_uri"])
    expected_storage_uri = (dataset_dir / "candles.csv").relative_to(market_data_root.parent.parent)
    if storage_uri != expected_storage_uri:
        raise InvalidMarketDatasetError(
            f"{dataset_dir / 'manifest.json'} storage_uri must be {expected_storage_uri.as_posix()}"
        )

    return MarketDatasetMetadata(
        id=manifest["id"],
        source=manifest["source"],
        symbol=manifest["symbol"],
        timeframe=manifest["timeframe"],
        version=manifest["version"],
        coverage_start_at=_parse_utc_datetime(manifest["coverage_start_at"]),
        coverage_end_at=_parse_utc_datetime(manifest["coverage_end_at"]),
        candle_count=int(manifest["candle_count"]),
        storage_uri=manifest["storage_uri"],
        created_at=_parse_utc_datetime(manifest["created_at"]),
        timezone=manifest["timezone"],
        sort_order=manifest["sort_order"],
        columns=columns,
    )


def _load_candles(dataset_dir: Path, metadata: MarketDatasetMetadata) -> tuple[Candle, ...]:
    csv_path = dataset_dir / "candles.csv"
    if not csv_path.exists():
        raise InvalidMarketDatasetError(f"Missing candles.csv in {dataset_dir}")

    candles: list[Candle] = []
    previous_ts: datetime | None = None
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if tuple(reader.fieldnames or ()) != REQUIRED_COLUMNS:
            raise InvalidMarketDatasetError(
                f"{csv_path} header must be {list(REQUIRED_COLUMNS)}"
            )

        for row in reader:
            candle = Candle(
                ts=_parse_utc_datetime(row["ts"]),
                open=_parse_decimal(row["open"], csv_path, "open"),
                high=_parse_decimal(row["high"], csv_path, "high"),
                low=_parse_decimal(row["low"], csv_path, "low"),
                close=_parse_decimal(row["close"], csv_path, "close"),
                volume=_parse_decimal(row["volume"], csv_path, "volume"),
            )
            if previous_ts is not None and candle.ts <= previous_ts:
                raise InvalidMarketDatasetError(f"{csv_path} timestamps must be strictly increasing")
            previous_ts = candle.ts
            candles.append(candle)

    if len(candles) != metadata.candle_count:
        raise InvalidMarketDatasetError(
            f"{csv_path} row count {len(candles)} does not match manifest candle_count {metadata.candle_count}"
        )

    if not candles:
        raise InvalidMarketDatasetError(f"{csv_path} must contain at least one candle")

    if candles[0].ts != metadata.coverage_start_at:
        raise InvalidMarketDatasetError(f"{csv_path} first ts does not match coverage_start_at")

    expected_coverage_end = candles[-1].ts + SUPPORTED_TIMEFRAME_DELTAS[metadata.timeframe]
    if expected_coverage_end != metadata.coverage_end_at:
        raise InvalidMarketDatasetError(f"{csv_path} coverage_end_at does not match final candle range")

    return tuple(candles)


def _filter_candles(
    candles: tuple[Candle, ...],
    backtest_range: BacktestRange | None,
) -> tuple[Candle, ...]:
    if backtest_range is None:
        return candles

    if backtest_range.start_at >= backtest_range.end_at:
        raise InvalidMarketDatasetError("backtest_range end_at must be later than start_at")

    filtered = tuple(
        candle
        for candle in candles
        if backtest_range.start_at <= candle.ts < backtest_range.end_at
    )
    return filtered


def _parse_utc_datetime(value: str) -> datetime:
    if not value.endswith("Z"):
        raise InvalidMarketDatasetError(f"{value!r} is not a UTC timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo != timezone.utc:
        raise InvalidMarketDatasetError(f"{value!r} is not normalized to UTC")
    return parsed


def _parse_decimal(value: str, csv_path: Path, field_name: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise InvalidMarketDatasetError(
            f"{csv_path} field {field_name}={value!r} is not a valid decimal"
        ) from exc


def _resolve_repo_relative_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()
