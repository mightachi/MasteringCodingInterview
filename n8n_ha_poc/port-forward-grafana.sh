#!/bin/bash

# Quick script to port-forward Grafana only

NAMESPACE="n8n-ha"

echo "Port forwarding Grafana to localhost:3000..."
echo "Press Ctrl+C to stop"
echo ""

# Check if Grafana service exists
if ! kubectl get svc -n $NAMESPACE grafana &> /dev/null; then
    echo "✗ Grafana service not found. Please deploy first: ./deploy.sh"
    exit 1
fi

# Check if port 3000 is already in use
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠ Port 3000 is already in use. Killing existing port-forward..."
    pkill -f "kubectl port-forward.*grafana.*3000" || true
    sleep 2
fi

# Start port forwarding
kubectl port-forward -n $NAMESPACE svc/grafana 3000:3000

