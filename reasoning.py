from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import perf_counter
from typing import Any
import re


class FailureType(str, Enum):
    NONE = "none"
    VALIDATION = "validation"
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    TIMEOUT = "timeout"


class ReasoningError(Exception):
    """Controlled reasoning failure."""

    def __init__(
        self,
        message: str,
        failure_type: FailureType = FailureType.PERMANENT,
    ) -> None:
        super().__init__(message)
        self.failure_type = failure_type


@dataclass
class ReasoningState:
    """
    State maintained during multi-step reasoning.

    Internal reasoning details are not exposed as hidden
    chain-of-thought. Only concise evidence summaries
    and observable state transitions are recorded.
    """

    subgoals: list[str]
    evidence: list[str] = field(default_factory=list)
    completed: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.subgoals, list):
            raise ReasoningError(
                "Subgoals must be provided as a list.",
                FailureType.VALIDATION,
            )

        if any(
            not isinstance(item, str)
            or not item.strip()
            for item in self.subgoals
        ):
            raise ReasoningError(
                "Every subgoal must be a non-empty string.",
                FailureType.VALIDATION,
            )


@dataclass
class ReasoningEvent:
    event: str
    subgoal: str | None
    message: str
    duration_ms: float | None = None


class ReasoningEngine:
    """
    Controlled multi-step reasoning engine.

    Responsibilities include:

    - subgoal decomposition
    - evidence validation
    - progress measurement
    - bounded backtracking
    - final synthesis
    - step limits
    - traceability
    - secret hygiene

    Internal chain-of-thought is never stored or exposed.
    Only concise, observable reasoning artifacts are recorded.
    """

    MAX_SUBGOALS = 10
    DEFAULT_MAX_BACKTRACKS = 2

    SECRET_PATTERNS = (
        re.compile(r"sk-[A-Za-z0-9_-]+"),
        re.compile(
            r"api[_-]?key\s*=\s*[^\s]+",
            re.IGNORECASE,
        ),
        re.compile(
            r"token\s*=\s*[^\s]+",
            re.IGNORECASE,
        ),
        re.compile(
            r"password\s*=\s*[^\s]+",
            re.IGNORECASE,
        ),
    )

    def __init__(
        self,
        max_subgoals: int = MAX_SUBGOALS,
        max_backtracks: int = DEFAULT_MAX_BACKTRACKS,
    ) -> None:
        self.max_subgoals = max_subgoals
        self.max_backtracks = max_backtracks
        self.backtrack_count = 0
        self.trace: list[ReasoningEvent] = []

    # =========================================================
    # Trace and security helpers
    # =========================================================

    def _redact(self, value: str) -> str:
        """Remove common secret-like values from trace messages."""

        redacted = value

        for pattern in self.SECRET_PATTERNS:
            redacted = pattern.sub(
                "[REDACTED]",
                redacted,
            )

        return redacted

    def _contains_secret(
        self,
        value: str,
    ) -> bool:
        """Return True when a value contains secret-like content."""

        return any(
            pattern.search(value)
            for pattern in self.SECRET_PATTERNS
        )

    def _record(
        self,
        event: str,
        subgoal: str | None,
        message: str,
        duration_ms: float | None = None,
    ) -> None:
        """Record a concise, redacted observable event."""

        self.trace.append(
            ReasoningEvent(
                event=event,
                subgoal=subgoal,
                message=self._redact(message),
                duration_ms=duration_ms,
            )
        )

    # =========================================================
    # Task 1 — State validation
    # =========================================================

    def validate_state(
        self,
        state: ReasoningState,
    ) -> None:
        """Validate the reasoning state before processing."""

        if not isinstance(
            state,
            ReasoningState,
        ):
            raise ReasoningError(
                "Invalid reasoning state.",
                FailureType.VALIDATION,
            )

        if len(state.subgoals) > self.max_subgoals:
            raise ReasoningError(
                f"Subgoal limit exceeded: "
                f"{len(state.subgoals)} > "
                f"{self.max_subgoals}.",
                FailureType.VALIDATION,
            )

        if len(state.completed) > self.max_subgoals:
            raise ReasoningError(
                "Completed subgoal limit exceeded.",
                FailureType.VALIDATION,
            )

        if any(
            self._contains_secret(item)
            for item in state.subgoals
            if isinstance(item, str)
        ):
            raise ReasoningError(
                "Secret-like content is not allowed "
                "in subgoals.",
                FailureType.VALIDATION,
            )

        if any(
            not isinstance(item, str)
            or not item.strip()
            for item in state.completed
        ):
            raise ReasoningError(
                "Completed subgoals must be "
                "non-empty strings.",
                FailureType.VALIDATION,
            )

    # =========================================================
    # Task 1 — Subgoal decomposition
    # =========================================================

    def decompose(
        self,
        goal: str,
    ) -> ReasoningState:
        """
        Decompose a supported goal into observable subgoals.
        """

        self.trace.clear()
        self.backtrack_count = 0

        if not isinstance(
            goal,
            str,
        ) or not goal.strip():

            self._record(
                "reasoning_rejected",
                None,
                "Goal must be a non-empty string.",
            )

            raise ReasoningError(
                "Goal must be a non-empty string.",
                FailureType.VALIDATION,
            )

        if self._contains_secret(goal):
            self._record(
                "reasoning_rejected",
                None,
                "Secret-like content rejected from goal.",
            )

            raise ReasoningError(
                "Secret-like content rejected from goal.",
                FailureType.VALIDATION,
            )

        normalized_goal = goal.strip()

        self._record(
            "reasoning_started",
            None,
            f"Decomposing goal: {normalized_goal}",
        )

        state = ReasoningState(
            subgoals=[
                "define input",
                "check constraints",
                "evaluate evidence",
                "prepare conclusion",
            ]
        )

        self.validate_state(state)

        self._record(
            "subgoals_created",
            None,
            f"Created {len(state.subgoals)} "
            f"observable subgoals.",
        )

        return state

    def complete_next(
        self,
        state: ReasoningState,
    ) -> ReasoningState:
        """
        Complete exactly one subgoal.
        """

        self.validate_state(state)

        if not state.subgoals:
            self._record(
                "reasoning_complete",
                None,
                "No remaining subgoals.",
            )

            return state

        start = perf_counter()

        subgoal = state.subgoals.pop(0)

        state.evidence.append(
            f"Evidence recorded for: {subgoal}"
        )

        state.completed.append(
            subgoal
        )

        elapsed = (
            perf_counter() - start
        ) * 1000

        self._record(
            "subgoal_completed",
            subgoal,
            "Subgoal completed with concise evidence.",
            duration_ms=elapsed,
        )

        if not state.subgoals:
            self._record(
                "reasoning_complete",
                None,
                "All subgoals completed.",
            )

        return state

    # =========================================================
    # Task 2 — Evidence tracking
    # =========================================================

    def validate_evidence(
        self,
        state: ReasoningState,
    ) -> None:
        """
        Validate concise evidence records.
        """

        self.validate_state(state)

        if len(state.evidence) > len(
            state.completed
        ):
            self._record(
                "evidence_rejected",
                None,
                "Evidence count exceeds completed "
                "subgoal count.",
            )

            raise ReasoningError(
                "Evidence cannot exceed the number "
                "of completed subgoals.",
                FailureType.VALIDATION,
            )

        for evidence in state.evidence:

            if not isinstance(
                evidence,
                str,
            ):
                self._record(
                    "evidence_rejected",
                    None,
                    "Evidence must be text.",
                )

                raise ReasoningError(
                    "Evidence must be text.",
                    FailureType.VALIDATION,
                )

            if not evidence.strip():
                self._record(
                    "evidence_rejected",
                    None,
                    "Evidence cannot be empty.",
                )

                raise ReasoningError(
                    "Evidence cannot be empty.",
                    FailureType.VALIDATION,
                )

            if self._contains_secret(
                evidence
            ):
                self._record(
                    "evidence_rejected",
                    None,
                    "Secret-like content rejected "
                    "from evidence.",
                )

                raise ReasoningError(
                    "Secret-like content rejected "
                    "from evidence.",
                    FailureType.VALIDATION,
                )

        self._record(
            "evidence_validated",
            None,
            "Evidence passed validation.",
        )

    # =========================================================
    # Task 3 — Progress tracking
    # =========================================================

    def progress(
        self,
        state: ReasoningState,
        total_subgoals: int | None = None,
    ) -> dict[str, Any]:
        """
        Return concise observable progress information.
        """

        self.validate_state(state)
        self.validate_evidence(state)

        if total_subgoals is None:
            total_subgoals = (
                len(state.subgoals)
                + len(state.completed)
            )

        if total_subgoals <= 0:
            self._record(
                "progress_rejected",
                None,
                "Total subgoals must be positive.",
            )

            raise ReasoningError(
                "Total subgoals must be positive.",
                FailureType.VALIDATION,
            )

        completed_count = len(
            state.completed
        )

        remaining_count = len(
            state.subgoals
        )

        if (
            completed_count
            + remaining_count
            != total_subgoals
        ):
            self._record(
                "progress_rejected",
                None,
                "Progress counts do not match "
                "the total subgoal count.",
            )

            raise ReasoningError(
                "Progress counts do not match "
                "the total subgoal count.",
                FailureType.VALIDATION,
            )

        completion_percent = round(
            (
                completed_count
                / total_subgoals
            )
            * 100,
            2,
        )

        progress = {
            "total_subgoals": total_subgoals,
            "completed_subgoals": completed_count,
            "remaining_subgoals": remaining_count,
            "completion_percent": completion_percent,
            "evidence_count": len(
                state.evidence
            ),
        }

        self._record(
            "progress_reported",
            None,
            (
                f"Progress: "
                f"{completed_count}/"
                f"{total_subgoals} completed."
            ),
        )

        return progress

    # =========================================================
    # Task 4 — Bounded backtracking
    # =========================================================

    def backtrack(
        self,
        state: ReasoningState,
        subgoal: str,
        reason: str,
    ) -> ReasoningState:
        """
        Revisit a completed subgoal when new evidence
        invalidates the previous result.
        """

        self.validate_state(state)
        self.validate_evidence(state)

        if not isinstance(
            subgoal,
            str,
        ) or not subgoal.strip():
            raise ReasoningError(
                "Backtracking requires a valid subgoal.",
                FailureType.VALIDATION,
            )

        if not isinstance(
            reason,
            str,
        ) or not reason.strip():
            raise ReasoningError(
                "Backtracking requires a reason.",
                FailureType.VALIDATION,
            )

        if self._contains_secret(reason):
            raise ReasoningError(
                "Secret-like content rejected "
                "from backtracking reason.",
                FailureType.VALIDATION,
            )

        if self.backtrack_count >= self.max_backtracks:
            self._record(
                "backtrack_rejected",
                subgoal,
                (
                    "Backtracking limit exceeded: "
                    f"{self.max_backtracks}."
                ),
            )

            raise ReasoningError(
                "Backtracking limit exceeded.",
                FailureType.VALIDATION,
            )

        if subgoal not in state.completed:
            self._record(
                "backtrack_rejected",
                subgoal,
                "Subgoal has not been completed.",
            )

            raise ReasoningError(
                "Cannot backtrack to a subgoal "
                "that has not been completed.",
                FailureType.VALIDATION,
            )

        self.backtrack_count += 1

        state.completed.remove(
            subgoal
        )

        matching_prefix = (
            f"Evidence recorded for: {subgoal}"
        )

        state.evidence = [
            item
            for item in state.evidence
            if item != matching_prefix
        ]

        state.subgoals.insert(
            0,
            subgoal,
        )

        self._record(
            "backtrack",
            subgoal,
            (
                "Previous result invalidated; "
                f"revisiting subgoal. "
                f"Reason: {reason}"
            ),
        )

        return state

    # =========================================================
    # Task 5 — Synthesis
    # =========================================================

    def synthesize(
        self,
        state: ReasoningState,
        conclusion: str,
        limitations: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Produce a concise final synthesis.

        The synthesis contains the observable conclusion,
        supporting evidence, progress information, and
        limitations. Hidden chain-of-thought is never returned.
        """

        self.validate_state(state)
        self.validate_evidence(state)

        if state.subgoals:
            self._record(
                "synthesis_rejected",
                None,
                "Cannot synthesize while subgoals remain.",
            )

            raise ReasoningError(
                "Cannot synthesize while subgoals remain.",
                FailureType.VALIDATION,
            )

        if not isinstance(
            conclusion,
            str,
        ) or not conclusion.strip():
            self._record(
                "synthesis_rejected",
                None,
                "Conclusion must be a non-empty string.",
            )

            raise ReasoningError(
                "Conclusion must be a non-empty string.",
                FailureType.VALIDATION,
            )

        if self._contains_secret(
            conclusion
        ):
            self._record(
                "synthesis_rejected",
                None,
                "Secret-like content rejected "
                "from conclusion.",
            )

            raise ReasoningError(
                "Secret-like content rejected "
                "from conclusion.",
                FailureType.VALIDATION,
            )

        if limitations is None:
            limitations = []

        if not isinstance(
            limitations,
            list,
        ):
            raise ReasoningError(
                "Limitations must be provided as a list.",
                FailureType.VALIDATION,
            )

        for limitation in limitations:

            if not isinstance(
                limitation,
                str,
            ) or not limitation.strip():
                raise ReasoningError(
                    "Limitations must contain "
                    "non-empty strings.",
                    FailureType.VALIDATION,
                )

            if self._contains_secret(
                limitation
            ):
                raise ReasoningError(
                    "Secret-like content rejected "
                    "from limitations.",
                    FailureType.VALIDATION,
                )

        start = perf_counter()

        progress = self.progress(
            state
        )

        synthesis = {
            "conclusion": conclusion.strip(),
            "supporting_evidence": list(
                state.evidence
            ),
            "completed_subgoals": list(
                state.completed
            ),
            "progress": progress,
            "backtrack_count": (
                self.backtrack_count
            ),
            "limitations": [
                item.strip()
                for item in limitations
            ],
        }

        elapsed = (
            perf_counter() - start
        ) * 1000

        self._record(
            "synthesis_complete",
            None,
            "Final synthesis generated from "
            "validated observable evidence.",
            duration_ms=elapsed,
        )

        return synthesis


# =============================================================
# Trace serialization
# =============================================================

def trace_to_dict(
    trace: list[ReasoningEvent],
) -> list[dict[str, Any]]:
    """Convert reasoning events to JSON-compatible records."""

    return [
        {
            "event": event.event,
            "subgoal": event.subgoal,
            "message": event.message,
            "duration_ms": event.duration_ms,
        }
        for event in trace
    ]