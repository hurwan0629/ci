# Communication
- Before editing, restate the user's goal, proposed changes, and affected files in plain language.
- Confirm that you understood the request and ask what the user wants changed before proceeding. Clarify ambiguity instead of guessing.
- Explain significant design decisions so the user can understand and approve them.
- After editing, summarize what changed, why, and what was verified. Ask whether the result matches the user's intent.

# Scope
- Write only the code necessary for the approved request.
- Do not add unrelated features, speculative abstractions, or unrequested refactoring.
- Use descriptive names; avoid excessive abbreviations and unnecessary complexity.

# Architecture
- Keep each module focused on one responsibility and avoid circular dependencies.
- Reuse an existing module when the responsibility fits. Add or split modules when a distinct responsibility justifies it.
- Explain the reason and impact before introducing modules, dependencies, or structural changes.

# Python and Data
- Use Python type hints for function parameters and return values.
- Use Pydantic for validating external inputs and outputs; do not use it for every internal type.
- Use Dockerized PostgreSQL. Track schema changes with migrations.
- Never delete data, reset databases, or commit secrets without explicit authorization.

# Verification
- Use pytest and add or update tests for changed behavior.
- After code changes, run the full test suite and available lint/type checks.
- Do not report work as complete if checks fail or cannot run; disclose failures and unverified work.
- Measure performance before claiming an optimization or performance guarantee.
