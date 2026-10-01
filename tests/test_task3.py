import pytest

from reasoning import (
    FailureType,
    ReasoningEngine,
    ReasoningError,
    ReasoningState,
)


def test_initial_progress_is_zero_percent():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[
            "one",
            "two",
            "three",
            "four",
        ]
    )

    progress = engine.progress(
        state
    )

    assert progress[
        "total_subgoals"
    ] == 4

    assert progress[
        "completed_subgoals"
    ] == 0

    assert progress[
        "remaining_subgoals"
    ] == 4

    assert progress[
        "completion_percent"
    ] == 0.0


def test_half_completed_progress():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[
            "one",
            "two",
            "three",
            "four",
        ]
    )

    engine.complete_next(state)
    engine.complete_next(state)

    progress = engine.progress(
        state
    )

    assert progress[
        "completed_subgoals"
    ] == 2

    assert progress[
        "remaining_subgoals"
    ] == 2

    assert progress[
        "completion_percent"
    ] == 50.0

    assert progress[
        "evidence_count"
    ] == 2


def test_complete_progress_is_100_percent():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[
            "one",
            "two",
        ]
    )

    engine.complete_next(state)
    engine.complete_next(state)

    progress = engine.progress(
        state
    )

    assert progress[
        "completion_percent"
    ] == 100.0

    assert progress[
        "completed_subgoals"
    ] == 2

    assert progress[
        "remaining_subgoals"
    ] == 0


def test_progress_rejects_inconsistent_total():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[
            "one",
            "two",
        ]
    )

    with pytest.raises(
        ReasoningError
    ) as exc_info:
        engine.progress(
            state,
            total_subgoals=5,
        )

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_progress_rejects_zero_total():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[]
    )

    with pytest.raises(
        ReasoningError
    ) as exc_info:
        engine.progress(
            state,
            total_subgoals=0,
        )

    assert (
        exc_info.value.failure_type
        == FailureType.VALIDATION
    )


def test_progress_reports_evidence_count():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[
            "one",
            "two",
        ]
    )

    engine.complete_next(state)

    progress = engine.progress(
        state
    )

    assert progress[
        "evidence_count"
    ] == 1


def test_progress_trace_is_recorded():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[
            "one",
        ]
    )

    engine.progress(state)

    events = [
        event.event
        for event in engine.trace
    ]

    assert (
        "progress_reported"
        in events
    )


def test_progress_after_each_step():
    engine = ReasoningEngine()

    state = ReasoningState(
        subgoals=[
            "one",
            "two",
            "three",
        ]
    )

    observed = []

    for expected in (
        0.0,
        33.33,
        66.67,
        100.0,
    ):
        progress = engine.progress(
            state
        )

        observed.append(
            progress[
                "completion_percent"
            ]
        )

        if state.subgoals:
            engine.complete_next(state)

    assert observed == [
        0.0,
        33.33,
        66.67,
        100.0,
    ]