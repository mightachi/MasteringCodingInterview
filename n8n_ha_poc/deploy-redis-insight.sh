#!/bin/bash

# Deploy Redis Insight and connect to Redis + Sentinel

set -e

NAMESPACE="n8n-ha"

echo "=========================================="
echo "Redis Insight Deployment"
echo "=========================================="
echo ""

# Check if Redis is accessible
REDIS_MASTER_POD=$(kubectl get pods -n $NAMESPACE -l app=redis,role=master -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
REDIS_SENTINEL_POD=$(kubectl get pods -n $NAMESPACE -l app=redis-sentinel -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$REDIS_MASTER_POD" ]; then
    echo "✗ Redis master pod not found"
    exit 1
fi

if [ -z "$REDIS_SENTINEL_POD" ]; then
    echo "⚠ Redis Sentinel pod not found (continuing anyway)"
fi

echo "✓ Redis Master Pod: $REDIS_MASTER_POD"
if [ -n "$REDIS_SENTINEL_POD" ]; then
    echo "✓ Redis Sentinel Pod: $REDIS_SENTINEL_POD"
fi
echo ""

# Check if Redis Insight already exists
if kubectl get deployment redisinsight -n $NAMESPACE &> /dev/null; then
    echo "⚠ Redis Insight already exists"
    echo ""
    echo "Access Redis Insight:"
    echo "  kubectl port-forward -n $NAMESPACE svc/redisinsight 8001:8001"
    echo "  Then open: http://localhost:8001"
    echo ""
    echo "Skipping deployment..."
else
    echo "Deploying Redis Insight..."
    
    # Create Redis Insight deployment
    kubectl create deployment redisinsight \
        --image=redis/redisinsight:latest \
        --namespace=$NAMESPACE \
        --port=8001 \
        -o yaml --dry-run=client | kubectl apply -f -
    
    # Create service
    kubectl create service clusterip redisinsight \
        --tcp=8001:8001 \
        --namespace=$NAMESPACE \
        -o yaml --dry-run=client | kubectl apply -f -
    
    # Wait for deployment
    echo "Waiting for Redis Insight to be ready..."
    kubectl wait --for=condition=available --timeout=120s deployment/redisinsight -n $NAMESPACE
    
    echo ""
    echo "✓ Redis Insight deployed!"
fi

echo ""
echo "=========================================="
echo "Connection Setup Instructions"
echo "=========================================="
echo ""

# Start port-forwarding for Redis Insight
echo "1. Start Port-Forwarding for Redis Insight:"
echo "   kubectl port-forward -n $NAMESPACE svc/redisinsight 8001:8001"
echo "   (Keep this terminal open)"
echo ""

# Start port-forwarding for Redis Master
echo "2. Start Port-Forwarding for Redis Master (in another terminal):"
echo "   kubectl port-forward -n $NAMESPACE $REDIS_MASTER_POD 6379:6379"
echo ""

# Start port-forwarding for Redis Sentinel
if [ -n "$REDIS_SENTINEL_POD" ]; then
    echo "3. Start Port-Forwarding for Redis Sentinel (in another terminal):"
    echo "   kubectl port-forward -n $NAMESPACE $REDIS_SENTINEL_POD 26379:26379"
    echo ""
fi

echo "4. Access Redis Insight:"
echo "   http://localhost:8001"
echo ""

echo "=========================================="
echo "Connection 1: Redis Master"
echo "=========================================="
echo ""
echo "In Redis Insight, add a new database connection:"
echo ""
echo "  Connection Type: Standalone"
echo "  Host: localhost"
echo "  Port: 6379"
echo "  Database Alias: n8n-redis-master"
echo "  Username: (leave empty)"
echo "  Password: (leave empty - no password configured)"
echo "  Database Index: 0"
echo ""
echo "  Connection String: redis://localhost:6379"
echo ""

echo "=========================================="
echo "Connection 2: Redis Sentinel"
echo "=========================================="
echo ""
if [ -n "$REDIS_SENTINEL_POD" ]; then
    echo "In Redis Insight, add a new database connection:"
    echo ""
    echo "  Connection Type: Sentinel"
    echo "  Master Name: mymaster"
    echo "  Sentinel Hosts:"
    echo "    - localhost:26379"
    echo "  Database Alias: n8n-redis-sentinel"
    echo "  Username: (leave empty)"
    echo "  Password: (leave empty)"
    echo "  Database Index: 0"
    echo ""
    echo "  Note: Sentinel connection will automatically discover the master"
    echo ""
else
    echo "⚠ Redis Sentinel not found. Skipping Sentinel connection."
    echo ""
fi

echo "=========================================="
echo "Alternative: Direct Cluster Connection"
echo "=========================================="
echo ""
echo "If Redis Insight is running in Kubernetes, you can connect directly:"
echo ""
echo "Connection 1 - Redis Master (Direct):"
echo "  Host: redis-master.n8n-ha.svc.cluster.local"
echo "  Port: 6379"
echo "  Connection String: redis://redis-master.n8n-ha.svc.cluster.local:6379"
echo ""

if [ -n "$REDIS_SENTINEL_POD" ]; then
    echo "Connection 2 - Redis Sentinel (Direct):"
    echo "  Connection Type: Sentinel"
    echo "  Master Name: mymaster"
    echo "  Sentinel Hosts:"
    echo "    - redis-sentinel.n8n-ha.svc.cluster.local:26379"
    echo ""
fi

echo "=========================================="
echo "Testing Connections"
echo "=========================================="
echo ""
echo "After connecting, test with these Redis commands in Redis Insight CLI:"
echo ""
echo "  PING"
echo "  # Should return: PONG"
echo ""
echo "  KEYS *"
echo "  # Should show all keys"
echo ""
echo "  KEYS *bull*"
echo "  # Should show Bull queue keys (n8n workflow queue)"
echo ""
echo "  INFO replication"
echo "  # Should show replication info"
echo ""

echo "=========================================="
echo "Sentinel Commands (via Sentinel connection)"
echo "=========================================="
echo ""
if [ -n "$REDIS_SENTINEL_POD" ]; then
    echo "Connect to Sentinel and run:"
    echo ""
    echo "  SENTINEL masters"
    echo "  # List all monitored masters"
    echo ""
    echo "  SENTINEL get-master-addr-by-name mymaster"
    echo "  # Get current master address"
    echo ""
    echo "  SENTINEL replicas mymaster"
    echo "  # List replicas for master"
    echo ""
    echo "  SENTINEL sentinels mymaster"
    echo "  # List other sentinels"
    echo ""
else
    echo "⚠ Redis Sentinel not available"
    echo ""
fi

echo "=========================================="
echo "Quick Start Script"
echo "=========================================="
echo ""
echo "To start all port-forwards automatically, run:"
echo "  ./start-redis-port-forwards.sh"
echo ""

echo "To remove Redis Insight:"
echo "  kubectl delete deployment,svc redisinsight -n $NAMESPACE"
echo ""


