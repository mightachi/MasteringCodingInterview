#!/bin/bash

# Deploy Redis GUI tools for visual queue inspection

set -e

NAMESPACE="n8n-ha"
GUI_TYPE="${1:-redisinsight}"  # redisinsight, rediscommander, or anotherredis

echo "=========================================="
echo "Redis GUI Deployment"
echo "=========================================="
echo ""

# Check if Redis is accessible
REDIS_POD=$(kubectl get pods -n $NAMESPACE -l app=redis,role=master -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [ -z "$REDIS_POD" ]; then
    echo "✗ Redis pod not found"
    exit 1
fi

echo "Redis Pod: $REDIS_POD"
echo ""

case "$GUI_TYPE" in
    redisinsight|ri)
        echo "Deploying RedisInsight (Recommended - Best UI)"
        echo "--------------------------------------------"
        
        # Check if already exists
        if kubectl get deployment redisinsight -n $NAMESPACE &> /dev/null; then
            echo "⚠ RedisInsight already exists"
            echo "   Access: kubectl port-forward -n $NAMESPACE svc/redisinsight 8001:8001"
            exit 0
        fi
        
        # Create RedisInsight deployment
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
        echo "Waiting for RedisInsight to be ready..."
        kubectl wait --for=condition=available --timeout=120s deployment/redisinsight -n $NAMESPACE
        
        echo ""
        echo "✓ RedisInsight deployed!"
        echo ""
        echo "1. Port forward:"
        echo "   kubectl port-forward -n $NAMESPACE svc/redisinsight 8001:8001"
        echo ""
        echo "2. Access: http://localhost:8001"
        echo ""
        echo "3. Add Redis connection:"
        echo "   - Host: postgresql-ha.n8n-ha.svc.cluster.local"
        echo "   - Wait, use: redis-master.n8n-ha.svc.cluster.local"
        echo "   - Port: 6379"
        echo "   - No password (or check Redis config)"
        echo ""
        echo "   OR use port-forwarded connection:"
        echo "   - Start: kubectl port-forward -n $NAMESPACE $REDIS_POD 6379:6379"
        echo "   - Host: localhost"
        echo "   - Port: 6379"
        ;;
        
    rediscommander|rc)
        echo "Deploying Redis Commander (Lightweight)"
        echo "--------------------------------------------"
        
        if kubectl get deployment rediscommander -n $NAMESPACE &> /dev/null; then
            echo "⚠ Redis Commander already exists"
            exit 0
        fi
        
        # Create Redis Commander deployment
        kubectl create deployment rediscommander \
            --image=rediscommander/redis-commander:latest \
            --namespace=$NAMESPACE \
            --env="REDIS_HOSTS=local:redis-master:6379" \
            --port=8081 \
            -o yaml --dry-run=client | kubectl apply -f -
        
        # Create service
        kubectl create service clusterip rediscommander \
            --tcp=8081:8081 \
            --namespace=$NAMESPACE \
            -o yaml --dry-run=client | kubectl apply -f -
        
        echo "Waiting for Redis Commander to be ready..."
        kubectl wait --for=condition=available --timeout=120s deployment/rediscommander -n $NAMESPACE
        
        echo ""
        echo "✓ Redis Commander deployed!"
        echo ""
        echo "1. Port forward:"
        echo "   kubectl port-forward -n $NAMESPACE svc/rediscommander 8081:8081"
        echo ""
        echo "2. Access: http://localhost:8081"
        echo ""
        echo "3. Connection is pre-configured to redis-master"
        ;;
        
    *)
        echo "Usage: $0 [redisinsight|rediscommander]"
        echo ""
        echo "Options:"
        echo "  redisinsight (default) - Best UI, recommended"
        echo "  rediscommander        - Lightweight alternative"
        echo ""
        echo "Or use local GUI tools with port-forwarding:"
        echo "  kubectl port-forward -n $NAMESPACE $REDIS_POD 6379:6379"
        exit 1
        ;;
esac

echo ""
echo "To remove:"
echo "  kubectl delete deployment,svc ${GUI_TYPE} -n $NAMESPACE"
echo ""

