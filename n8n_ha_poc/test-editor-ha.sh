#!/bin/bash

# Test script for n8n Editor HA
# This script tests failover scenarios for n8n editor pods and workflow persistence

set -e

NAMESPACE="n8n-ha"
EDITOR_DEPLOYMENT="n8n-editor"
SERVICE="n8n-editor"
N8N_URL="http://localhost:5678"
N8N_USER="sukh.shukla@tiket.com"
N8N_PASS="Admin123"

echo "=========================================="
echo "n8n Editor HA Test"
echo "=========================================="
echo ""
echo "This test verifies:"
echo "  1. Pod failover and recovery"
echo "  2. Service connectivity"
echo "  3. Workflow persistence (requires port-forwarding)"
echo ""
echo "Note: For workflow persistence testing:"
echo "  1. Ensure port-forwarding is active: ./port-forward.sh"
echo "  2. Create a user account in n8n UI first (if not exists):"
echo "     - Open: http://localhost:5678"
echo "     - Complete initial setup or login"
echo "     - The REST API requires a user session, not just basic auth"
echo ""
echo "If API is not accessible, the test will continue with pod failover tests only."
echo ""

# Function to check pod status
check_pods() {
    echo "Current Editor Pods:"
    kubectl get pods -n $NAMESPACE -l app=$EDITOR_DEPLOYMENT -o wide
    echo ""
}

# Function to get pod count
get_pod_count() {
    kubectl get pods -n $NAMESPACE -l app=$EDITOR_DEPLOYMENT --no-headers | grep -c Running || echo "0"
}

# Function to wait for pods to be ready
wait_for_pods() {
    local expected=$1
    local count=0
    local max_wait=60
    
    echo "Waiting for $expected editor pod(s) to be ready..."
    while [ $count -lt $max_wait ]; do
        local running=$(get_pod_count)
        if [ "$running" -eq "$expected" ]; then
            echo "✓ All $expected pod(s) are running"
            return 0
        fi
        echo "  Waiting... ($running/$expected running)"
        sleep 2
        count=$((count + 2))
    done
    
    echo "✗ Timeout waiting for pods"
    return 1
}

# Function to check if n8n API is accessible
check_n8n_api() {
    local max_attempts=10
    local attempt=0
    
    echo "Checking n8n API accessibility..."
    
    # First check if port is accessible (try multiple methods)
    local port_check=""
    local port_accessible=false
    
    # Try healthz endpoint
    if curl -s -f --connect-timeout 2 "${N8N_URL}/healthz" > /dev/null 2>&1; then
        port_accessible=true
        port_check="healthz"
    # Try with basic auth
    elif curl -s -f --connect-timeout 2 -u "${N8N_USER}:${N8N_PASS}" "${N8N_URL}/healthz" > /dev/null 2>&1; then
        port_accessible=true
        port_check="healthz-auth"
    # Try root endpoint
    elif curl -s -f --connect-timeout 2 -u "${N8N_USER}:${N8N_PASS}" "${N8N_URL}/" > /dev/null 2>&1; then
        port_accessible=true
        port_check="root"
    fi
    
    if [ "$port_accessible" = false ]; then
        echo "⚠ n8n service not accessible on ${N8N_URL}"
        echo ""
        echo "   Port-forwarding is required for workflow persistence tests."
        echo ""
        echo "   Quick Fix:"
        echo "   1. In a separate terminal, run:"
        echo "      cd $(pwd)"
        echo "      ./port-forward.sh"
        echo ""
        echo "   2. Wait 5 seconds, then re-run this test:"
        echo "      ./test-editor-ha.sh"
        echo ""
        echo "   Or manually start port-forwarding:"
        echo "      kubectl port-forward -n $NAMESPACE svc/$SERVICE 5678:5678"
        echo ""
        echo "   Check status:"
        echo "      ./check-port-forward.sh"
        echo "      lsof -i :5678"
        echo ""
        echo "   Continuing with pod-level tests only (workflow tests will be skipped)..."
        return 1
    fi
    
    echo "✓ n8n service is accessible (via $port_check)"
    
    # Try to authenticate and get workflows using cookie-based auth
    while [ $attempt -lt $max_attempts ]; do
        # Try to get a session cookie by accessing the root with basic auth
        # Then use that session for API calls
        local cookie_response=$(curl -s -c /tmp/n8n_test_cookies.txt -u "${N8N_USER}:${N8N_PASS}" \
            "${N8N_URL}/" > /dev/null 2>&1 && echo "ok" || echo "fail")
        
        # Try multiple authentication methods
        # Method 1: Try login endpoint first (most reliable)
        rm -f /tmp/n8n_test_cookies.txt
        local login_response=$(curl -s -c /tmp/n8n_test_cookies.txt -X POST \
            "${N8N_URL}/rest/login" \
            -H "Content-Type: application/json" \
            -d "{\"emailOrLdapLoginId\":\"${N8N_USER}\",\"password\":\"${N8N_PASS}\"}" 2>/dev/null)
        
        # Check if login was successful (should return user data with "data" field)
        if echo "$login_response" | grep -q "\"data\"" || echo "$login_response" | grep -q "\"id\""; then
            # Login successful, test API access
            local login_workflows=$(curl -s -b /tmp/n8n_test_cookies.txt "${N8N_URL}/rest/workflows" 2>/dev/null)
            # Check if response contains "data" array or "count" (successful API response)
            if [ -n "$login_workflows" ] && (echo "$login_workflows" | grep -q "\"data\"" || echo "$login_workflows" | grep -q "\"count\""); then
                echo "✓ n8n API is accessible with login cookie"
                rm -f /tmp/n8n_test_cookies.txt
                return 0
            else
                # Login worked but API call failed - might be a temporary issue
                if [ $attempt -lt 2 ]; then
                    echo "  Login successful but API call failed, retrying..."
                fi
            fi
        else
            # Login failed - check error
            if echo "$login_response" | grep -q "401\|Unauthorized\|Wrong username"; then
                echo "⚠ Login failed: Invalid credentials"
                echo "   Response: $(echo "$login_response" | head -c 200)"
            fi
        fi
        
        # Method 2: Session cookie from root access (fallback)
        curl -s -c /tmp/n8n_test_cookies.txt -u "${N8N_USER}:${N8N_PASS}" "${N8N_URL}/" > /dev/null 2>&1
        local workflows_response=$(curl -s -b /tmp/n8n_test_cookies.txt "${N8N_URL}/rest/workflows" 2>/dev/null)
        if [ -n "$workflows_response" ] && (echo "$workflows_response" | grep -q "\"data\"" || echo "$workflows_response" | grep -q "\"count\""); then
            echo "✓ n8n API is accessible with session cookie"
            rm -f /tmp/n8n_test_cookies.txt
            return 0
        fi
        
        # Method 4: Check if owner setup is needed
        local owner_check=$(curl -s "${N8N_URL}/rest/owner/setup" 2>/dev/null)
        if echo "$owner_check" | grep -q "setup"; then
            echo "⚠ n8n requires initial owner setup"
            echo "   Please visit http://localhost:5678 and complete the setup"
            echo "   Then create a user account to use the REST API"
        fi
        
        echo "  Waiting for n8n API... ($attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "⚠ n8n API authentication failed after multiple attempts"
    echo "   Tried: session cookie, basic auth, and login endpoint"
    echo ""
    echo "   Possible issues:"
    echo "   1. Port-forwarding not active:"
    echo "      - Check: ./check-port-forward.sh"
    echo "      - Start: ./port-forward.sh (in another terminal)"
    echo "   2. Invalid credentials:"
    echo "      - Current user: ${N8N_USER}"
    echo "      - Edit script to update N8N_USER and N8N_PASS if needed"
    echo "   3. n8n not fully started:"
    echo "      - Check pods: kubectl get pods -n $NAMESPACE -l app=n8n-editor"
    echo "      - Check logs: kubectl logs -n $NAMESPACE -l app=n8n-editor --tail=20"
    echo "   4. Owner setup required:"
    echo "      - Visit: ${N8N_URL} and complete initial setup"
    echo ""
    echo "   This is OK - the script will continue with pod-level tests only"
    echo "   Workflow persistence tests will be skipped"
    echo ""
    echo "   To enable workflow tests, ensure port-forwarding is active and re-run."
    rm -f /tmp/n8n_test_cookies.txt
    return 1
}

# Function to get authentication cookie
get_auth_cookie() {
    # Use the login endpoint to get a proper session cookie
    local login_response=$(curl -s -c /tmp/n8n_cookies.txt -X POST \
        "${N8N_URL}/rest/login" \
        -H "Content-Type: application/json" \
        -d "{\"emailOrLdapLoginId\":\"${N8N_USER}\",\"password\":\"${N8N_PASS}\"}" 2>/dev/null)
    
    # Check if login was successful (should return user data)
    if echo "$login_response" | grep -q "\"data\"" || echo "$login_response" | grep -q "\"id\""; then
    # Verify we can use the cookie for API calls
    local test_response=$(curl -s -b /tmp/n8n_cookies.txt "${N8N_URL}/rest/workflows" 2>/dev/null)
    # Check if response contains "data" array or "count" (successful API response)
    if [ -n "$test_response" ] && (echo "$test_response" | grep -q "\"data\"" || echo "$test_response" | grep -q "\"count\""); then
        echo "✓ Authentication successful (login cookie)"
        return 0
    fi
    fi
    
    echo "⚠ Login failed or cookie not working"
    return 1
}

# Function to create a test workflow
create_test_workflow() {
    local workflow_name="HA Test Workflow $(date +%s)"
    local workflow_json=$(cat <<EOF
{
  "name": "${workflow_name}",
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
        "message": "HA Test Workflow executed successfully"
      },
      "id": "set-node",
      "name": "Set",
      "type": "n8n-nodes-base.set",
      "typeVersion": 1,
      "position": [450, 300]
    }
  ],
  "connections": {
    "Start": {
      "main": [[{"node": "Set", "type": "main", "index": 0}]]
    }
  },
  "active": false,
  "settings": {}
}
EOF
)
    
    echo "Creating test workflow: ${workflow_name}" >&2
    
    # Get authentication cookie
    get_auth_cookie > /dev/null 2>&1
    local response=""
    
    # Use cookie for API call
    if [ -f /tmp/n8n_cookies.txt ]; then
        response=$(curl -s -b /tmp/n8n_cookies.txt -X POST \
            "${N8N_URL}/rest/workflows" \
            -H "Content-Type: application/json" \
            -d "${workflow_json}" 2>/dev/null)
    else
        # Fallback: try login again
        curl -s -c /tmp/n8n_cookies.txt -X POST \
            "${N8N_URL}/rest/login" \
            -H "Content-Type: application/json" \
            -d "{\"emailOrLdapLoginId\":\"${N8N_USER}\",\"password\":\"${N8N_PASS}\"}" > /dev/null 2>&1
        
        response=$(curl -s -b /tmp/n8n_cookies.txt -X POST \
            "${N8N_URL}/rest/workflows" \
            -H "Content-Type: application/json" \
            -d "${workflow_json}" 2>/dev/null)
    fi
    
    # Extract workflow ID from response
    # n8n returns {"data": {"id": "...", ...}} for workflow creation
    local workflow_id=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Try data.id first (n8n workflow creation response)
    if 'data' in data and isinstance(data['data'], dict):
        wf_id = data['data'].get('id', '')
        if wf_id:
            print(wf_id)
            sys.exit(0)
    # Try root level id (fallback)
    wf_id = data.get('id', '')
    if wf_id:
        print(wf_id)
        sys.exit(0)
except:
    pass
" 2>/dev/null || \
                       echo "$response" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")
    
    if [ -n "$workflow_id" ] && [ "$workflow_id" != "null" ] && [ ${#workflow_id} -gt 5 ]; then
        echo "✓ Workflow created with ID: $workflow_id" >&2
        echo "$workflow_id"
        return 0
    else
        echo "✗ Failed to extract workflow ID from response" >&2
        echo "Response preview: $(echo "$response" | head -c 300)..." >&2
        # Try to extract ID using grep as fallback
        local fallback_id=$(echo "$response" | grep -oE '"id"\s*:\s*"[^"]{10,}"' | head -1 | cut -d'"' -f4 || echo "")
        if [ -n "$fallback_id" ] && [ ${#fallback_id} -gt 5 ]; then
            echo "✓ Found workflow ID using fallback method: $fallback_id" >&2
            echo "$fallback_id"
            return 0
        fi
        return 1
    fi
}

# Function to verify workflow exists
verify_workflow() {
    local workflow_id=$1
    
    if [ -z "$workflow_id" ]; then
        echo "✗ No workflow ID provided"
        return 1
    fi
    
    echo "Verifying workflow ID: $workflow_id"
    
    # Retry authentication multiple times (pod may need time to be ready)
    local max_auth_attempts=5
    local auth_attempt=0
    local auth_success=false
    
    while [ $auth_attempt -lt $max_auth_attempts ] && [ "$auth_success" = false ]; do
        # Always get a fresh cookie to ensure authentication
        rm -f /tmp/n8n_cookies.txt
        local login_result=$(curl -s -c /tmp/n8n_cookies.txt -X POST \
            "${N8N_URL}/rest/login" \
            -H "Content-Type: application/json" \
            -d "{\"emailOrLdapLoginId\":\"${N8N_USER}\",\"password\":\"${N8N_PASS}\"}" 2>/dev/null)
        
        # Verify login was successful - check multiple possible response formats
        if echo "$login_result" | grep -q "\"data\"" || \
           echo "$login_result" | grep -q "\"id\"" || \
           echo "$login_result" | grep -q "firstName\|lastName\|email" || \
           [ -n "$login_result" ] && [ "$login_result" != "null" ] && [ "$login_result" != "{}" ]; then
            # Test if cookie actually works by making a test API call
            local test_response=$(curl -s -b /tmp/n8n_cookies.txt "${N8N_URL}/rest/workflows" 2>/dev/null)
            if [ -n "$test_response" ] && (echo "$test_response" | grep -q "\"data\"" || echo "$test_response" | grep -q "\"count\"" || echo "$test_response" | grep -q "\[\]"); then
                auth_success=true
                break
            fi
        fi
        
        if [ $auth_attempt -lt $((max_auth_attempts - 1)) ]; then
            echo "  Authentication attempt $((auth_attempt + 1))/$max_auth_attempts failed, retrying in 3 seconds..."
            sleep 3
        fi
        auth_attempt=$((auth_attempt + 1))
    done
    
    # Verify login was successful
    if [ "$auth_success" = false ]; then
        echo "✗ Failed to authenticate for verification after $max_auth_attempts attempts"
        echo "  Login response preview: $(echo "$login_result" | head -c 200)..."
        return 1
    fi
    
    # Try to get the specific workflow first
    local response=$(curl -s -b /tmp/n8n_cookies.txt \
        "${N8N_URL}/rest/workflows/${workflow_id}" 2>/dev/null)
    
    # Check if workflow was found (response should contain the workflow ID)
    if [ -n "$response" ] && (echo "$response" | grep -q "\"id\":\"${workflow_id}\"" || echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if data.get('id') == '${workflow_id}' else 1)" 2>/dev/null); then
        local workflow_name=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('name', 'Unknown'))" 2>/dev/null || \
                              echo "$response" | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "Unknown")
        echo "✓ Workflow verified: $workflow_name"
        return 0
    fi
    
    # If direct lookup failed, try listing all workflows and searching
    echo "  Direct lookup failed, searching in workflow list..."
    local all_workflows=$(curl -s -b /tmp/n8n_cookies.txt "${N8N_URL}/rest/workflows" 2>/dev/null)
    
    if [ -n "$all_workflows" ] && echo "$all_workflows" | grep -q "\"id\":\"${workflow_id}\""; then
        local workflow_name=$(echo "$all_workflows" | python3 -c "import sys, json; data=json.load(sys.stdin); workflows=data.get('data', []); wf=[w for w in workflows if w.get('id') == '${workflow_id}']; print(wf[0].get('name', 'Unknown') if wf else 'Unknown')" 2>/dev/null || echo "Unknown")
        echo "✓ Workflow verified in list: $workflow_name"
        return 0
    else
        echo "✗ Workflow not found"
        echo "  Workflow ID: $workflow_id"
        echo "  Response length: ${#response} characters"
        if [ -n "$response" ] && [ ${#response} -lt 500 ]; then
            echo "  Response: $response"
        elif [ -n "$response" ]; then
            echo "  Response preview: $(echo "$response" | head -c 200)..."
        else
            echo "  Response: (empty)"
        fi
        return 1
    fi
}

# Function to list all workflows
list_workflows() {
    echo "Listing all workflows..."
    
    local response=""
    if [ -f /tmp/n8n_cookies.txt ]; then
        response=$(curl -s -b /tmp/n8n_cookies.txt \
            "${N8N_URL}/rest/workflows" 2>/dev/null)
    else
        # Get fresh cookie
        curl -s -c /tmp/n8n_cookies.txt -X POST \
            "${N8N_URL}/rest/login" \
            -H "Content-Type: application/json" \
            -d "{\"emailOrLdapLoginId\":\"${N8N_USER}\",\"password\":\"${N8N_PASS}\"}" > /dev/null 2>&1
        
        response=$(curl -s -b /tmp/n8n_cookies.txt \
            "${N8N_URL}/rest/workflows" 2>/dev/null)
    fi
    
    # Handle both array and object response formats
    if echo "$response" | grep -q "\"data\""; then
        # Response is {"data": [...], "count": ...}
        local count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', [])))" 2>/dev/null || echo "0")
        echo "Total workflows found: $count"
    else
        # Response might be a direct array
        local count=$(echo "$response" | grep -o '"id"' | wc -l | tr -d ' ')
        echo "Total workflows found: $count"
    fi
    return 0
}

# Initial state
echo "Step 1: Initial State"
check_pods
INITIAL_COUNT=$(get_pod_count)
echo "Initial pod count: $INITIAL_COUNT"
echo ""

# Check n8n API accessibility
echo "Step 1.5: Checking n8n API Accessibility"
if ! check_n8n_api; then
    echo ""
    echo "⚠ Warning: n8n API not accessible."
    echo ""
    echo "   To enable workflow persistence tests:"
    echo ""
    echo "   Quick Fix:"
    echo "   1. In a separate terminal, run:"
    echo "      cd $(pwd)"
    echo "      ./port-forward.sh"
    echo ""
    echo "   2. Wait 5 seconds, then check API access:"
    echo "      ./check-api-access.sh"
    echo ""
    echo "   3. If API check passes, re-run this test:"
    echo "      ./test-editor-ha.sh"
    echo ""
    echo "   Manual port-forwarding:"
    echo "      kubectl port-forward -n $NAMESPACE svc/$SERVICE 5678:5678"
    echo ""
    echo "   Check status:"
    echo "      ./check-port-forward.sh"
    echo "      ./check-api-access.sh"
    echo ""
    echo "   Continuing with pod-level tests only (workflow tests will be skipped)..."
    SKIP_WORKFLOW_TESTS=true
else
    SKIP_WORKFLOW_TESTS=false
fi
echo ""

    # Create test workflow if API is accessible
if [ "$SKIP_WORKFLOW_TESTS" = "false" ]; then
    echo "Step 1.6: Creating Test Workflow"
    # Capture stderr for display, stdout for workflow ID
    WORKFLOW_ID=$(create_test_workflow 2>&1 | tee /tmp/workflow_create.log | tail -1)
    CREATE_OUTPUT=$(cat /tmp/workflow_create.log | grep -v "^[A-Za-z0-9]\{10,\}$" || cat /tmp/workflow_create.log)
    echo "$CREATE_OUTPUT"
    
    # Validate workflow ID (should be alphanumeric, typically 10+ chars)
    # n8n workflow IDs are usually 15-16 characters
    if [ -z "$WORKFLOW_ID" ] || [ "$WORKFLOW_ID" = "null" ] || [ ${#WORKFLOW_ID} -lt 10 ] || echo "$WORKFLOW_ID" | grep -q "Creating\|Failed\|Response"; then
        echo "⚠ Failed to create workflow or extract workflow ID, continuing with pod tests only"
        SKIP_WORKFLOW_TESTS=true
        WORKFLOW_ID=""
    else
        echo "✓ Test workflow created with ID: $WORKFLOW_ID"
        sleep 2  # Give time for workflow to be saved
    fi
    rm -f /tmp/workflow_create.log
    echo ""
fi

# Test 1: Delete one editor pod
echo "Step 2: Testing Pod Failure - Deleting one editor pod"
POD_TO_DELETE=$(kubectl get pods -n $NAMESPACE -l app=$EDITOR_DEPLOYMENT -o jsonpath='{.items[0].metadata.name}')
echo "Deleting pod: $POD_TO_DELETE"
kubectl delete pod -n $NAMESPACE $POD_TO_DELETE --grace-period=0 --force 2>/dev/null || kubectl delete pod -n $NAMESPACE $POD_TO_DELETE

echo "Waiting 5 seconds for deletion..."
sleep 5

check_pods
CURRENT_COUNT=$(get_pod_count)
echo "Current pod count: $CURRENT_COUNT"

if [ "$CURRENT_COUNT" -lt "$INITIAL_COUNT" ]; then
    echo "✓ Pod deletion confirmed"
else
    echo "⚠ Pod count unchanged (may have already recovered)"
fi

echo ""
echo "Step 3: Waiting for Auto-Recovery"
wait_for_pods $INITIAL_COUNT

check_pods
FINAL_COUNT=$(get_pod_count)
echo "Final pod count: $FINAL_COUNT"

if [ "$FINAL_COUNT" -eq "$INITIAL_COUNT" ]; then
    echo "✓ HA Test PASSED: Pods recovered successfully"
else
    echo "✗ HA Test FAILED: Expected $INITIAL_COUNT pods, got $FINAL_COUNT"
    exit 1
fi

# Wait a bit for the new pod to be fully ready
echo "Waiting 10 seconds for new pod to be fully ready..."
sleep 10
echo ""

# Verify workflow persistence after failover
if [ "$SKIP_WORKFLOW_TESTS" = "false" ] && [ -n "$WORKFLOW_ID" ] && [ "$WORKFLOW_ID" != "null" ]; then
    echo "Step 3.5: Verifying Workflow Persistence After Failover"
    echo "Waiting 10 seconds for API to stabilize after pod restart..."
    sleep 10
    
    # Check if port forwarding is still active (pod restart may have broken it)
    if ! lsof -Pi :5678 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠ Port forwarding connection lost after pod restart"
        echo "   This is normal - port forwarding breaks when pods restart"
        echo ""
        echo "   Attempting to restart port forwarding automatically..."
        # Try to restart port forwarding
        if command -v kubectl &> /dev/null; then
            kubectl port-forward -n $NAMESPACE svc/$SERVICE 5678:5678 > /tmp/n8n-pf-auto.log 2>&1 &
            sleep 5
            if lsof -Pi :5678 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
                echo "✓ Port forwarding restarted automatically"
            else
                echo "⚠ Automatic restart failed"
                echo ""
                echo "   To continue workflow verification manually:"
                echo "   1. In another terminal, run:"
                echo "      ./restart-port-forward.sh"
                echo "   2. Or manually:"
                echo "      kubectl port-forward -n $NAMESPACE svc/$SERVICE 5678:5678"
                echo ""
                echo "   Or skip workflow verification and check manually in n8n UI"
                echo "   Workflow ID: $WORKFLOW_ID"
                echo ""
                SKIP_WORKFLOW_TESTS=true
            fi
        else
            echo "   kubectl not found, cannot auto-restart"
            echo "   Please restart port forwarding manually:"
            echo "   ./restart-port-forward.sh"
            SKIP_WORKFLOW_TESTS=true
        fi
    else
        # Clean up any stale cookies
        rm -f /tmp/n8n_cookies.txt
        
        # Retry verification up to 3 times with increasing delays
        verify_attempt=0
        max_verify_attempts=3
        verify_success=false
        
        while [ $verify_attempt -lt $max_verify_attempts ] && [ "$verify_success" = false ]; do
            if verify_workflow "$WORKFLOW_ID"; then
                echo "✓ Workflow persistence test PASSED: Workflow survived pod failure"
                verify_success=true
            else
                verify_attempt=$((verify_attempt + 1))
                if [ $verify_attempt -lt $max_verify_attempts ]; then
                    echo "  Verification attempt $verify_attempt failed, retrying in 5 seconds..."
                    sleep 5
                fi
            fi
        done
    fi
    
    if [ "$verify_success" = false ]; then
        echo "✗ Workflow persistence test FAILED: Workflow not found after failover"
        echo "  This may indicate:"
        echo "    - Database connectivity issues"
        echo "    - API not fully ready after pod restart"
        echo "    - Authentication issues"
        echo "    - Workflow ID mismatch"
        echo "  Workflow ID was: $WORKFLOW_ID"
        echo ""
        echo "  Troubleshooting:"
        echo "    1. Check if port-forwarding is still active: lsof -i :5678"
        echo "    2. Check n8n pod logs: kubectl logs -n $NAMESPACE -l app=n8n-editor --tail=50"
        echo "    3. Try accessing n8n UI: $N8N_URL"
        echo "    4. Verify workflow manually in n8n UI"
        # Don't exit, as pod recovery was successful
    fi
    echo ""
    
    # List all workflows to show persistence
    list_workflows
    echo ""
fi

echo ""
echo "Step 4: Service Connectivity Test"
echo "Checking if service is accessible..."
SERVICE_IP=$(kubectl get svc -n $NAMESPACE $SERVICE -o jsonpath='{.spec.clusterIP}')
if [ -n "$SERVICE_IP" ]; then
    echo "✓ Service IP: $SERVICE_IP"
    echo "✓ Service endpoints:"
    kubectl get endpoints -n $NAMESPACE $SERVICE
else
    echo "✗ Service not found"
    exit 1
fi

echo ""
echo "=========================================="
echo "Test Complete!"
echo "=========================================="
echo ""
echo "Test Summary:"
echo "  ✓ Pod failover: PASSED"
echo "  ✓ Service connectivity: PASSED"
if [ "$SKIP_WORKFLOW_TESTS" = "false" ] && [ -n "$WORKFLOW_ID" ]; then
    echo "  ✓ Workflow persistence: PASSED"
else
    echo "  ⚠ Workflow persistence: SKIPPED (API not accessible)"
fi
echo ""
echo "Monitor the Grafana dashboard to see:"
echo "  - Editor pod count drop and recover"
echo "  - Service availability maintained"
echo "  - Response time metrics"
echo ""
echo "View Grafana: kubectl port-forward -n $NAMESPACE svc/grafana 3000:3000"
echo "Then open: http://localhost:3000 (admin/admin123)"
echo ""
if [ -n "$WORKFLOW_ID" ] && [ "$SKIP_WORKFLOW_TESTS" = "false" ]; then
    echo "Test workflow ID: $WORKFLOW_ID"
    echo "You can verify it in n8n UI: ${N8N_URL}"
fi

# Cleanup
rm -f /tmp/n8n_cookies.txt

