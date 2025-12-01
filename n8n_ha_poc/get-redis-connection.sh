#!/bin/bash

# Script to get Redis connection details for RedisInsight

set -e

NAMESPACE="n8n-ha"
REDIS_POD=$(kubectl get pods -n $NAMESPACE -l app=redis,role=master -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$REDIS_POD" ]; then
    echo "✗ Redis pod not found"
    exit 1
fi

echo "=========================================="
echo "Redis Connection Details for RedisInsight"
echo "=========================================="
echo ""

# Check if port-forward is active
PF_ACTIVE=$(lsof -i :6379 2>/dev/null | grep -c kubectl || echo "0")

if [ "$PF_ACTIVE" = "0" ]; then
    echo "⚠ Port-forwarding is NOT active"
    echo ""
    echo "Start port-forwarding first:"
    echo "  kubectl port-forward -n $NAMESPACE $REDIS_POD 6379:6379"
    echo ""
    echo "Then use these connection details:"
else
    echo "✓ Port-forwarding is active"
    echo ""
    echo "Use these connection details in RedisInsight:"
fi

echo "----------------------------------------"
echo "Connection Details:"
echo "----------------------------------------"
echo ""
echo "  Host: localhost"
echo "  Port: 6379"
echo "  Username: (leave empty)"
echo "  Password: (leave empty)"
echo "  Database Index: 0"
echo ""
echo "Connection String:"
echo "  redis://localhost:6379"
echo ""

echo "----------------------------------------"
echo "Alternative: Cluster-Internal Connection"
echo "----------------------------------------"
echo ""
echo "If RedisInsight is deployed in Kubernetes:"
echo "  Host: redis-master.n8n-ha.svc.cluster.local"
echo "  Port: 6379"
echo "  Connection String: redis://redis-master.n8n-ha.svc.cluster.local:6379"
echo ""

echo "----------------------------------------"
echo "Quick Test"
echo "----------------------------------------"
echo ""
echo "After connecting, test with:"
echo "  PING"
echo "  KEYS *bull*"
echo ""

if [ "$PF_ACTIVE" = "0" ]; then
    echo "=========================================="
    echo "Start Port-Forwarding Now?"
    echo "=========================================="
    read -p "Start port-forwarding in background? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl port-forward -n $NAMESPACE $REDIS_POD 6379:6379 > /tmp/redis-port-forward.log 2>&1 &
        PF_PID=$!
        echo "✓ Port-forwarding started (PID: $PF_PID)"
        echo "  Logs: /tmp/redis-port-forward.log"
        echo ""
        echo "You can now connect to RedisInsight!"
        echo ""
        echo "To stop: kill $PF_PID"
    fi
fi

echo ""


