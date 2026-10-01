import pytest

from reasoning import (
    FailureType,
    ReasoningEngine,
    ReasoningError,
)


def test_backtracking_revisits_completed_subgoal():
    engine = ReasoningEngine(
        max_backtracks=2
    )

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    engine.complete_next(state)

    assert state.completed == [
        "define input"
    ]

    engine.backtrack(
        state,
        "define input",
        "New evidence invalidated the previous result.",
    )

    assert state.completed == []

    assert state.subgoals[0] == (
        "define input"
    )

    assert engine.backtrack_count == 1


def test_backtracking_removes_old_evidence():
    engine = ReasoningEngine(
        max_backtracks=2
    )

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    engine.complete_next(state)

    assert len(state.evidence) == 1

    engine.backtrack(
        state,
        "define input",
        "Previous evidence was invalidated.",
    )

    assert state.evidence == []


def test_backtracking_reason_is_traced():
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
        "New evidence changed the interpretation.",
    )

    events = [
        event.event
        for event in engine.trace
    ]

    assert "backtrack" in events


def test_backtracking_can_be_followed_by_recompletion():
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
        "Previous result was invalidated.",
    )

    engine.complete_next(state)

    assert state.completed == [
        "define input"
    ]

    assert len(state.evidence) == 1


def test_backtracking_limit_is_enforced():
    engine = ReasoningEngine(
        max_backtracks=1
    )

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    engine.complete_next(state)

    engine.backtrack(
        state,
        "define input",
        "First revision.",
    )

    # Re-complete the subgoal so it can be
    # legitimately selected for another revision.
    engine.complete_next(state)

    with pytest.raises(
        ReasoningError
    ) as exc_info:
        engine.backtrack(
            state,
            "define input",
            "Second revision.",
        )

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_uncompleted_subgoal_cannot_be_backtracked():
    engine = ReasoningEngine(
        max_backtracks=2
    )

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    with pytest.raises(
        ReasoningError
    ) as exc_info:
        engine.backtrack(
            state,
            "define input",
            "This has not been completed yet.",
        )

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_empty_backtrack_reason_is_rejected():
    engine = ReasoningEngine(
        max_backtracks=2
    )

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    engine.complete_next(state)

    with pytest.raises(
        ReasoningError
    ) as exc_info:
        engine.backtrack(
            state,
            "define input",
            "",
        )

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_secret_like_backtrack_reason_is_rejected():
    engine = ReasoningEngine(
        max_backtracks=2
    )

    state = engine.decompose(
        "evaluate a candidate solution"
    )

    engine.complete_next(state)

    with pytest.raises(
        ReasoningError
    ) as exc_info:
        engine.backtrack(
            state,
            "define input",
            "token=secret123 invalidated the result.",
        )

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )