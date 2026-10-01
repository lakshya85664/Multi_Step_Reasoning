import json
from pathlib import Path

from reasoning import (
    ReasoningEngine,
    ReasoningError,
    trace_to_dict,
)


TRACE_PATH = Path(
    "traces/task5_trace.json"
)

REPORT_PATH = Path(
    "outputs/reasoning_report.json"
)


def demonstrate_success():
    engine = ReasoningEngine(
        max_backtracks=2
    )

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    print("\nREASONING WORKFLOW")
    print("-" * 60)

    while state.subgoals:
        engine.complete_next(state)

    synthesis = engine.synthesize(
        state,
        conclusion=(
            "The candidate solution satisfies "
            "the evaluated reasoning criteria."
        ),
        limitations=[
            "The conclusion is based only on "
            "the supplied observable evidence."
        ],
    )

    print(
        f"Conclusion: "
        f"{synthesis['conclusion']}"
    )

    print(
        f"Completed subgoals: "
        f"{synthesis['completed_subgoals']}"
    )

    print(
        f"Evidence count: "
        f"{len(synthesis['supporting_evidence'])}"
    )

    print(
        f"Completion: "
        f"{synthesis['progress']['completion_percent']}%"
    )

    print(
        f"Backtracks: "
        f"{synthesis['backtrack_count']}"
    )

    print(
        f"Limitations: "
        f"{synthesis['limitations']}"
    )

    return synthesis, engine.trace


def demonstrate_rejection():
    engine = ReasoningEngine()

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    print("\nREJECTION PATH")
    print("-" * 60)

    try:
        engine.synthesize(
            state,
            conclusion=(
                "Premature conclusion."
            ),
        )

    except ReasoningError as exc:
        print(
            f"Rejected premature synthesis: "
            f"{exc}"
        )

        print(
            f"failure_type="
            f"{exc.failure_type.value}"
        )

    return engine.trace


def main():
    print("=" * 70)
    print("Topic 12 — Task 5: Synthesis")
    print("=" * 70)

    synthesis, success_trace = (
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

    output = {
        "synthesis": synthesis,
        "trace_event_count": (
            len(success_trace)
            + len(rejection_trace)
        ),
    }

    TRACE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.parent.mkdir(
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

    REPORT_PATH.write_text(
        json.dumps(
            output,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nTRACE SAVED")
    print(TRACE_PATH)

    print("\nREPORT SAVED")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()