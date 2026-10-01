# Topic 12 — Multi-Step Reasoning Assessment

## Project Overview

This project implements a controlled multi-step reasoning workflow for the Tayana AI Agent Architecture assessment.

The implementation focuses on breaking a reasoning goal into observable subgoals, tracking concise evidence, measuring progress, revising selected completed subgoals through bounded backtracking, and producing a final synthesis only after all required subgoals are complete.

The implementation deliberately does **not** expose hidden chain-of-thought. Instead, it records concise evidence summaries, state transitions, validation outcomes, and trace events that can be inspected and tested.

## Project Structure

```text
Multi_Step_Reasoning_Assessment/
├── reasoning.py
├── task1_decomposition.py
├── task2_evidence.py
├── task3_progress.py
├── task4_backtracking.py
├── task5_synthesis.py
├── tests/
│   ├── test_task1.py
│   ├── test_task2.py
│   ├── test_task3.py
│   ├── test_task4.py
│   └── test_task5.py
├── traces/
│   ├── task1_trace.json
│   ├── task2_trace.json
│   ├── task3_trace.json
│   ├── task4_trace.json
│   └── task5_trace.json
├── outputs/
│   └── reasoning_report.json
├── requirements.txt
├── .gitignore
└── README.md
```

## Implementation

The main implementation is contained in `reasoning.py`.

### Core components

- `ReasoningState` — stores subgoals, concise evidence, and completed subgoals.
- `ReasoningEvent` — represents an observable trace event.
- `ReasoningEngine` — provides the controlled reasoning workflow.
- `ReasoningError` — provides controlled failure handling.
- `FailureType` — categorizes validation, transient, permanent, and timeout failure types.
- `trace_to_dict()` — converts trace events into JSON-compatible data.

## Task 1 — Subgoal Decomposition

The engine validates the incoming goal and decomposes it into a bounded set of observable subgoals.

The implemented workflow creates four subgoals:

1. Define input
2. Check constraints
3. Evaluate evidence
4. Prepare conclusion

Invalid or empty goals are rejected with a validation failure.

### Evidence

- `task1_decomposition.py`
- `tests/test_task1.py`
- `traces/task1_trace.json`

Task result: **8/8 tests passed**

## Task 2 — Evidence Tracking

The implementation records concise evidence when a subgoal is completed.

Evidence validation checks that:

- Evidence is textual.
- Evidence is not empty.
- Evidence does not exceed the number of completed subgoals.
- Secret-like content is rejected.

### Evidence

- `task2_evidence.py`
- `tests/test_task2.py`
- `traces/task2_trace.json`

Task result: **8/8 tests passed**

## Task 3 — Progress Tracking

The engine calculates observable reasoning progress using:

- Total subgoals
- Completed subgoals
- Remaining subgoals
- Completion percentage
- Evidence count

Invalid progress accounting is rejected when completed plus remaining subgoals does not match the declared total.

### Evidence

- `task3_progress.py`
- `tests/test_task3.py`
- `traces/task3_trace.json`

Task result: **8/8 tests passed**

## Task 4 — Bounded Backtracking

The engine supports targeted revision of a previously completed subgoal.

When backtracking:

1. The selected completed subgoal is removed from the completed list.
2. Its associated evidence is removed.
3. The subgoal is returned to the pending subgoal list.
4. A backtrack event records the revision reason.
5. A configurable maximum number of backtracks prevents unbounded revision.

The default maximum is two backtracks.

### Evidence

- `task4_backtracking.py`
- `tests/test_task4.py`
- `traces/task4_trace.json`

Task result: **8/8 tests passed**

## Task 5 — Synthesis

Final synthesis is allowed only after all subgoals are completed.

The synthesis output contains:

- Final conclusion
- Supporting observable evidence
- Completed subgoals
- Progress information
- Backtrack count
- Limitations

Premature synthesis is rejected while pending subgoals remain.

### Evidence

- `task5_synthesis.py`
- `tests/test_task5.py`
- `traces/task5_trace.json`
- `outputs/reasoning_report.json`

Task result: **8/8 tests passed**

## Guardrails

The implementation includes the following controls:

### Step and scope limits

A maximum number of subgoals is enforced by `MAX_SUBGOALS`.

### Validation

Invalid goals, state values, evidence, progress counts, backtracking requests, conclusions, and limitations are rejected with controlled validation failures.

### Bounded backtracking

Backtracking is limited by `max_backtracks`, preventing unlimited revision loops.

### Secret hygiene

Secret-like values such as API keys, tokens, and passwords are rejected from reasoning inputs and observable evidence. Trace messages are also redacted where applicable.

### Traceability

Each major state transition records an observable event with the relevant subgoal, concise message, and timing information where applicable.

### Hidden chain-of-thought protection

The implementation does not expose private chain-of-thought. The externally visible artifacts contain concise evidence summaries, state transitions, validation outcomes, and final conclusions.

### Timeout and retry applicability

The local reasoning operations are deterministic and do not perform network or external service calls, so external-operation timeout and transient retry handling are not exercised in this assessment. The failure taxonomy includes `TIMEOUT` and `TRANSIENT` categories for controlled extension to external operations.

## Running the Project

Activate the virtual environment:

```cmd
.venv\Scripts\activate
```

Install dependencies:

```cmd
pip install -r requirements.txt
```

Run an individual task:

```cmd
python task1_decomposition.py
python task2_evidence.py
python task3_progress.py
python task4_backtracking.py
python task5_synthesis.py
```

Run the complete automated test suite:

```cmd
python -m pytest -q
```

## Final Verification

Final full-suite verification:

```text
40 passed in 0.07s
```

This represents all five task test files passing:

```text
Task 1:  8 passed
Task 2:  8 passed
Task 3:  8 passed
Task 4:  8 passed
Task 5:  8 passed
-------------------
Total:  40 passed
```

## Observable Submission Evidence

The project saves JSON traces for each task under `traces/`.

The final synthesis report is saved as:

```text
outputs/reasoning_report.json
```

These artifacts provide inspectable evidence of successful paths, validation/rejection paths, progress, backtracking, and synthesis without exposing hidden reasoning.

## Reflection

This project helped me understand how multi-step reasoning can be implemented as a controlled engineering workflow rather than treating reasoning as an unstructured model response. The main design decision was to represent reasoning state explicitly through subgoals, completed work, evidence, and trace events. This made it possible to test each part of the workflow independently and to verify that invalid states were rejected.

The decomposition task established a bounded sequence of observable subgoals. Evidence tracking then connected completed work to concise evidence, while progress tracking made the state measurable throughout execution. Bounded backtracking was particularly useful because it demonstrated how a reasoning system can revise a selected step without allowing unlimited revision loops. The final synthesis step brought the validated state together into a conclusion while retaining supporting evidence and limitations.

A key implementation principle was avoiding exposure of hidden chain-of-thought. Instead of returning private reasoning, the project exposes only concise evidence, state transitions, validation results, and final synthesis information. This provides useful observability while keeping internal reasoning private.

The assessment also reinforced the importance of guardrails. Validation, subgoal limits, bounded backtracking, secret hygiene, and traceability make the reasoning workflow more predictable and testable. The final result contains automated tests for both successful and rejected operations across all five tasks. The complete suite passed 40 tests, providing evidence that the implemented behavior is consistent with the defined requirements.

Overall, the project gave me practical experience designing a structured reasoning component that can be evaluated through state, evidence, failure handling, and measurable progress rather than relying only on the final answer.
