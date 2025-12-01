#!/bin/bash

# Quick status check for n8n HA cluster

NAMESPACE="n8n-ha"

echo "=========================================="
echo "n8n HA Cluster - Quick Status"
echo "=========================================="
echo ""

# Get all pods and their status
echo "Component Status:"
echo "-----------------"
kubectl get pods -n $NAMESPACE -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,READY:.status.containerStatuses[0].ready,RESTARTS:.status.containerStatuses[0].restartCount 2>/dev/null | grep -E "NAME|postgresql|redis|n8n|prometheus|grafana" | head -20

echo ""
echo "Service Endpoints:"
echo "-----------------"
kubectl get svc -n $NAMESPACE -o custom-columns=NAME:.metadata.name,TYPE:.spec.type,CLUSTER-IP:.spec.clusterIP,PORT:.spec.ports[0].port 2>/dev/null | head -10

echo ""
echo "Quick Health Check:"
echo "------------------"

# Count running pods
POSTGRES_RUNNING=$(kubectl get pods -n $NAMESPACE -l app=postgresql,role=primary --no-headers 2>/dev/null | grep -c Running || echo "0")
REDIS_RUNNING=$(kubectl get pods -n $NAMESPACE -l app=redis,role=master --no-headers 2>/dev/null | grep -c Running || echo "0")
EDITOR_RUNNING=$(kubectl get pods -n $NAMESPACE -l app=n8n-editor --no-headers 2>/dev/null | grep -c Running || echo "0")
WORKER_RUNNING=$(kubectl get pods -n $NAMESPACE -l app=n8n-worker --no-headers 2>/dev/null | grep -c Running || echo "0")

echo "PostgreSQL: $POSTGRES_RUNNING/1"
echo "Redis:      $REDIS_RUNNING/1"
echo "n8n Editor: $EDITOR_RUNNING/2"
echo "n8n Worker: $WORKER_RUNNING/2"

echo ""
if [ "$POSTGRES_RUNNING" -eq 1 ] && [ "$REDIS_RUNNING" -eq 1 ] && [ "$EDITOR_RUNNING" -eq 2 ] && [ "$WORKER_RUNNING" -eq 2 ]; then
    echo "✓ All critical components running"
else
    echo "⚠ Some components need attention"
    echo ""
    echo "Run detailed check: ./health-check.sh"
    echo "Or restart: ./restart-cluster.sh"
fi

echo ""


