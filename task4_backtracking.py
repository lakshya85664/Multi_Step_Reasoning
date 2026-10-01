import json
from pathlib import Path

from reasoning import (
    ReasoningEngine,
    ReasoningError,
    trace_to_dict,
)


TRACE_PATH = Path(
    "traces/task4_trace.json"
)


def demonstrate_success():
    engine = ReasoningEngine(
        max_backtracks=2
    )

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    print("\nINITIAL REASONING")
    print("-" * 60)

    engine.complete_next(state)
    engine.complete_next(state)

    print(
        f"Completed before backtrack: "
        f"{state.completed}"
    )

    state = engine.backtrack(
        state,
        "define input",
        "New evidence invalidated the earlier input interpretation.",
    )

    print("\nBOUNDED BACKTRACK")
    print("-" * 60)

    print(
        f"Backtrack count: "
        f"{engine.backtrack_count}"
    )

    print(
        f"Subgoals after backtrack: "
        f"{state.subgoals}"
    )

    engine.complete_next(state)

    print(
        f"Completed after revision: "
        f"{state.completed}"
    )

    return engine.trace


def demonstrate_limit_rejection():
    engine = ReasoningEngine(
        max_backtracks=1
    )

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    engine.complete_next(state)

    print("\nBACKTRACK LIMIT")
    print("-" * 60)

    engine.backtrack(
        state,
        "define input",
        "First evidence revision.",
    )

    try:
        engine.backtrack(
            state,
            "define input",
            "Second revision should exceed the limit.",
        )

    except ReasoningError as exc:
        print(
            f"Rejected excessive backtracking: "
            f"{exc}"
        )

        print(
            f"failure_type="
            f"{exc.failure_type.value}"
        )

    return engine.trace


def main():
    print("=" * 70)
    print("Topic 12 — Task 4: Bounded Backtracking")
    print("=" * 70)

    success_trace = (
        demonstrate_success()
    )

    rejection_trace = (
        demonstrate_limit_rejection()
    )

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