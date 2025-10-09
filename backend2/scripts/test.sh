#!/bin/bash
# Test runner script
set -euo pipefail

echo "🧪 Running SeatDuty Backend Tests..."

# Load development environment variables
if [ -f "env.development" ]; then
    export $(cat env.development | grep -v '^#' | xargs)
fi

REPORT_DIR=${REPORT_DIR:-tests}
REPORT_FILE=${REPORT_FILE:-$REPORT_DIR/summary.txt}
mkdir -p "$REPORT_DIR"

# Run tests in compose 'test' service and capture output
echo "Running pytest tests..."
set +e
docker compose -f docker-compose.test.yaml run --rm test | tee "$REPORT_FILE"
EXIT_CODE=${PIPESTATUS[0]}
set -e

echo "Summary written to $REPORT_FILE"
echo "✅ Tests completed!"
exit $EXIT_CODE
