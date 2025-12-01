#!/bin/bash

# Cleanup script for n8n HA POC

set -e

NAMESPACE="n8n-ha"

echo "=========================================="
echo "Cleaning up n8n HA POC"
echo "=========================================="
echo ""

# Stop port forwarding
echo "Stopping port forwarding..."
pkill -f "kubectl port-forward.*n8n-ha" || true
rm -f /tmp/n8n-ha-port-forward.pid
echo "✓ Port forwarding stopped"
echo ""

# Delete namespace (this will delete all resources)
echo "Deleting namespace: $NAMESPACE"
kubectl delete namespace $NAMESPACE --ignore-not-found=true
echo "✓ Namespace deleted"
echo ""

echo "=========================================="
echo "Cleanup Complete!"
echo "=========================================="

