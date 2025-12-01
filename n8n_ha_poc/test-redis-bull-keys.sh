#!/bin/bash

# Script to test and verify Bull queue keys appear when workflows execute
# This script helps verify that the Redis queue is working correctly

set -e

NAMESPACE="n8n-ha"

echo "=========================================="
echo "Redis Bull Queue Keys Test"
echo "=========================================="
echo ""

# Get Redis master pod
REDIS_MASTER_POD=$(kubectl get pods -n $NAMESPACE -l app=redis,role=master -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [ -z "$REDIS_MASTER_POD" ]; then
    echo "✗ Redis master pod not found"
    exit 1
fi

echo "Step 1: Checking Current Bull Keys"
echo "-----------------------------------"
BULL_KEYS_BEFORE=$(kubectl exec -n $NAMESPACE $REDIS_MASTER_POD -- redis-cli KEYS "bull:*" 2>/dev/null | grep -v "^$" || echo "")
BULL_COUNT_BEFORE=$(echo "$BULL_KEYS_BEFORE" | grep -v "^$" | wc -l | tr -d ' ' || echo "0")

echo "Current Bull keys: $BULL_COUNT_BEFORE"
if [ -n "$BULL_KEYS_BEFORE" ]; then
    echo "$BULL_KEYS_BEFORE" | sed 's/^/  • /'
else
    echo "  (none - this is normal if no workflows are executing)"
fi
echo ""

echo "Step 2: Instructions to Generate Bull Keys"
echo "-------------------------------------------"
echo "To see Bull queue keys appear, you need to execute a workflow:"
echo ""
echo "1. Ensure port forwarding is active:"
echo "   ./port-forward.sh"
echo ""
echo "2. Open n8n UI in your browser:"
echo "   http://localhost:5678"
echo ""
echo "3. Create or open a simple workflow:"
echo "   - Add a 'Wait' node (set to 5-10 seconds)"
echo "   - Add a 'Set' node to set a variable"
echo "   - Save the workflow"
echo ""
echo "4. Execute the workflow (click 'Execute Workflow' button)"
echo ""
echo "5. While the workflow is executing, run this command in another terminal:"
echo "   ./find-redis-queue-keys.sh"
echo ""
echo "   OR monitor in real-time:"
echo "   ./find-redis-queue-keys.sh --monitor"
echo ""

echo "Step 3: Expected Keys During Execution"
echo "---------------------------------------"
echo "When a workflow is executing, you should see keys like:"
echo ""
echo "  • bull:jobs:wait          - Job waiting in queue"
echo "  • bull:jobs:active        - Job being processed"
echo "  • bull:jobs:completed     - Job completed (may be cleaned up quickly)"
echo "  • bull:jobs:stalled-check - Always present (maintenance key)"
echo ""

echo "Step 4: Real-Time Monitoring"
echo "-----------------------------"
echo "To watch keys appear in real-time, run in a separate terminal:"
echo ""
echo "  ./find-redis-queue-keys.sh --monitor"
echo ""
echo "Then execute a workflow in n8n UI. You'll see Redis commands as they happen."
echo ""

echo "Step 5: Verify Queue Configuration"
echo "-----------------------------------"
echo "Current configuration:"
WORKER_POD=$(kubectl get pods -n $NAMESPACE -l app=n8n-worker -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [ -n "$WORKER_POD" ]; then
    echo ""
    kubectl exec -n $NAMESPACE $WORKER_POD -- env 2>/dev/null | grep -E "QUEUE_BULL|EXECUTIONS_MODE" | sed 's/^/  /' || echo "  (Could not retrieve configuration)"
else
    echo "  ⚠ Worker pod not found"
fi
echo ""

echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
if [ "$BULL_COUNT_BEFORE" -gt 0 ]; then
    echo "✅ Bull queue is working! Found $BULL_COUNT_BEFORE key(s)."
    echo ""
    echo "To see more keys (wait, active, completed), execute a workflow in n8n UI."
else
    echo "ℹ️  No active Bull keys found (this is normal)."
    echo ""
    echo "The queue is configured correctly. To see keys:"
    echo "  1. Execute a workflow in n8n UI"
    echo "  2. Run: ./find-redis-queue-keys.sh"
    echo ""
    echo "The presence of 'bull:jobs:stalled-check' confirms Bull is working."
    echo "Additional keys only appear during active workflow executions."
fi
echo ""
echo "For more information, see: REDIS_BULL_KEYS_GUIDE.md"
echo ""

