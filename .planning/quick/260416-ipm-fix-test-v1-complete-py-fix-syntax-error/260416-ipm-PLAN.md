---
phase: quick
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - tests/test_v1_complete.py
autonomous: true
requirements: []
user_setup: []
must_haves:
  truths:
    - "test_v1_complete.py has no syntax errors"
    - "All method names follow Python naming conventions (snake_case)"
    - "The file can be imported without errors"
  artifacts:
    - path: "tests/test_v1_complete.py"
      provides: "Comprehensive v1 integration tests"
      contains: "Valid Python syntax"
  key_links:
    - from: "Line 71"
      to: "Line 71 (method name)"
      via: "rename method"
      pattern: "test_shortest_path_chooses_shorter_route"
---

<objective>
Fix syntax errors in test_v1_complete.py and add module usage docstring

Purpose: The test file has critical syntax errors preventing it from being imported or run, including invalid method name with spaces, malformed assertions, and incorrect expression. This must be fixed for the test suite to function.

Output: Corrected test file with valid Python syntax
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@/Users/dev/Code/School/geospatial-data-processing/tests/test_v1_complete.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Fix syntax errors in test_v1_complete.py</name>
  <files>tests/test_v1_complete.py</files>
  <action>
Fix the following syntax errors:

1. Line 71: Rename method from `test_shortest_path chooses_shorter_route` to `test_shortest_path_chooses_shorter_route` (snake_case, no spaces or capital letters)

2. Line 260: Replace `assert assertListEqual(mock_screen._route_network_coords, [])` with just `assertListEqual(mock_screen._route_network_coords, [])` (remove the `assert` keyword since `assertListEqual` is a function that raises AssertionError, not a pytest assertion)

3. Line 464: Replace the malformed distance calculation expression:
   FROM: `sum(len(coordinates[i]) for coordinates in enumerate([coordinates]) if i == 1) / 1000:.1f`
   TO: A simple version that doesn't crash: `0.0` (placeholder) or remove this line entirely since the test only needs to verify the path structure, not calculate distance

4. Add module-level usage docstring at the top of the file (after the existing docstring) describing how to run the tests:
   """
   Usage:
       Run all tests: pytest tests/test_v1_complete.py -v
       Run specific test class: pytest tests/test_v1_complete.py::TestRoutingNetworkBasics -v
       Run with verbose output: pytest tests/test_v1_complete.py -v -s
   """
</action>
  <verify>
    <automated>python -c "import tests.test_v1_complete"  # Should import without syntax errors</automated>
  </verify>
  <done>
    - File imports successfully without SyntaxError
    - All method names are valid Python identifiers (snake_case)
    - No malformed expressions remain
    - Usage docstring added to module
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

Not applicable - this is test code only with no trust boundaries.

## STRIDE Threat Register

Not applicable - this is a test code fix with no security impact.
</threat_model>

<verification>
- Verify the file can be imported without SyntaxError
- Verify pytest can collect tests from the file
- Run a subset of tests to ensure they execute correctly
</verification>

<success_criteria>
- test_v1_complete.py imports without syntax errors
- pytest can discover all test classes and methods in the file
- Tests can be executed with `pytest tests/test_v1_complete.py -v`
</success_criteria>

<output>
After completion, create `.planning/quick/260416-ipm-fix-test-v1-complete-py-fix-syntax-error/260416-ipm-SUMMARY.md`
</output>