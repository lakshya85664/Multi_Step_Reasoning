import pytest

from reasoning import (
    FailureType,
    ReasoningEngine,
    ReasoningError,
    ReasoningState,
)


def complete_all(engine, state):
    while state.subgoals:
        engine.complete_next(state)


def test_successful_synthesis():
    engine = ReasoningEngine()

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    complete_all(
        engine,
        state,
    )

    result = engine.synthesize(
        state,
        conclusion=(
            "The solution satisfies the "
            "evaluated criteria."
        ),
    )

    assert (
        result["conclusion"]
        == "The solution satisfies the evaluated criteria."
    )

    assert (
        result["progress"]["completion_percent"]
        == 100.0
    )

    assert len(
        result["supporting_evidence"]
    ) == 4


def test_synthesis_contains_completed_subgoals():
    engine = ReasoningEngine()

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    complete_all(
        engine,
        state,
    )

    result = engine.synthesize(
        state,
        conclusion="Evaluation completed.",
    )

    assert result[
        "completed_subgoals"
    ] == [
        "define input",
        "check constraints",
        "evaluate evidence",
        "prepare conclusion",
    ]


def test_synthesis_reports_backtrack_count():
    engine = ReasoningEngine(
        max_backtracks=2
    )

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    engine.complete_next(state)

    engine.backtrack(
        state,
        "define input",
        "New evidence invalidated the earlier result.",
    )

    engine.complete_next(state)

    while state.subgoals:
        engine.complete_next(state)

    result = engine.synthesize(
        state,
        conclusion="Revised evaluation completed.",
    )

    assert result[
        "backtrack_count"
    ] == 1


def test_synthesis_reports_limitations():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[],
        completed=[
            "one"
        ],
        evidence=[
            "Evidence for one."
        ],
    )

    result = engine.synthesize(
        state,
        conclusion="Conclusion.",
        limitations=[
            "Evidence was limited to the supplied inputs."
        ],
    )

    assert result[
        "limitations"
    ] == [
        "Evidence was limited to the supplied inputs."
    ]


def test_synthesis_rejects_incomplete_reasoning():
    engine = ReasoningEngine()

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    with pytest.raises(
        ReasoningError
    ) as exc_info:
        engine.synthesize(
            state,
            conclusion="Too early.",
        )

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_synthesis_rejects_empty_conclusion():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[],
        completed=[
            "one"
        ],
        evidence=[
            "Evidence for one."
        ],
    )

    with pytest.raises(
        ReasoningError
    ) as exc_info:
        engine.synthesize(
            state,
            conclusion="",
        )

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_synthesis_rejects_secret_like_conclusion():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[],
        completed=[
            "one"
        ],
        evidence=[
            "Evidence for one."
        ],
    )

    with pytest.raises(
        ReasoningError
    ) as exc_info:
        engine.synthesize(
            state,
            conclusion="token=secret123",
        )

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_synthesis_trace_is_recorded():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[],
        completed=[
            "one"
        ],
        evidence=[
            "Evidence for one."
        ],
    )

    engine.synthesize(
        state,
        conclusion="Conclusion.",
    )

    events = [
        event.event
        for event in engine.trace
    ]

    assert (
        "synthesis_complete"
        in events
    )