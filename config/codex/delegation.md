## Codex Agent Delegation Policy

For Codex sessions, proactively delegate concrete, bounded, independent work when it saves substantial exploration or mechanical execution in the primary context. This is an explicit instruction to use subagents when the criteria below apply.

- The primary agent retains ambiguous requirements, architecture, difficult debugging, cross-module reasoning, algorithm design, security-sensitive decisions, tradeoffs, integration, and the final answer.
- Use `luna_explorer` (gpt-5.6-luna, medium, read-only) for well-scoped file/symbol searches, configuration or log inspection, small code-path tracing, and factual summaries requiring multiple searches or reads.
- Use `luna_worker` (gpt-5.6-luna, medium, workspace-write) only when the intended change is clear, localized, low risk, and easy to verify. Suitable work includes mechanical edits, straightforward configuration changes, simple scripts, and focused tests.
- Keep trivial work that needs only one or two simple operations with the primary agent. Do not delegate merely to use a subagent.
- Delegate only when the bounded task can proceed independently alongside useful primary-agent work. Give the agent explicit scope, expected output, relevant context, and validation criteria.
- Prefer independent read-only work in parallel. Assign one writer per file or subsystem; avoid overlapping edits.
- If a delegated task becomes ambiguous or reveals a deeper design issue, the subagent must return its evidence and uncertainty for the primary agent to decide instead of guessing.
- The primary agent reviews findings and diffs, resolves conflicts, verifies important conclusions, and owns the final result.
- If the runtime exposes only generic spawning rather than named custom agents, explicitly select gpt-5.6-luna with medium effort and include the appropriate explorer/worker instructions in the task. Use a scoped context rather than a full-history fork when a model override requires it.
- If Luna or custom agents are unavailable, report that limitation and continue with the primary agent; do not silently switch to a different paid model.
