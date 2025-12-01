#!/bin/bash

# Quick script to check if n8n API is accessible

NAMESPACE="n8n-ha"
N8N_URL="http://localhost:5678"
N8N_USER="${N8N_USER:-sukh.shukla@tiket.com}"
N8N_PASS="${N8N_PASS:-Admin123}"

echo "=========================================="
echo "n8n API Accessibility Check"
echo "=========================================="
echo ""

# Check port forwarding
echo "1. Checking port forwarding..."
if lsof -Pi :5678 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    PID=$(lsof -Pi :5678 -sTCP:LISTEN -t | head -1)
    echo "✓ Port forwarding is active (PID: $PID)"
else
    echo "✗ Port forwarding is NOT active"
    echo ""
    echo "   To start port forwarding:"
    echo "   ./port-forward.sh"
    echo "   Or: kubectl port-forward -n $NAMESPACE svc/n8n-editor 5678:5678"
    echo ""
    exit 1
fi

# Check health endpoint
echo ""
echo "2. Checking health endpoint..."
if curl -s -f --connect-timeout 3 "${N8N_URL}/healthz" > /dev/null 2>&1; then
    echo "✓ Health endpoint is accessible"
elif curl -s -f --connect-timeout 3 -u "${N8N_USER}:${N8N_PASS}" "${N8N_URL}/healthz" > /dev/null 2>&1; then
    echo "✓ Health endpoint is accessible (with auth)"
else
    echo "✗ Health endpoint is NOT accessible"
    echo "   Check if n8n pods are running:"
    echo "   kubectl get pods -n $NAMESPACE -l app=n8n-editor"
    exit 1
fi

# Check login
echo ""
echo "3. Testing authentication..."
rm -f /tmp/n8n_api_check_cookies.txt
LOGIN_RESPONSE=$(curl -s -c /tmp/n8n_api_check_cookies.txt -X POST \
    "${N8N_URL}/rest/login" \
    -H "Content-Type: application/json" \
    -d "{\"emailOrLdapLoginId\":\"${N8N_USER}\",\"password\":\"${N8N_PASS}\"}" 2>/dev/null)

if echo "$LOGIN_RESPONSE" | grep -q "\"data\"" || echo "$LOGIN_RESPONSE" | grep -q "\"id\""; then
    echo "✓ Login successful"
else
    echo "✗ Login failed"
    echo "   Response: $(echo "$LOGIN_RESPONSE" | head -c 200)"
    echo ""
    echo "   Possible issues:"
    echo "   - Invalid credentials (user: ${N8N_USER})"
    echo "   - User account not created in n8n"
    echo "   - n8n requires initial setup"
    echo ""
    echo "   To fix:"
    echo "   1. Visit: ${N8N_URL}"
    echo "   2. Complete initial setup or login"
    echo "   3. Create user account if needed"
    rm -f /tmp/n8n_api_check_cookies.txt
    exit 1
fi

# Check API access
echo ""
echo "4. Testing API access..."
WORKFLOWS_RESPONSE=$(curl -s -b /tmp/n8n_api_check_cookies.txt "${N8N_URL}/rest/workflows" 2>/dev/null)

if [ -n "$WORKFLOWS_RESPONSE" ] && (echo "$WORKFLOWS_RESPONSE" | grep -q "\"data\"" || echo "$WORKFLOWS_RESPONSE" | grep -q "\"count\""); then
    echo "✓ API is accessible"
    WORKFLOW_COUNT=$(echo "$WORKFLOWS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', [])))" 2>/dev/null || echo "?")
    echo "  Found $WORKFLOW_COUNT workflow(s)"
else
    echo "✗ API access failed"
    echo "   Response: $(echo "$WORKFLOWS_RESPONSE" | head -c 200)"
    rm -f /tmp/n8n_api_check_cookies.txt
    exit 1
fi

rm -f /tmp/n8n_api_check_cookies.txt

echo ""
echo "=========================================="
echo "✓ All checks passed!"
echo "=========================================="
echo ""
echo "n8n API is fully accessible and ready for workflow tests."
echo "You can now run: ./test-editor-ha.sh"
echo ""

