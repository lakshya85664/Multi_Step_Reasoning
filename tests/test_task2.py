import pytest

from reasoning import (
    FailureType,
    ReasoningEngine,
    ReasoningError,
    ReasoningState,
)


def test_completed_subgoal_creates_evidence():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[
            "identify input",
        ]
    )

    engine.complete_next(state)

    assert state.completed == [
        "identify input"
    ]

    assert state.evidence == [
        "Evidence recorded for: identify input"
    ]


def test_valid_evidence_is_accepted():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[],
        completed=[
            "identify input"
        ],
        evidence=[
            "Input format was identified."
        ],
    )

    engine.validate_evidence(state)

    assert (
        engine.trace[-1].event
        == "evidence_validated"
    )


def test_excess_evidence_is_rejected():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[],
        completed=[],
        evidence=[
            "unsupported evidence"
        ],
    )

    with pytest.raises(ReasoningError) as exc_info:
        engine.validate_evidence(state)

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_empty_evidence_is_rejected():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[],
        completed=[
            "identify input"
        ],
        evidence=[
            "   "
        ],
    )

    with pytest.raises(ReasoningError) as exc_info:
        engine.validate_evidence(state)

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_non_string_evidence_is_rejected():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[],
        completed=[
            "identify input"
        ],
        evidence=[
            123
        ],
    )

    with pytest.raises(ReasoningError) as exc_info:
        engine.validate_evidence(state)

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_secret_like_evidence_is_rejected():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[],
        completed=[
            "identify input"
        ],
        evidence=[
            "api_key=secret123"
        ],
    )

    with pytest.raises(ReasoningError) as exc_info:
        engine.validate_evidence(state)

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_evidence_trace_is_recorded():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[],
        completed=[
            "identify input"
        ],
        evidence=[
            "Input was identified."
        ],
    )

    engine.validate_evidence(state)

    events = [
        event.event
        for event in engine.trace
    ]

    assert (
        "evidence_validated"
        in events
    )


def test_evidence_matches_completed_work():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[
            "identify input",
            "check constraints",
        ]
    )

    engine.complete_next(state)
    engine.complete_next(state)

    engine.validate_evidence(state)

    assert len(state.evidence) == 2
    assert len(state.completed) == 2