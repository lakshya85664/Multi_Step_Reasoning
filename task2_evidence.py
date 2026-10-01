import json
from pathlib import Path

from reasoning import (
    FailureType,
    ReasoningEngine,
    ReasoningError,
    ReasoningState,
    trace_to_dict,
)


TRACE_PATH = Path("traces/task2_trace.json")


def demonstrate_success():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[
            "identify input",
            "check constraints",
        ]
    )

    print("\nSUCCESS PATH")
    print("-" * 60)

    engine.complete_next(state)
    engine.complete_next(state)

    print(
        f"Completed: {state.completed}"
    )

    print(
        f"Evidence: {state.evidence}"
    )

    print(
        f"Evidence count: "
        f"{len(state.evidence)}"
    )

    return engine.trace


def demonstrate_rejection():
    engine = ReasoningEngine()

    print("\nREJECTION PATH")
    print("-" * 60)

    invalid_state = ReasoningState(
        subgoals=[
            "valid subgoal",
        ]
    )

    # Evidence entries must remain concise and
    # correspond to completed subgoals.
    invalid_state.evidence.append(
        "unsupported evidence"
    )

    try:
        engine.validate_evidence(
            invalid_state
        )

    except ReasoningError as exc:
        print(
            f"Rejected invalid evidence: "
            f"{exc}"
        )

        print(
            f"failure_type="
            f"{exc.failure_type.value}"
        )

    return engine.trace


def main():
    print("=" * 70)
    print("Topic 12 — Task 2: Evidence Tracking")
    print("=" * 70)

    success_trace = demonstrate_success()
    rejection_trace = demonstrate_rejection()

    combined_trace = {
        "success": trace_to_dict(
            success_trace
        ),
        "rejection": trace_to_dict(
            rejection_trace
        ),
    }

    TRACE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    TRACE_PATH.write_text(
        json.dumps(
            combined_trace,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nTRACE SAVED")
    print(TRACE_PATH)


if __name__ == "__main__":
    main()