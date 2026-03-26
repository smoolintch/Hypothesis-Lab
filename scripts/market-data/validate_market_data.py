from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MARKET_DATA_DIR = ROOT / "data" / "market"
REQUIRED_COLUMNS = ["ts", "open", "high", "low", "close", "volume"]
REQUIRED_MANIFEST_FIELDS = {
    "schema_version",
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
SUPPORTED_TIMEFRAMES = {
    "4H": timedelta(hours=4),
    "1D": timedelta(days=1),
}


@dataclass
class DatasetSummary:
    dataset_dir: Path
    row_count: int


def parse_utc(value: str) -> datetime:
    if not value.endswith("Z"):
        raise ValueError(f"{value} is not a UTC Z timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo != timezone.utc:
        raise ValueError(f"{value} is not normalized to UTC")
    return parsed


def discover_dataset_dirs(base: Path) -> list[Path]:
    if not base.exists():
        raise FileNotFoundError(f"Path does not exist: {base}")

    if (base / "manifest.json").exists() and (base / "candles.csv").exists():
        return [base]

    return sorted(
        {
            manifest.parent
            for manifest in base.glob("**/manifest.json")
            if (manifest.parent / "candles.csv").exists()
        }
    )


def load_manifest(dataset_dir: Path) -> dict:
    manifest_path = dataset_dir / "manifest.json"
    with manifest_path.open("r", encoding="utf-8") as fh:
        manifest = json.load(fh)

    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest.keys()))
    if missing:
        raise ValueError(f"{manifest_path}: missing manifest fields: {', '.join(missing)}")

    if manifest["timezone"] != "UTC":
        raise ValueError(f"{manifest_path}: timezone must be UTC")

    if manifest["sort_order"] != "ts_asc":
        raise ValueError(f"{manifest_path}: sort_order must be ts_asc")

    if manifest["columns"] != REQUIRED_COLUMNS:
        raise ValueError(f"{manifest_path}: columns must equal {REQUIRED_COLUMNS}")

    timeframe = manifest["timeframe"]
    if timeframe not in SUPPORTED_TIMEFRAMES:
        raise ValueError(f"{manifest_path}: unsupported timeframe {timeframe}")

    return manifest


def validate_directory_metadata(dataset_dir: Path, manifest: dict) -> None:
    expected_parts = dataset_dir.relative_to(DEFAULT_MARKET_DATA_DIR).parts
    if len(expected_parts) != 4:
        raise ValueError(
            f"{dataset_dir}: expected path format data/market/<source>/<symbol>/<timeframe>/<version>"
        )

    source, symbol, timeframe, version = expected_parts
    comparisons = {
        "source": source,
        "symbol": symbol,
        "timeframe": timeframe,
        "version": version,
    }
    for key, expected in comparisons.items():
        actual = manifest[key]
        if actual != expected:
            raise ValueError(f"{dataset_dir}: manifest {key}={actual!r} does not match path {expected!r}")

    storage_uri = manifest["storage_uri"]
    expected_storage_uri = dataset_dir.relative_to(ROOT) / "candles.csv"
    if Path(storage_uri) != expected_storage_uri:
        raise ValueError(
            f"{dataset_dir}: storage_uri must be {expected_storage_uri.as_posix()}, got {storage_uri}"
        )


def validate_candles(dataset_dir: Path, manifest: dict) -> DatasetSummary:
    csv_path = dataset_dir / "candles.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != REQUIRED_COLUMNS:
            raise ValueError(f"{csv_path}: header must be {REQUIRED_COLUMNS}")

        previous_ts: datetime | None = None
        first_ts: datetime | None = None
        last_ts: datetime | None = None
        row_count = 0

        for row in reader:
            row_count += 1
            current_ts = parse_utc(row["ts"])
            if first_ts is None:
                first_ts = current_ts
            if previous_ts is not None and current_ts <= previous_ts:
                raise ValueError(f"{csv_path}: timestamps must be strictly increasing")
            previous_ts = current_ts
            last_ts = current_ts

            for field in REQUIRED_COLUMNS[1:]:
                value = row[field]
                try:
                    float(value)
                except ValueError as exc:
                    raise ValueError(f"{csv_path}: field {field}={value!r} is not numeric") from exc

        if row_count == 0 or first_ts is None or last_ts is None:
            raise ValueError(f"{csv_path}: dataset must contain at least one candle row")

    if manifest["candle_count"] != row_count:
        raise ValueError(
            f"{csv_path}: candle_count={manifest['candle_count']} does not match actual rows={row_count}"
        )

    coverage_start_at = parse_utc(manifest["coverage_start_at"])
    coverage_end_at = parse_utc(manifest["coverage_end_at"])
    timeframe_delta = SUPPORTED_TIMEFRAMES[manifest["timeframe"]]

    if coverage_start_at != first_ts:
        raise ValueError(f"{csv_path}: coverage_start_at does not match first ts")

    if coverage_end_at != last_ts + timeframe_delta:
        raise ValueError(f"{csv_path}: coverage_end_at must equal last ts plus timeframe")

    return DatasetSummary(dataset_dir=dataset_dir, row_count=row_count)


def main() -> int:
    base = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_MARKET_DATA_DIR

    dataset_dirs = discover_dataset_dirs(base)
    if not dataset_dirs:
        raise FileNotFoundError(f"No dataset directories found under {base}")

    summaries: list[DatasetSummary] = []
    for dataset_dir in dataset_dirs:
        manifest = load_manifest(dataset_dir)
        validate_directory_metadata(dataset_dir, manifest)
        summaries.append(validate_candles(dataset_dir, manifest))

    for summary in summaries:
        rel_path = summary.dataset_dir.relative_to(ROOT)
        print(f"OK {rel_path.as_posix()} rows={summary.row_count}")

    print(f"Validated {len(summaries)} dataset(s).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - lightweight CLI path
        print(f"ERROR {exc}", file=sys.stderr)
        raise SystemExit(1)
