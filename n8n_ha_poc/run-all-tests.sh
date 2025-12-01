#!/bin/bash

# Run all HA tests in sequence
# Make sure Grafana is accessible to monitor the tests

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAMESPACE="n8n-ha"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
declare -A TEST_RESULTS
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Parse command line arguments
INTERACTIVE=true
SKIP_PREREQS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --non-interactive|-n)
            INTERACTIVE=false
            shift
            ;;
        --skip-prereqs|-s)
            SKIP_PREREQS=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --non-interactive, -n    Run without prompts"
            echo "  --skip-prereqs, -s       Skip prerequisite checks"
            echo "  --help, -h               Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to print colored output
print_info() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    if [ "$SKIP_PREREQS" = true ]; then
        print_warning "⚠ Skipping prerequisite checks"
        return 0
    fi
    
    print_info "Checking prerequisites..."
    echo ""
    
    local all_ok=true
    
    # Check if namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        print_error "✗ Namespace '$NAMESPACE' not found"
        print_info "  Run: ./deploy.sh"
        all_ok=false
    else
        print_success "✓ Namespace '$NAMESPACE' exists"
    fi
    
    # Check if pods are running
    local pod_count=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -c Running || echo "0")
    if [ "$pod_count" -eq 0 ]; then
        print_error "✗ No pods running in namespace '$NAMESPACE'"
        print_info "  Run: ./deploy.sh"
        all_ok=false
    else
        print_success "✓ Found $pod_count running pod(s)"
    fi
    
    # Check port forwarding (optional but recommended)
    if lsof -Pi :5678 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_success "✓ Port forwarding active (port 5678)"
    else
        print_warning "⚠ Port forwarding not active (port 5678)"
        print_info "  Some tests may be skipped. Run in another terminal: ./port-forward.sh"
    fi
    
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_success "✓ Grafana port forwarding active (port 3000)"
    else
        print_warning "⚠ Grafana port forwarding not active (port 3000)"
        print_info "  Grafana monitoring will not be available. Run: ./port-forward.sh"
    fi
    
    echo ""
    
    if [ "$all_ok" = false ]; then
        print_error "Prerequisites not met. Please fix the issues above and try again."
        exit 1
    fi
    
    print_success "✓ All prerequisites met"
    echo ""
}

# Function to check if test script exists
check_test_script() {
    local script=$1
    if [ ! -f "$SCRIPT_DIR/$script" ]; then
        print_error "✗ Test script not found: $script"
        return 1
    fi
    if [ ! -x "$SCRIPT_DIR/$script" ]; then
        print_warning "⚠ Test script not executable: $script"
        chmod +x "$SCRIPT_DIR/$script"
        print_info "  Made script executable"
    fi
    return 0
}

# Function to run a test
run_test() {
    local test_name=$1
    local test_script=$2
    local test_number=$3
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo ""
    echo "=========================================="
    echo "TEST $test_number: $test_name"
    echo "=========================================="
    echo ""
    
    if ! check_test_script "$test_script"; then
        TEST_RESULTS["$test_name"]="SKIPPED"
        print_warning "⚠ Test skipped: $test_name (script not found)"
        return 1
    fi
    
    # Run the test and capture exit code
    if "$SCRIPT_DIR/$test_script"; then
        TEST_RESULTS["$test_name"]="PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        print_success "✓ Test PASSED: $test_name"
        return 0
    else
        TEST_RESULTS["$test_name"]="FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        print_error "✗ Test FAILED: $test_name"
        return 1
    fi
}

# Function to wait for user input (if interactive)
wait_for_user() {
    if [ "$INTERACTIVE" = true ]; then
        echo ""
        read -p "Press Enter to continue to next test (or Ctrl+C to cancel)..."
        echo ""
    else
        echo ""
        print_info "Waiting 5 seconds before next test..."
        sleep 5
        echo ""
    fi
}

# Main execution
echo "=========================================="
echo "n8n HA Test Suite"
echo "=========================================="
echo ""
echo "This will run all HA tests in sequence."
echo "Make sure Grafana is accessible to monitor the tests."
echo ""

if [ "$INTERACTIVE" = true ]; then
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""
fi

# Check prerequisites
check_prerequisites

# Wait a bit for services to stabilize
if [ "$INTERACTIVE" = false ]; then
    print_info "Waiting 5 seconds for services to stabilize..."
    sleep 5
    echo ""
fi

# Test 1: Editor HA
run_test "n8n Editor HA" "test-editor-ha.sh" "1"
wait_for_user

# Wait a bit between tests
if [ "$INTERACTIVE" = false ]; then
sleep 10
fi

# Test 2: PostgreSQL HA
run_test "PostgreSQL HA" "test-postgres-ha.sh" "2"
wait_for_user

# Wait a bit between tests
if [ "$INTERACTIVE" = false ]; then
sleep 10
fi

# Test 3: n8n Worker HA
run_test "n8n Worker HA" "test-worker-ha.sh" "3"
wait_for_user

# Wait a bit between tests
if [ "$INTERACTIVE" = false ]; then
    sleep 10
fi

# Test 4: Redis HA
run_test "Redis HA" "test-redis-ha.sh" "4"

# Final summary
echo ""
echo "=========================================="
echo "Test Suite Summary"
echo "=========================================="
echo ""

for test_name in "${!TEST_RESULTS[@]}"; do
    local result="${TEST_RESULTS[$test_name]}"
    case "$result" in
        PASSED)
            print_success "✓ $test_name: PASSED"
            ;;
        FAILED)
            print_error "✗ $test_name: FAILED"
            ;;
        SKIPPED)
            print_warning "⚠ $test_name: SKIPPED"
            ;;
    esac
done

echo ""
echo "=========================================="
echo "Overall Results"
echo "=========================================="
echo ""
echo "Total Tests: $TOTAL_TESTS"
print_success "Passed: $PASSED_TESTS"
print_error "Failed: $FAILED_TESTS"
SKIPPED_COUNT=$((TOTAL_TESTS - PASSED_TESTS - FAILED_TESTS))
if [ "$SKIPPED_COUNT" -gt 0 ]; then
    print_warning "Skipped: $SKIPPED_COUNT"
fi
echo ""

if [ "$FAILED_TESTS" -eq 0 ] && [ "$PASSED_TESTS" -eq "$TOTAL_TESTS" ]; then
    print_success "🎉 All tests PASSED!"
    EXIT_CODE=0
elif [ "$FAILED_TESTS" -gt 0 ]; then
    print_error "❌ Some tests FAILED"
    EXIT_CODE=1
else
    print_warning "⚠ Some tests were SKIPPED"
    EXIT_CODE=0
fi

echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "Check Grafana dashboard for detailed metrics:"
echo "  http://localhost:3000 (admin/admin123)"
echo ""
echo "View test logs for more details:"
echo "  - Each test script outputs detailed information"
echo "  - Check pod logs: kubectl logs -n $NAMESPACE <pod-name>"
echo ""
echo "Troubleshooting:"
echo "  - If tests failed, check prerequisites: ./deploy.sh"
echo "  - Ensure port forwarding is active: ./port-forward.sh"
echo "  - Check pod status: kubectl get pods -n $NAMESPACE"
echo ""

exit $EXIT_CODE
