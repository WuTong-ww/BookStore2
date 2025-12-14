#!/bin/sh
# Run tests with coverage and save full output and errors to logs.
# Works in Git Bash on Windows.

set -o pipefail

# Clean previous logs and ensure logs directory exists
# if [ -d logs ]; then
#   rm -f logs/*.log logs/*.xml 2>/dev/null || true
# fi
mkdir -p logs

# Timestamped filenames
TS=$(date +%Y%m%d_%H%M%S)
FULL_LOG="logs/pytest_${TS}.log"
ERR_LOG="logs/pytest_errors_${TS}.log"
JUNIT_XML="logs/junit_${TS}.xml"

# Clean Python cache and ensure fresh imports
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Clear any existing Python modules from memory and set clean path
unset PYTHONPATH
export PYTHONPATH="$(pwd)"
export PYTHONDONTWRITEBYTECODE=1

# Run coverage + pytest. Collect all failures, verbose traceback, and junit xml.
# Note: --maxfail=0 means do not stop on failures.
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest \
  -vv -ra --maxfail=0 --disable-warnings --color=no --tb=long \
  --junitxml="${JUNIT_XML}" 2>&1 | tee "${FULL_LOG}"
STATUS=${PIPESTATUS[0]}

# Produce human-readable coverage table and HTML report
coverage report -m | tee "logs/coverage_${TS}.log" || true
coverage html || true

# Extract an errors-only summary from the full log
# Capture blocks starting from FAILURES/ERRORS headings and short summary lines
{
  echo "==== Extracted FAILURES/ERRORS/SUMMARY from ${FULL_LOG} ===="
  echo
  awk '/^=+ FAILURES =+/{flag=1} flag{print} /^=+ .* in .* =+/{if(flag){exit}}' "${FULL_LOG}" || true
  echo
  awk '/^=+ ERRORS =+/{flag=1} flag{print} /^=+ .* in .* =+/{if(flag){exit}}' "${FULL_LOG}" || true
  echo
  grep -nE "^=+ short test summary info =+|^FAILED|^ERROR|^E +|^\s*\d+ failed|^\s*\d+ errors" "${FULL_LOG}" || true
} > "${ERR_LOG}"

# Final pointers
echo "\nFull pytest output: ${FULL_LOG}"
echo "Errors-only summary: ${ERR_LOG}"
echo "JUnit XML: ${JUNIT_XML}"
echo "Coverage summary: logs/coverage_${TS}.log"
echo "HTML coverage: htmlcov/index.html"

exit ${STATUS}
