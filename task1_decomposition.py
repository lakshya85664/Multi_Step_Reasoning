import json
from pathlib import Path

from reasoning import (
    ReasoningEngine,
    ReasoningError,
    trace_to_dict,
)


TRACE_PATH = Path("traces/task1_trace.json")


def demonstrate_success():
    engine = ReasoningEngine()

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    print("\nSUCCESS PATH")
    print("-" * 60)

    print(
        f"Initial subgoals: "
        f"{state.subgoals}"
    )

    while state.subgoals:
        engine.complete_next(state)

    print(
        f"Completed: "
        f"{state.completed}"
    )

    print(
        f"Evidence count: "
        f"{len(state.evidence)}"
    )

    return state, engine.trace


def demonstrate_rejection():
    engine = ReasoningEngine()

    print("\nREJECTION PATH")
    print("-" * 60)

    try:
        engine.decompose("")

    except ReasoningError as exc:
        print(
            f"Rejected invalid goal: "
            f"{exc}"
        )
        print(
            f"failure_type="
            f"{exc.failure_type.value}"
        )

    return engine.trace


def main():
    print("=" * 70)
    print("Topic 12 — Task 1: Subgoal Decomposition")
    print("=" * 70)

    success_state, success_trace = (
        demonstrate_success()
    )

    rejection_trace = demonstrate_rejection()

    combined_trace = {
        "success": trace_to_dict(
            success_trace
        ),
        "rejection": trace_to_dict(
            rejection_trace
        ),
        "final_completed": (
            success_state.completed
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