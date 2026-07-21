---
description: Prompt Heuristics for evaluating and refining user prompts
trigger: always_on
---

# Prompt Heuristics Guidelines

Always check incoming user prompts against these core prompt heuristics:

### 1. Be Specific
* **Headline**: NAME THE FILES, THE CASES, AND THE TOOLS
* **DON'T**: `add tests for foo.py`
* **DO**: `Write pytest tests for foo.py covering two cases: logged-out user and expired token. No mocks — use the test client in tests/conftest.py.`
* **Why**: Naming the file, the exact cases, and the tools to use removes guesswork and stops the agent from inventing its own scope.

### 2. Give Examples
* **Headline**: AN INPUT/OUTPUT PAIR PINS THE CONTRACT
* **DON'T**: `parse the dates in this CSV`
* **DO**: `Parse the created column. Example: "2026-03-09T14:00Z" → 1773064800000 (epoch ms). Three more pairs in tests/fixtures/dates.json — match them exactly.`
* **Why**: A concrete input → output pair (or a unit test) pins the contract far better than prose. Tests are executable examples the agent can run.

### 3. Decompose
* **Headline**: ONE COHERENT STEP AT A TIME
* **DON'T**: `migrate the whole app from REST to GraphQL`
* **DO**: `Step 1 only: expose the existing /users endpoint as a GraphQL query. Leave REST in place. Don't touch other endpoints yet.`
* **Why**: Small steps keep the diff reviewable and the context small. Migrate one service, not ten — then iterate on the next.

### 4. Remove Ambiguity
* **Headline**: KILL EVERY "THIS", "THAT", "THE OTHER ONE"
* **DON'T**: `fix it so this works like the other one`
* **DO**: `In PaymentForm.tsx, make the submit button disable-on-submit exactly like CheckoutForm.tsx (lines 40–62). Reuse the useDisableOnSubmit hook.`
* **Why**: Vague pronouns force the agent to guess which thing you mean. Name the file, the function, and the line range.

### 5. Point to Existing Patterns
* **Headline**: ANCHOR THE OUTPUT TO YOUR CODEBASE
* **DON'T**: `create a new widget component`
* **DO**: `Create a HotDogWidget that follows HamburgerWidget.tsx exactly: same props shape, same folder layout, same test-file structure`
* **Why**: Pointing at a reference file makes the output match your conventions instead of a generic internet style. “Follow the pattern in X.”

### 6. Iterate
* **Headline**: REPHRASE; DON'T PILE UP CORRECTIONS
* **DON'T**: `no, fix the colors too ... still broken ... now the header is wrong (all in one growing thread)`
* **DO**: `That approach used global state — let's restart. New prompt: implement the cart with a local reducer, following CartContext.tsx.`
* **Why**: After two failed corrections, /clear and rewrite the first prompt. Stacked fixes pollute the context and entrench the wrong approach.

### 7. State Boundaries & Positive Alternatives
* **Headline**: STATE WHAT TO PRESERVE & USE INSTEAD OF PURE NEGATIVES
* **DON'T**: `Refactor auth.py. Don't use global state or break legacy tokens.`
* **DO**: `Refactor auth_middleware.py using local state (useReducer). Maintain full backward compatibility with v1 token formats.`
* **Why**: Pure negatives ("don't X") confuse LLMs. Specifying positive alternatives and preservation boundaries directs the model effectively.

### 8. Explain the "Why" (Symptom & Context)
* **Headline**: EXPLAIN THE PROBLEM BEFORE ASKING FOR A SOLUTION
* **DON'T**: `Change timeout to 30s.`
* **DO**: `We are seeing HTTP 504 timeouts during PDF generation in report_service.py. Increase the client timeout to 30s and add exponential backoff retry logic.`
* **Why**: Providing root-cause context enables the agent to select an appropriate architectural solution rather than applying a superficial patch.

### 9. Direct Tool & Search Strategy
* **Headline**: DIRECT THE AGENT'S TOOL CHOICE WHEN NECESSARY
* **DON'T**: `Find where permissions are checked.`
* **DO**: `Use code_search to locate 'has_permission()' across the repository, then inspect the call sites in auth/ middleware.`
* **Why**: Steering tool choice prevents wasteful searches or inefficient directory traversals.

---
*Note: To add or update rules, simply edit this markdown file directly.*

