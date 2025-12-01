#!/bin/bash

# Script to fix DBeaver connection to PostgreSQL
# This script verifies credentials and provides connection instructions

set -e

NAMESPACE="n8n-ha"
DB_NAME="n8n"
DB_USER="postgres"

echo "=========================================="
echo "DBeaver PostgreSQL Connection Fix"
echo "=========================================="
echo ""

# Step 1: Get PostgreSQL pod
echo "Step 1: Finding PostgreSQL Pod"
echo "-------------------------------"
PRIMARY_POD=$(kubectl get pods -n $NAMESPACE -l app=postgresql,role=primary -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$PRIMARY_POD" ]; then
    echo "✗ PostgreSQL primary pod not found"
    echo "  Please ensure PostgreSQL is deployed: ./deploy.sh"
    exit 1
fi

echo "✓ Found PostgreSQL pod: $PRIMARY_POD"
echo ""

# Step 2: Get password from secret
echo "Step 2: Retrieving Password from Secret"
echo "----------------------------------------"
DB_PASSWORD=$(kubectl get secret postgresql-secret -n $NAMESPACE -o jsonpath='{.data.postgres-password}' 2>/dev/null | base64 -d || echo "")

if [ -z "$DB_PASSWORD" ]; then
    echo "⚠ Could not retrieve password from secret, using default: postgres123"
    DB_PASSWORD="postgres123"
else
    echo "✓ Password retrieved from secret"
fi

echo "  Username: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo "  Database: $DB_NAME"
echo ""

# Step 3: Test connection
echo "Step 3: Testing PostgreSQL Connection"
echo "--------------------------------------"
if kubectl exec -n $NAMESPACE $PRIMARY_POD -- psql -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null 2>&1; then
    echo "✓ PostgreSQL connection test successful"
else
    echo "✗ PostgreSQL connection test failed"
    echo "  This might indicate a configuration issue"
    exit 1
fi
echo ""

# Step 4: Check port forwarding
echo "Step 4: Checking Port Forwarding"
echo "----------------------------------"
if lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
    PF_PROCESS=$(lsof -Pi :5432 -sTCP:LISTEN -t | head -1)
    echo "✓ Port forwarding is active (PID: $PF_PROCESS)"
    echo "  Port 5432 is already in use"
    echo ""
    echo "  If this is NOT a kubectl port-forward, you may need to:"
    echo "    1. Stop the existing process using port 5432"
    echo "    2. Start port forwarding: kubectl port-forward -n $NAMESPACE $PRIMARY_POD 5432:5432"
else
    echo "⚠ Port forwarding is NOT active"
    echo ""
    echo "  Starting port forwarding..."
    echo "  Run this command in a separate terminal and keep it running:"
    echo ""
    echo "    kubectl port-forward -n $NAMESPACE $PRIMARY_POD 5432:5432"
    echo ""
    echo "  Or run it in the background:"
    echo "    kubectl port-forward -n $NAMESPACE $PRIMARY_POD 5432:5432 > /tmp/postgres-pf.log 2>&1 &"
    echo ""
    read -p "Start port forwarding now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting port forwarding in background..."
        kubectl port-forward -n $NAMESPACE $PRIMARY_POD 5432:5432 > /tmp/postgres-pf.log 2>&1 &
        PF_PID=$!
        echo $PF_PID > /tmp/postgres-pf.pid
        sleep 2
        if kill -0 $PF_PID 2>/dev/null; then
            echo "✓ Port forwarding started (PID: $PF_PID)"
            echo "  Logs: /tmp/postgres-pf.log"
        else
            echo "✗ Port forwarding failed. Check logs: /tmp/postgres-pf.log"
        fi
    fi
fi
echo ""

# Step 5: DBeaver connection instructions
echo "=========================================="
echo "DBeaver Connection Settings"
echo "=========================================="
echo ""
echo "Use these exact settings in DBeaver:"
echo ""
echo "  Connection Type: PostgreSQL"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: $DB_NAME"
echo "  Username: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""
echo "Important Notes:"
echo "  - Make sure port forwarding is active before connecting"
echo "  - If connection fails, verify the password is exactly: $DB_PASSWORD"
echo "  - Check that no other application is using port 5432"
echo ""

# Step 6: Test connection with psql (if port forwarding is active)
if lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Step 5: Testing Connection via Port Forward"
    echo "-------------------------------------------"
    echo "Testing connection through localhost:5432..."
    
    if command -v psql &> /dev/null; then
        if PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" > /dev/null 2>&1; then
            echo "✓ Connection test successful via port forward"
            echo "  DBeaver should be able to connect with the same credentials"
        else
            echo "⚠ Connection test failed via port forward"
            echo "  This might indicate:"
            echo "    - Port forwarding is not working correctly"
            echo "    - Password is incorrect"
            echo "    - PostgreSQL is not accepting connections"
        fi
    else
        echo "⚠ psql not found, skipping connection test"
        echo "  You can test manually:"
        echo "    PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME"
    fi
    echo ""
fi

# Step 7: Troubleshooting
echo "=========================================="
echo "Troubleshooting"
echo "=========================================="
echo ""
echo "If connection still fails:"
echo ""
echo "1. Verify password:"
echo "   kubectl get secret postgresql-secret -n $NAMESPACE -o jsonpath='{.data.postgres-password}' | base64 -d"
echo ""
echo "2. Test direct connection:"
echo "   kubectl exec -it -n $NAMESPACE $PRIMARY_POD -- psql -U $DB_USER -d $DB_NAME"
echo ""
echo "3. Check PostgreSQL logs:"
echo "   kubectl logs -n $NAMESPACE $PRIMARY_POD | tail -20"
echo ""
echo "4. Verify port forwarding:"
echo "   lsof -i :5432"
echo "   kubectl port-forward -n $NAMESPACE $PRIMARY_POD 5432:5432"
echo ""
echo "5. Reset password (if needed):"
echo "   kubectl delete secret postgresql-secret -n $NAMESPACE"
echo "   # Then update postgresql-ha.yaml and redeploy"
echo ""

echo "=========================================="
echo "Quick Connection Test"
echo "=========================================="
echo ""
read -p "Test connection now with psql? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v psql &> /dev/null; then
        if lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "Connecting to PostgreSQL..."
            PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT 'Connection successful!' as status, version() as postgres_version;"
        else
            echo "⚠ Port forwarding not active. Starting direct connection..."
            kubectl exec -it -n $NAMESPACE $PRIMARY_POD -- psql -U $DB_USER -d $DB_NAME
        fi
    else
        echo "⚠ psql not found. Install PostgreSQL client or use DBeaver."
    fi
fi

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
echo "DBeaver Connection Details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: $DB_NAME"
echo "  Username: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""
echo "Make sure port forwarding is active before connecting!"
echo ""

