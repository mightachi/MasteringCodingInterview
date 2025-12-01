#!/bin/bash

# Script to create and execute a test workflow that generates Bull queue keys
# This workflow includes a Wait node to ensure keys appear (wait, active, completed)

set -e

NAMESPACE="n8n-ha"
N8N_URL="http://localhost:5678"
N8N_USER="sukh.shukla@tiket.com"
N8N_PASS="Admin123"
WORKFLOW_NAME="Queue Test Workflow - $(date +%Y%m%d-%H%M%S)"

echo "=========================================="
echo "Create Test Workflow for Queue Testing"
echo "=========================================="
echo ""

# Function to get authentication cookie
get_auth_cookie() {
    rm -f /tmp/n8n_queue_test_cookies.txt
    local login_response=$(curl -s -c /tmp/n8n_queue_test_cookies.txt -X POST \
        "${N8N_URL}/rest/login" \
        -H "Content-Type: application/json" \
        -d "{\"emailOrLdapLoginId\":\"${N8N_USER}\",\"password\":\"${N8N_PASS}\"}" 2>/dev/null)
    
    if echo "$login_response" | grep -q "\"data\"" || echo "$login_response" | grep -q "\"id\""; then
        # Verify cookie works
        local test_response=$(curl -s -b /tmp/n8n_queue_test_cookies.txt "${N8N_URL}/rest/workflows" 2>/dev/null)
        if [ -n "$test_response" ] && (echo "$test_response" | grep -q "\"data\"" || echo "$test_response" | grep -q "\"count\""); then
            return 0
        fi
    fi
    return 1
}

# Check port forwarding
echo "Step 1: Checking Port Forwarding"
echo "--------------------------------"
if ! lsof -Pi :5678 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✗ Port 5678 is not listening"
    echo ""
    echo "Please start port forwarding first:"
    echo "  ./port-forward.sh"
    echo ""
    echo "Or manually:"
    echo "  kubectl port-forward -n $NAMESPACE svc/n8n-editor 5678:5678"
    exit 1
fi
echo "✓ Port forwarding is active"
echo ""

# Check API accessibility
echo "Step 2: Checking n8n API Accessibility"
echo "----------------------------------------"
if ! curl -s -f --connect-timeout 5 "${N8N_URL}/healthz" > /dev/null 2>&1; then
    echo "✗ n8n health endpoint not accessible"
    echo "  Please ensure n8n is running and port forwarding is active"
    exit 1
fi
echo "✓ n8n health endpoint is accessible"
echo ""

# Authenticate
echo "Step 3: Authenticating"
echo "----------------------"
if ! get_auth_cookie; then
    echo "✗ Authentication failed"
    echo "  Please check N8N_USER and N8N_PASS in the script"
    exit 1
fi
echo "✓ Authentication successful"
echo ""

# Create workflow with Wait node (to ensure execution takes time)
echo "Step 4: Creating Test Workflow"
echo "------------------------------"
echo "Workflow name: ${WORKFLOW_NAME}"
echo ""

# Create a workflow with:
# 1. Start node (manual trigger)
# 2. Wait node (5 seconds - ensures job stays in queue/active state)
# 3. Set node (to set a variable)
WORKFLOW_JSON=$(cat <<EOF
{
  "name": "${WORKFLOW_NAME}",
  "nodes": [
    {
      "parameters": {},
      "id": "start-node",
      "name": "Start",
      "type": "n8n-nodes-base.start",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "amount": 5,
        "unit": "seconds"
      },
      "id": "wait-node",
      "name": "Wait",
      "type": "n8n-nodes-base.wait",
      "typeVersion": 1,
      "position": [450, 300]
    },
    {
      "parameters": {
        "values": {
          "string": [
            {
              "name": "test_message",
              "value": "Queue test workflow executed at $(date +%Y-%m-%d\ %H:%M:%S)"
            }
          ]
        }
      },
      "id": "set-node",
      "name": "Set",
      "type": "n8n-nodes-base.set",
      "typeVersion": 1,
      "position": [650, 300]
    }
  ],
  "connections": {
    "Start": {
      "main": [[{"node": "Wait", "type": "main", "index": 0}]]
    },
    "Wait": {
      "main": [[{"node": "Set", "type": "main", "index": 0}]]
    }
  },
  "active": false,
  "settings": {}
}
EOF
)

CREATE_RESPONSE=$(curl -s -b /tmp/n8n_queue_test_cookies.txt -X POST \
    "${N8N_URL}/rest/workflows" \
    -H "Content-Type: application/json" \
    -d "${WORKFLOW_JSON}" 2>/dev/null)

# Extract workflow ID
WORKFLOW_ID=$(echo "$CREATE_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'data' in data and 'id' in data['data']:
        print(data['data']['id'])
    elif 'id' in data:
        print(data['id'])
    else:
        print('')
except:
    print('')
" 2>/dev/null || echo "")

if [ -z "$WORKFLOW_ID" ] || [ "$WORKFLOW_ID" = "null" ]; then
    echo "✗ Failed to create workflow"
    echo "  Response: $(echo "$CREATE_RESPONSE" | head -c 300)"
    exit 1
fi

echo "✓ Workflow created successfully"
echo "  Workflow ID: $WORKFLOW_ID"
echo ""

# Execute workflow
echo "Step 5: Executing Workflow"
echo "---------------------------"
echo "Triggering workflow execution..."
echo ""

EXECUTE_RESPONSE=$(curl -s -b /tmp/n8n_queue_test_cookies.txt -X POST \
    "${N8N_URL}/rest/workflows/${WORKFLOW_ID}/execute" \
    -H "Content-Type: application/json" \
    -d "{}" 2>/dev/null)

# Extract execution ID
EXECUTION_ID=$(echo "$EXECUTE_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Try different possible paths
    if 'executionId' in data:
        print(data['executionId'])
    elif 'data' in data and 'executionId' in data['data']:
        print(data['data']['executionId'])
    elif 'id' in data:
        print(data['id'])
    elif 'data' in data and 'id' in data['data']:
        print(data['data']['id'])
    else:
        print('')
except:
    print('')
" 2>/dev/null || echo "")

if [ -z "$EXECUTION_ID" ] || [ "$EXECUTION_ID" = "null" ]; then
    # Check if execution was queued (which is OK for queue mode)
    if echo "$EXECUTE_RESPONSE" | grep -qi "queued\|queue\|execution"; then
        echo "✓ Workflow execution queued (this is expected in queue mode)"
        echo "  Response: $(echo "$EXECUTE_RESPONSE" | head -c 200)"
        EXECUTION_ID="queued"
    else
        echo "⚠ Could not extract execution ID"
        echo "  Response: $(echo "$EXECUTE_RESPONSE" | head -c 300)"
        EXECUTION_ID=""
    fi
else
    echo "✓ Workflow execution started"
    echo "  Execution ID: $EXECUTION_ID"
fi
echo ""

# Monitor Bull keys
echo "Step 6: Monitoring Bull Queue Keys"
echo "----------------------------------"
echo "Checking for Bull keys in Redis..."
echo ""

REDIS_MASTER_POD=$(kubectl get pods -n $NAMESPACE -l app=redis,role=master -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [ -z "$REDIS_MASTER_POD" ]; then
    echo "⚠ Redis master pod not found, skipping key monitoring"
else
    echo "Monitoring keys for 10 seconds..."
    echo ""
    
    # Check keys multiple times during execution
    for i in {1..5}; do
        echo "Check $i/5 (at $(date +%H:%M:%S)):"
        BULL_KEYS=$(kubectl exec -n $NAMESPACE $REDIS_MASTER_POD -- redis-cli KEYS "bull:*" 2>/dev/null | grep -v "^$" || echo "")
        
        if [ -n "$BULL_KEYS" ]; then
            KEY_COUNT=$(echo "$BULL_KEYS" | grep -v "^$" | wc -l | tr -d ' ')
            echo "  Found $KEY_COUNT Bull key(s):"
            echo "$BULL_KEYS" | while read key; do
                if [ -n "$key" ]; then
                    # Get key type and TTL
                    KEY_TYPE=$(kubectl exec -n $NAMESPACE $REDIS_MASTER_POD -- redis-cli TYPE "$key" 2>/dev/null | tr -d '\r\n' || echo "unknown")
                    TTL=$(kubectl exec -n $NAMESPACE $REDIS_MASTER_POD -- redis-cli TTL "$key" 2>/dev/null | tr -d '\r\n' || echo "-1")
                    
                    if [ "$TTL" = "-1" ]; then
                        TTL_STR="no expiration"
                    elif [ "$TTL" = "-2" ]; then
                        TTL_STR="expired"
                    else
                        TTL_STR="${TTL}s"
                    fi
                    
                    echo "    • $key (type: $KEY_TYPE, TTL: $TTL_STR)"
                fi
            done
            
            # Check for specific key types
            if echo "$BULL_KEYS" | grep -q "bull:jobs:wait"; then
                echo "  ✓ Found 'wait' key - job is queued"
            fi
            if echo "$BULL_KEYS" | grep -q "bull:jobs:active"; then
                echo "  ✓ Found 'active' key - job is being processed"
            fi
            if echo "$BULL_KEYS" | grep -q "bull:jobs:completed"; then
                echo "  ✓ Found 'completed' key - job completed"
            fi
        else
            echo "  No Bull keys found (workflow may have completed)"
        fi
        echo ""
        
        if [ $i -lt 5 ]; then
            sleep 2
        fi
    done
fi
echo ""

# Summary
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
echo "Workflow Details:"
echo "  Name: ${WORKFLOW_NAME}"
echo "  ID: ${WORKFLOW_ID}"
if [ -n "$EXECUTION_ID" ] && [ "$EXECUTION_ID" != "queued" ]; then
    echo "  Execution ID: ${EXECUTION_ID}"
fi
echo ""
echo "Next Steps:"
echo "  1. View workflow in n8n UI: ${N8N_URL}"
echo "  2. Check execution status in n8n UI"
echo "  3. Monitor Bull keys: ./find-redis-queue-keys.sh --monitor"
echo "  4. Check worker logs: kubectl logs -n $NAMESPACE -l app=n8n-worker --tail=50"
echo ""
echo "To clean up this test workflow:"
echo "  curl -s -b /tmp/n8n_queue_test_cookies.txt -X DELETE \"${N8N_URL}/rest/workflows/${WORKFLOW_ID}\""
echo ""

# Clean up cookies
rm -f /tmp/n8n_queue_test_cookies.txt

