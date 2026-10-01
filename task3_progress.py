import json
from pathlib import Path

from reasoning import (
    ReasoningEngine,
    ReasoningError,
    ReasoningState,
    trace_to_dict,
)


TRACE_PATH = Path(
    "traces/task3_trace.json"
)


def demonstrate_success():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[
            "evaluate input",
            "check constraints",
            "review evidence",
            "prepare conclusion",
        ]
    )

    print("\nSUCCESS PATH")
    print("-" * 60)

    progress = engine.progress(
        state
    )

    print(
        f"Initial progress: "
        f"{progress}"
    )

    engine.complete_next(state)
    engine.complete_next(state)

    progress = engine.progress(
        state
    )

    print(
        f"Updated progress: "
        f"{progress}"
    )

    engine.complete_next(state)
    engine.complete_next(state)

    progress = engine.progress(
        state
    )

    print(
        f"Final progress: "
        f"{progress}"
    )

    return engine.trace


def demonstrate_rejection():
    engine = ReasoningEngine()

    print("\nREJECTION PATH")
    print("-" * 60)

    state = ReasoningState(
        subgoals=[
            "one",
        ]
    )

    try:
        engine.progress(
            state,
            total_subgoals=5,
        )

    except ReasoningError as exc:
        print(
            f"Rejected invalid progress: "
            f"{exc}"
        )

        print(
            f"failure_type="
            f"{exc.failure_type.value}"
        )

    return engine.trace


def main():
    print("=" * 70)
    print("Topic 12 — Task 3: Progress")
    print("=" * 70)

    success_trace = (
        demonstrate_success()
    )

    rejection_trace = (
        demonstrate_rejection()
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