#!/bin/bash

# Script to check if port forwarding is active

echo "Checking port forwarding status..."
echo ""

# Check each port
PORTS=("5678:n8n" "9090:Prometheus" "3000:Grafana")

ALL_ACTIVE=true

for port_info in "${PORTS[@]}"; do
    IFS=':' read -r port name <<< "$port_info"
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        PID=$(lsof -Pi :$port -sTCP:LISTEN -t | head -1)
        echo "✓ $name (port $port) - ACTIVE (PID: $PID)"
    else
        echo "✗ $name (port $port) - NOT ACTIVE"
        ALL_ACTIVE=false
    fi
done

echo ""

if [ "$ALL_ACTIVE" = true ]; then
    echo "✅ All port forwards are active!"
    echo ""
    echo "Access services:"
    echo "  - n8n:        http://localhost:5678"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana:   http://localhost:3000"
else
    echo "⚠ Some port forwards are not active"
    echo ""
    echo "To start port forwarding, run:"
    echo "  ./port-forward.sh"
    echo ""
    echo "Or port-forward individual services:"
    echo "  kubectl port-forward -n n8n-ha svc/n8n-editor 5678:5678"
    echo "  kubectl port-forward -n n8n-ha svc/prometheus 9090:9090"
    echo "  kubectl port-forward -n n8n-ha svc/grafana 3000:3000"
fi
