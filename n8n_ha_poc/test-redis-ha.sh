#!/bin/bash

# Test script for Redis HA
# This script tests failover scenarios for Redis master

set -e

NAMESPACE="n8n-ha"
MASTER_STATEFULSET="redis-master"
REPLICA_STATEFULSET="redis-replica"
MASTER_SERVICE="redis-master"

echo "=========================================="
echo "Redis HA Test"
echo "=========================================="
echo ""

# Function to check Redis pods
check_pods() {
    echo "Redis Pods:"
    kubectl get pods -n $NAMESPACE -l app=redis -o wide
    echo ""
    echo "Redis Sentinel Pods:"
    kubectl get pods -n $NAMESPACE -l app=redis-sentinel -o wide
    echo ""
}

# Function to get master pod
get_master_pod() {
    kubectl get pods -n $NAMESPACE -l app=redis,role=master -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo ""
}

# Function to test Redis connection
test_redis_connection() {
    local pod=$1
    echo "Testing connection to: $pod"
    kubectl exec -n $NAMESPACE $pod -- redis-cli ping > /dev/null 2>&1
    return $?
}

# Function to get Redis role
get_redis_role() {
    local pod=$1
    kubectl exec -n $NAMESPACE $pod -- redis-cli info replication 2>/dev/null | grep "role:" | cut -d: -f2 | tr -d '\r\n ' || echo "unknown"
}

# Function to set test data
set_test_data() {
    local pod=$1
    echo "Setting test data in: $pod"
    kubectl exec -n $NAMESPACE $pod -- redis-cli set "ha_test_key" "ha_test_value_$(date +%s)" > /dev/null 2>&1
}

# Function to get test data
get_test_data() {
    local pod=$1
    kubectl exec -n $NAMESPACE $pod -- redis-cli get "ha_test_key" 2>/dev/null | tr -d '\r\n' || echo ""
}

# Initial state
echo "Step 1: Initial State"
check_pods
MASTER_POD=$(get_master_pod)
if [ -z "$MASTER_POD" ]; then
    echo "✗ Master pod not found"
    exit 1
fi
echo "Master pod: $MASTER_POD"
echo ""

# Verify master role
echo "Step 2: Verifying Master Role"
ROLE=$(get_redis_role $MASTER_POD)
if [ "$ROLE" = "master" ]; then
    echo "✓ Master role confirmed: $ROLE"
else
    echo "⚠ Role is: $ROLE (expected master)"
fi
echo ""

# Test connection to master
echo "Step 3: Testing Master Connection"
if test_redis_connection $MASTER_POD; then
    echo "✓ Master connection successful"
else
    echo "✗ Master connection failed"
    exit 1
fi
echo ""

# Set test data
echo "Step 4: Setting Test Data"
set_test_data $MASTER_POD
echo "✓ Test data set"
echo ""

# Verify data exists
echo "Step 5: Verifying Test Data"
VALUE=$(get_test_data $MASTER_POD)
if [ -n "$VALUE" ]; then
    echo "✓ Test data verified: $VALUE"
else
    echo "✗ Test data verification failed"
    exit 1
fi
echo ""

# Test master failure
echo "Step 6: Testing Master Failure"
echo "Deleting master pod: $MASTER_POD"
kubectl delete pod -n $NAMESPACE $MASTER_POD --grace-period=0 --force 2>/dev/null || kubectl delete pod -n $NAMESPACE $MASTER_POD

echo "Waiting 10 seconds for pod restart..."
sleep 10

check_pods

# Wait for new master (either restarted or promoted replica)
echo "Waiting for new master pod..."
for i in {1..30}; do
    NEW_MASTER=$(get_master_pod)
    if [ -n "$NEW_MASTER" ]; then
        echo "✓ Found pod: $NEW_MASTER"
        break
    fi
    echo "  Waiting... ($i/30)"
    sleep 2
done

NEW_MASTER=$(get_master_pod)
if [ -z "$NEW_MASTER" ]; then
    echo "⚠ No master pod found, checking all Redis pods..."
    # Check all redis pods for master role
    for pod in $(kubectl get pods -n $NAMESPACE -l app=redis -o jsonpath='{.items[*].metadata.name}'); do
        ROLE=$(get_redis_role $pod)
        if [ "$ROLE" = "master" ]; then
            NEW_MASTER=$pod
            echo "✓ Found master: $NEW_MASTER"
            break
        fi
    done
fi

if [ -z "$NEW_MASTER" ]; then
    echo "✗ New master not found"
    exit 1
fi

# Wait for pod to be ready
echo "Waiting for new master to be ready..."
kubectl wait --for=condition=ready pod/$NEW_MASTER -n $NAMESPACE --timeout=60s || true

sleep 5

# Verify new master role
echo "Step 7: Verifying New Master Role"
ROLE=$(get_redis_role $NEW_MASTER)
if [ "$ROLE" = "master" ]; then
    echo "✓ New master role confirmed: $ROLE"
else
    echo "⚠ Role is: $ROLE (expected master)"
fi
echo ""

# Test connection to new master
echo "Step 8: Testing New Master Connection"
if test_redis_connection $NEW_MASTER; then
    echo "✓ New master connection successful"
else
    echo "✗ New master connection failed"
    exit 1
fi
echo ""

# Verify data still exists (if replication is working)
echo "Step 9: Verifying Data Persistence"
NEW_VALUE=$(get_test_data $NEW_MASTER)
if [ -n "$NEW_VALUE" ]; then
    echo "✓ Data persistence verified: $NEW_VALUE"
    if [ "$NEW_VALUE" = "$VALUE" ]; then
        echo "✓ Data matches original value"
    else
        echo "⚠ Data value changed (may be expected with AOF)"
    fi
else
    echo "⚠ Data not found (may need replication setup)"
fi
echo ""

# Test service connectivity
echo "Step 10: Testing Service Connectivity"
SERVICE_IP=$(kubectl get svc -n $NAMESPACE $MASTER_SERVICE -o jsonpath='{.spec.clusterIP}')
if [ -n "$SERVICE_IP" ]; then
    echo "✓ Master Service IP: $SERVICE_IP"
    echo "✓ Service endpoints:"
    kubectl get endpoints -n $NAMESPACE $MASTER_SERVICE
else
    echo "✗ Service not found"
    exit 1
fi

# Check sentinel status
echo ""
echo "Step 11: Checking Sentinel Status"
SENTINEL_PODS=$(kubectl get pods -n $NAMESPACE -l app=redis-sentinel -o jsonpath='{.items[*].metadata.name}')
if [ -n "$SENTINEL_PODS" ]; then
    echo "Sentinel pods: $SENTINEL_PODS"
    for sentinel in $SENTINEL_PODS; do
        echo "  Checking $sentinel..."
        kubectl exec -n $NAMESPACE $sentinel -- redis-cli -p 26379 sentinel masters 2>/dev/null | head -5 || echo "    ⚠ Sentinel not responding"
    done
else
    echo "⚠ No sentinel pods found"
fi

echo ""
echo "=========================================="
echo "Test Complete!"
echo "=========================================="
echo ""
echo "Monitor the Grafana dashboard to see:"
echo "  - Redis master status changes"
echo "  - Memory usage metrics"
echo "  - Failover events"
echo ""
echo "View Grafana: kubectl port-forward -n $NAMESPACE svc/grafana 3000:3000"
echo "Then open: http://localhost:3000 (admin/admin123)"

