from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = (
    "AGENTS.md",
    ".env.example",
    "pnpm-workspace.yaml",
    "docs/MVP开发计划.md",
    "docs/project/current-status.md",
    "docs/contracts/domain-model.md",
    "docs/contracts/api-contracts.md",
    "docs/contracts/rule-template-schema-v1.md",
    "docs/product/user-flow-and-page-states.md",
    "docs/architecture/technical-solution-and-constraints.md",
    "docs/acceptance/acceptance-criteria-and-test-checklist.md",
    "docs/samples/ma-cross-btcusdt-4h.json",
    "docs/samples/rsi-threshold-ethusdt-1d.json",
    "data/market/README.md",
)

REQUIRED_DATASET_MANIFESTS = (
    "data/market/fixture/BTCUSDT/4H/sample-v1/manifest.json",
    "data/market/fixture/BTCUSDT/1D/sample-v1/manifest.json",
    "data/market/fixture/ETHUSDT/4H/sample-v1/manifest.json",
    "data/market/fixture/ETHUSDT/1D/sample-v1/manifest.json",
)


def _assert_files_exist(paths: tuple[str, ...]) -> None:
    missing_files = [path for path in paths if not (REPO_ROOT / path).is_file()]
    if missing_files:
        missing_list = ", ".join(missing_files)
        raise SystemExit(f"Missing required files: {missing_list}")


def run_repo_guardrails() -> None:
    _assert_files_exist(REQUIRED_FILES)
    _assert_files_exist(REQUIRED_DATASET_MANIFESTS)


if __name__ == "__main__":
    run_repo_guardrails()
