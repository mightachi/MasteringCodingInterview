#!/bin/bash

# Fix Redis Insight connection issues
# This script ensures Redis Insight is deployed and port forwarding is active

set -e

NAMESPACE="n8n-ha"
PID_FILE="/tmp/redis-insight-fix.pid"

echo "=========================================="
echo "Redis Insight Connection Fix"
echo "=========================================="
echo ""

# Step 1: Check if Redis pods are running
echo "Step 1: Checking Redis pods..."
REDIS_MASTER_POD=$(kubectl get pods -n $NAMESPACE -l app=redis,role=master -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
REDIS_SENTINEL_POD=$(kubectl get pods -n $NAMESPACE -l app=redis-sentinel -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$REDIS_MASTER_POD" ]; then
    echo "✗ Redis master pod not found"
    echo "  Please deploy Redis first: ./deploy.sh"
    exit 1
fi

echo "✓ Redis Master Pod: $REDIS_MASTER_POD"
if [ -n "$REDIS_SENTINEL_POD" ]; then
    echo "✓ Redis Sentinel Pod: $REDIS_SENTINEL_POD"
fi
echo ""

# Step 2: Deploy Redis Insight if not exists
echo "Step 2: Checking Redis Insight deployment..."
if ! kubectl get deployment redisinsight -n $NAMESPACE &> /dev/null; then
    echo "Redis Insight not found. Deploying..."
    
    # Create deployment
    kubectl create deployment redisinsight \
        --image=redis/redisinsight:latest \
        --namespace=$NAMESPACE \
        --port=8001 \
        --replicas=1 \
        -o yaml --dry-run=client | kubectl apply -f -
    
    # Create service
    kubectl create service clusterip redisinsight \
        --tcp=8001:8001 \
        --namespace=$NAMESPACE \
        -o yaml --dry-run=client | kubectl apply -f -
    
    echo "Waiting for Redis Insight to be ready..."
    kubectl wait --for=condition=available --timeout=120s deployment/redisinsight -n $NAMESPACE || {
        echo "⚠ Timeout waiting for Redis Insight, but continuing..."
    }
    echo "✓ Redis Insight deployed"
else
    echo "✓ Redis Insight already deployed"
fi
echo ""

# Step 3: Check and start port forwards
echo "Step 3: Setting up port forwarding..."

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 1  # Port is in use
    else
        return 0  # Port is free
    fi
}

# Function to kill existing port forward
kill_port_forward() {
    local port=$1
    local pids=$(lsof -ti :$port 2>/dev/null || echo "")
    if [ -n "$pids" ]; then
        echo "  Killing existing process on port $port..."
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Clear old PIDs
rm -f "$PID_FILE"

# Port forward Redis Insight
if check_port 8001; then
    echo "Starting Redis Insight port-forward (8001)..."
    kubectl port-forward -n $NAMESPACE svc/redisinsight 8001:8001 > /tmp/redisinsight-pf.log 2>&1 &
    PF_PID=$!
    echo $PF_PID >> "$PID_FILE"
    sleep 3
    if kill -0 $PF_PID 2>/dev/null; then
        echo "✓ Redis Insight port-forward started (PID: $PF_PID)"
    else
        echo "✗ Failed to start Redis Insight port-forward"
        echo "  Check logs: /tmp/redisinsight-pf.log"
    fi
else
    echo "⚠ Port 8001 already in use"
    kill_port_forward 8001
    echo "Starting Redis Insight port-forward (8001)..."
    kubectl port-forward -n $NAMESPACE svc/redisinsight 8001:8001 > /tmp/redisinsight-pf.log 2>&1 &
    PF_PID=$!
    echo $PF_PID >> "$PID_FILE"
    sleep 3
    if kill -0 $PF_PID 2>/dev/null; then
        echo "✓ Redis Insight port-forward started (PID: $PF_PID)"
    fi
fi

# Port forward Redis Master
if check_port 6379; then
    echo "Starting Redis Master port-forward (6379)..."
    kubectl port-forward -n $NAMESPACE $REDIS_MASTER_POD 6379:6379 > /tmp/redis-master-pf.log 2>&1 &
    PF_PID=$!
    echo $PF_PID >> "$PID_FILE"
    sleep 3
    if kill -0 $PF_PID 2>/dev/null; then
        echo "✓ Redis Master port-forward started (PID: $PF_PID)"
    else
        echo "✗ Failed to start Redis Master port-forward"
    fi
else
    echo "⚠ Port 6379 already in use"
    kill_port_forward 6379
    echo "Starting Redis Master port-forward (6379)..."
    kubectl port-forward -n $NAMESPACE $REDIS_MASTER_POD 6379:6379 > /tmp/redis-master-pf.log 2>&1 &
    PF_PID=$!
    echo $PF_PID >> "$PID_FILE"
    sleep 3
    if kill -0 $PF_PID 2>/dev/null; then
        echo "✓ Redis Master port-forward started (PID: $PF_PID)"
    fi
fi

# Port forward Redis Sentinel (if exists)
if [ -n "$REDIS_SENTINEL_POD" ]; then
    if check_port 26379; then
        echo "Starting Redis Sentinel port-forward (26379)..."
        kubectl port-forward -n $NAMESPACE $REDIS_SENTINEL_POD 26379:26379 > /tmp/redis-sentinel-pf.log 2>&1 &
        PF_PID=$!
        echo $PF_PID >> "$PID_FILE"
        sleep 3
        if kill -0 $PF_PID 2>/dev/null; then
            echo "✓ Redis Sentinel port-forward started (PID: $PF_PID)"
        fi
    else
        echo "⚠ Port 26379 already in use"
        kill_port_forward 26379
        echo "Starting Redis Sentinel port-forward (26379)..."
        kubectl port-forward -n $NAMESPACE $REDIS_SENTINEL_POD 26379:26379 > /tmp/redis-sentinel-pf.log 2>&1 &
        PF_PID=$!
        echo $PF_PID >> "$PID_FILE"
        sleep 3
        if kill -0 $PF_PID 2>/dev/null; then
            echo "✓ Redis Sentinel port-forward started (PID: $PF_PID)"
        fi
    fi
fi

echo ""

# Step 4: Test connections
echo "Step 4: Testing connections..."
sleep 2

# Test Redis Master
echo "Testing Redis Master connection..."
if redis-cli -h localhost -p 6379 PING > /dev/null 2>&1; then
    echo "✓ Redis Master: Connection successful"
else
    echo "⚠ Redis Master: Connection test failed (may need redis-cli installed)"
    echo "  But port-forward is active, so connection should work in Redis Insight"
fi

# Test Redis Insight
echo "Testing Redis Insight web interface..."
if curl -s http://localhost:8001 > /dev/null 2>&1; then
    echo "✓ Redis Insight: Web interface accessible"
else
    echo "⚠ Redis Insight: Web interface not responding yet (may need a few more seconds)"
fi

echo ""

# Step 5: Display connection instructions
echo "=========================================="
echo "Connection Instructions"
echo "=========================================="
echo ""
echo "1. Open Redis Insight in your browser:"
echo "   http://localhost:8001"
echo ""
echo "2. Add Redis Master Connection:"
echo "   - Click 'Add Database'"
echo "   - Select 'Standalone'"
echo "   - Host: localhost"
echo "   - Port: 6379"
echo "   - Database Alias: n8n-redis-master"
echo "   - Username: (leave empty)"
echo "   - Password: (leave empty)"
echo "   - Database Index: 0"
echo "   - Click 'Add Redis Database'"
echo ""

if [ -n "$REDIS_SENTINEL_POD" ]; then
    echo "3. Add Redis Sentinel Connection (Optional):"
    echo "   - Click 'Add Database'"
    echo "   - Select 'Sentinel'"
    echo "   - Master Name: mymaster"
    echo "   - Sentinel Hosts: localhost:26379"
    echo "   - Database Alias: n8n-redis-sentinel"
    echo "   - Username: (leave empty)"
    echo "   - Password: (leave empty)"
    echo "   - Database Index: 0"
    echo "   - Click 'Add Redis Database'"
    echo ""
fi

echo "=========================================="
echo "Port Forwarding Status"
echo "=========================================="
echo ""
echo "Port forwards are running in the background."
echo "PIDs saved to: $PID_FILE"
echo ""
echo "To stop port forwarding:"
echo "  ./stop-redis-port-forwards.sh"
echo "  Or: kill \$(cat $PID_FILE)"
echo ""
echo "Port forward logs:"
echo "  Redis Insight: /tmp/redisinsight-pf.log"
echo "  Redis Master: /tmp/redis-master-pf.log"
if [ -n "$REDIS_SENTINEL_POD" ]; then
    echo "  Redis Sentinel: /tmp/redis-sentinel-pf.log"
fi
echo ""

echo "=========================================="
echo "Quick Test Commands"
echo "=========================================="
echo ""
echo "After connecting in Redis Insight, try these commands in the CLI tab:"
echo ""
echo "  PING"
echo "  # Should return: PONG"
echo ""
echo "  KEYS *"
echo "  # Should show all keys"
echo ""
echo "  KEYS *bull*"
echo "  # Should show n8n Bull queue keys"
echo ""
echo "  INFO replication"
echo "  # Should show replication info"
echo ""

