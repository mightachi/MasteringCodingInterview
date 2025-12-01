#!/bin/bash

# Quick test script to verify n8n API access

N8N_URL="http://localhost:5678"
N8N_USER="sukh.shukla@tiket.com"
N8N_PASS="Admin123"

echo "Testing n8n API access..."
echo ""

# Test 1: Health check
echo "1. Health check:"
if curl -s -f "${N8N_URL}/healthz" > /dev/null 2>&1; then
    echo "   ✓ Health endpoint accessible"
else
    echo "   ✗ Health endpoint not accessible"
    exit 1
fi

# Test 2: Root with basic auth
echo "2. Root endpoint with basic auth:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -u "${N8N_USER}:${N8N_PASS}" "${N8N_URL}/")
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✓ Root accessible with basic auth (HTTP $HTTP_CODE)"
else
    echo "   ✗ Root not accessible (HTTP $HTTP_CODE)"
fi

# Test 3: Get session cookie
echo "3. Getting session cookie:"
curl -s -c /tmp/n8n_test_cookie.txt -u "${N8N_USER}:${N8N_PASS}" "${N8N_URL}/" > /dev/null
if [ -f /tmp/n8n_test_cookie.txt ] && [ -s /tmp/n8n_test_cookie.txt ]; then
    echo "   ✓ Cookie file created"
    echo "   Cookie contents:"
    cat /tmp/n8n_test_cookie.txt | grep -v "^#" | grep -v "^$"
else
    echo "   ⚠ No cookie received"
fi

# Test 4: REST API with cookie
echo "4. REST API with cookie:"
RESPONSE=$(curl -s -b /tmp/n8n_test_cookie.txt "${N8N_URL}/rest/workflows")
if echo "$RESPONSE" | grep -q "Unauthorized"; then
    echo "   ✗ Unauthorized with cookie"
    echo "   Response: $RESPONSE"
else
    echo "   ✓ API accessible with cookie"
    echo "   Response type: $(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(type(data).__name__)" 2>/dev/null || echo "unknown")"
fi

# Test 5: REST API with basic auth
echo "5. REST API with basic auth:"
RESPONSE2=$(curl -s -u "${N8N_USER}:${N8N_PASS}" "${N8N_URL}/rest/workflows")
if echo "$RESPONSE2" | grep -q "Unauthorized"; then
    echo "   ✗ Unauthorized with basic auth"
    echo "   Response: $RESPONSE2"
else
    echo "   ✓ API accessible with basic auth"
    echo "   Response type: $(echo "$RESPONSE2" | python3 -c "import sys, json; data=json.load(sys.stdin); print(type(data).__name__)" 2>/dev/null || echo "unknown")"
fi

# Test 6: Login endpoint
echo "6. Login endpoint:"
LOGIN_RESPONSE=$(curl -s -X POST "${N8N_URL}/rest/login" \
    -H "Content-Type: application/json" \
    -d "{\"emailOrLdapLoginId\":\"${N8N_USER}\",\"password\":\"${N8N_PASS}\"}" \
    -c /tmp/n8n_login_cookie.txt)
echo "   Response: $LOGIN_RESPONSE"
if [ -f /tmp/n8n_login_cookie.txt ] && [ -s /tmp/n8n_login_cookie.txt ]; then
    echo "   ✓ Login cookie received"
    cat /tmp/n8n_login_cookie.txt | grep -v "^#" | grep -v "^$"
    
    # Test API with login cookie
    echo "7. REST API with login cookie:"
    RESPONSE3=$(curl -s -b /tmp/n8n_login_cookie.txt "${N8N_URL}/rest/workflows")
    if echo "$RESPONSE3" | grep -q "Unauthorized"; then
        echo "   ✗ Still unauthorized with login cookie"
    else
        echo "   ✓ API accessible with login cookie!"
    fi
fi

rm -f /tmp/n8n_test_cookie.txt /tmp/n8n_login_cookie.txt

echo ""
echo "Summary: Check which authentication method works above."

