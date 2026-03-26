from scripts.ci.check_repo_guardrails import run_repo_guardrails


def test_repo_guardrails_pass_for_current_baseline() -> None:
    run_repo_guardrails()
