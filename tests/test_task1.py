import pytest

from reasoning import (
    FailureType,
    ReasoningEngine,
    ReasoningError,
    ReasoningState,
)


def test_goal_is_decomposed_into_subgoals():
    engine = ReasoningEngine()

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    assert len(state.subgoals) == 4

    assert state.subgoals == [
        "define input",
        "check constraints",
        "evaluate evidence",
        "prepare conclusion",
    ]


def test_subgoal_completion_records_evidence():
    engine = ReasoningEngine()

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    engine.complete_next(state)

    assert state.completed == [
        "define input"
    ]

    assert state.evidence == [
        "Evidence recorded for: define input"
    ]

    assert state.subgoals == [
        "check constraints",
        "evaluate evidence",
        "prepare conclusion",
    ]


def test_all_subgoals_can_be_completed():
    engine = ReasoningEngine()

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    while state.subgoals:
        engine.complete_next(state)

    assert state.subgoals == []

    assert len(state.completed) == 4

    assert len(state.evidence) == 4


def test_empty_goal_is_rejected():
    engine = ReasoningEngine()

    with pytest.raises(ReasoningError) as exc_info:
        engine.decompose("")

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_whitespace_goal_is_rejected():
    engine = ReasoningEngine()

    with pytest.raises(ReasoningError):
        engine.decompose("   ")


def test_subgoal_limit_is_enforced():
    engine = ReasoningEngine(
        max_subgoals=2
    )

    state = ReasoningState(
        subgoals=[
            "one",
            "two",
            "three",
        ]
    )

    with pytest.raises(ReasoningError) as exc_info:
        engine.validate_state(state)

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_secret_like_goal_is_rejected():
    engine = ReasoningEngine()

    with pytest.raises(ReasoningError) as exc_info:
        engine.decompose(
            "use api_key=secret123"
        )

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_trace_contains_observable_events():
    engine = ReasoningEngine()

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    engine.complete_next(state)

    events = [
        event.event
        for event in engine.trace
    ]

    assert "reasoning_started" in events
    assert "subgoals_created" in events
    assert "subgoal_completed" in events