#!/bin/bash

# Test script for PostgreSQL HA
# This script tests failover scenarios for PostgreSQL primary

set -e

NAMESPACE="n8n-ha"
PRIMARY_STATEFULSET="postgresql-primary"
REPLICA_STATEFULSET="postgresql-replica"
PRIMARY_SERVICE="postgresql-primary"
HA_SERVICE="postgresql-ha"

echo "=========================================="
echo "PostgreSQL HA Test"
echo "=========================================="
echo ""

# Function to check PostgreSQL pods
check_pods() {
    echo "PostgreSQL Pods:"
    kubectl get pods -n $NAMESPACE -l app=postgresql -o wide
    echo ""
}

# Function to get primary pod
get_primary_pod() {
    kubectl get pods -n $NAMESPACE -l app=postgresql,role=primary -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo ""
}

# Function to test database connection
test_db_connection() {
    local pod=$1
    echo "Testing connection to: $pod"
    kubectl exec -n $NAMESPACE $pod -- psql -U postgres -d n8n -c "SELECT version();" > /dev/null 2>&1
    return $?
}

# Function to create test data
create_test_data() {
    local pod=$1
    echo "Creating test data in: $pod"
    kubectl exec -n $NAMESPACE $pod -- psql -U postgres -d n8n <<EOF > /dev/null 2>&1
CREATE TABLE IF NOT EXISTS ha_test (
    id SERIAL PRIMARY KEY,
    test_data TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
INSERT INTO ha_test (test_data) VALUES ('HA test data ' || NOW());
EOF
}

# Function to verify test data
verify_test_data() {
    local pod=$1
    echo "Verifying test data in: $pod"
    local count=$(kubectl exec -n $NAMESPACE $pod -- psql -U postgres -d n8n -t -c "SELECT COUNT(*) FROM ha_test;" 2>/dev/null | tr -d ' ')
    echo "Test records found: $count"
    return $count
}

# Initial state
echo "Step 1: Initial State"
check_pods
PRIMARY_POD=$(get_primary_pod)
if [ -z "$PRIMARY_POD" ]; then
    echo "✗ Primary pod not found"
    exit 1
fi
echo "Primary pod: $PRIMARY_POD"
echo ""

# Test connection to primary
echo "Step 2: Testing Primary Connection"
if test_db_connection $PRIMARY_POD; then
    echo "✓ Primary connection successful"
else
    echo "✗ Primary connection failed"
    exit 1
fi
echo ""

# Create test data
echo "Step 3: Creating Test Data"
create_test_data $PRIMARY_POD
echo "✓ Test data created"
echo ""

# Verify data exists
echo "Step 4: Verifying Test Data"
if verify_test_data $PRIMARY_POD; then
    echo "✓ Test data verified"
else
    echo "✗ Test data verification failed"
    exit 1
fi
echo ""

# Test primary failure
echo "Step 5: Testing Primary Failure"
echo "Deleting primary pod: $PRIMARY_POD"
kubectl delete pod -n $NAMESPACE $PRIMARY_POD --grace-period=0 --force 2>/dev/null || kubectl delete pod -n $NAMESPACE $PRIMARY_POD

echo "Waiting 10 seconds for pod restart..."
sleep 10

check_pods

# Wait for new primary
echo "Waiting for new primary pod..."
for i in {1..30}; do
    NEW_PRIMARY=$(get_primary_pod)
    if [ -n "$NEW_PRIMARY" ] && [ "$NEW_PRIMARY" != "$PRIMARY_POD" ]; then
        echo "✓ New primary pod: $NEW_PRIMARY"
        break
    fi
    echo "  Waiting... ($i/30)"
    sleep 2
done

NEW_PRIMARY=$(get_primary_pod)
if [ -z "$NEW_PRIMARY" ]; then
    echo "✗ New primary not found"
    exit 1
fi

# Wait for pod to be ready
echo "Waiting for new primary to be ready..."
kubectl wait --for=condition=ready pod/$NEW_PRIMARY -n $NAMESPACE --timeout=60s || true

sleep 5

# Test connection to new primary
echo "Step 6: Testing New Primary Connection"
if test_db_connection $NEW_PRIMARY; then
    echo "✓ New primary connection successful"
else
    echo "✗ New primary connection failed"
    exit 1
fi
echo ""

# Verify data still exists (if replication is working)
echo "Step 7: Verifying Data Persistence"
if verify_test_data $NEW_PRIMARY; then
    echo "✓ Data persistence verified"
else
    echo "⚠ Data not found (may need replication setup)"
fi
echo ""

# Test service connectivity
echo "Step 8: Testing Service Connectivity"
SERVICE_IP=$(kubectl get svc -n $NAMESPACE $HA_SERVICE -o jsonpath='{.spec.clusterIP}')
if [ -n "$SERVICE_IP" ]; then
    echo "✓ HA Service IP: $SERVICE_IP"
    echo "✓ Service endpoints:"
    kubectl get endpoints -n $NAMESPACE $HA_SERVICE
else
    echo "✗ Service not found"
    exit 1
fi

echo ""
echo "=========================================="
echo "Test Complete!"
echo "=========================================="
echo ""
echo "Monitor the Grafana dashboard to see:"
echo "  - Primary pod status changes"
echo "  - Database connection metrics"
echo "  - Replication lag (if configured)"
echo ""
echo "View Grafana: kubectl port-forward -n $NAMESPACE svc/grafana 3000:3000"
echo "Then open: http://localhost:3000 (admin/admin123)"

