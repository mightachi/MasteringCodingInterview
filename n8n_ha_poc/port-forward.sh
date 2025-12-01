#!/bin/bash

# Port forwarding script for n8n HA services

set -e

NAMESPACE="n8n-ha"
PID_FILE="/tmp/n8n-ha-port-forward.pid"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping port forwarding..."
    if [ -f "$PID_FILE" ]; then
        while read pid; do
            kill $pid 2>/dev/null || true
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
    pkill -f "kubectl port-forward.*n8n-ha" || true
    echo "Port forwarding stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "=========================================="
echo "Starting Port Forwarding"
echo "=========================================="
echo ""

# Check if services exist
if ! kubectl get svc -n $NAMESPACE n8n-editor &> /dev/null; then
    echo "✗ Services not found. Please deploy first: ./deploy.sh"
    exit 1
fi

# Clear old PIDs
rm -f "$PID_FILE"

# Port forward n8n editor
echo "Forwarding n8n editor (localhost:5678)..."
# Check if port 5678 is already in use
if lsof -Pi :5678 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠ Port 5678 is already in use. Killing existing process..."
    lsof -ti :5678 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start port forward (will auto-reconnect if pod restarts via service)
kubectl port-forward -n $NAMESPACE svc/n8n-editor 5678:5678 > /tmp/n8n-pf.log 2>&1 &
PF_PID=$!
echo $PF_PID >> "$PID_FILE"
sleep 3
if kill -0 $PF_PID 2>/dev/null; then
    echo "✓ n8n editor port forward started (PID: $PF_PID)"
    echo "  Note: If pod restarts, port-forward may disconnect. Restart it if needed."
else
    echo "⚠ Port forward may have failed. Check logs: /tmp/n8n-pf.log"
fi

# Port forward Prometheus
echo "Forwarding Prometheus (localhost:9090)..."
# Check if port 9090 is already in use
if lsof -Pi :9090 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠ Port 9090 is already in use. Killing existing process..."
    lsof -ti :9090 | xargs kill -9 2>/dev/null || true
    sleep 2
fi
kubectl port-forward -n $NAMESPACE svc/prometheus 9090:9090 > /dev/null 2>&1 &
PF_PID=$!
echo $PF_PID >> "$PID_FILE"
sleep 3
if kill -0 $PF_PID 2>/dev/null; then
    echo "✓ Prometheus port forward started (PID: $PF_PID)"
fi

# Port forward Grafana
echo "Forwarding Grafana (localhost:3000)..."
# Check if port 3000 is already in use
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠ Port 3000 is already in use. Killing existing process..."
    lsof -ti :3000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi
kubectl port-forward -n $NAMESPACE svc/grafana 3000:3000 > /dev/null 2>&1 &
PF_PID=$!
echo $PF_PID >> "$PID_FILE"
sleep 3
# Verify port forward started
if kill -0 $PF_PID 2>/dev/null; then
    echo "✓ Grafana port forward started (PID: $PF_PID)"
else
    echo "⚠ Grafana port forward may have failed. Check manually."
fi

echo ""
echo "=========================================="
echo "Port Forwarding Active"
echo "=========================================="
echo ""
echo "Services:"
echo "  - n8n Editor:    http://localhost:5678"
echo "    Username: admin"
echo "    Password: admin123"
echo ""
echo "  - Prometheus:   http://localhost:9090"
echo ""
echo "  - Grafana:      http://localhost:3000"
echo "    Username: admin"
echo "    Password: admin123"
echo ""
echo "Press Ctrl+C to stop port forwarding"
echo ""

# Keep script running
while true; do
    sleep 1
done
