#!/bin/bash

# Script to connect to PostgreSQL
# Usage: ./connect-postgresql.sh

NAMESPACE="n8n-ha"
DB_USER="postgres"
DB_NAME="n8n"

echo "🔍 Finding PostgreSQL pod..."

# Try standard deployment first, then HA setup with role=primary
POSTGRESQL_POD=$(kubectl get pods -n $NAMESPACE -l app=postgresql -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$POSTGRESQL_POD" ]; then
    # Try HA setup with role=primary
    POSTGRESQL_POD=$(kubectl get pods -n $NAMESPACE -l app=postgresql,role=primary -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
fi

if [ -z "$POSTGRESQL_POD" ]; then
    echo "❌ Error: Could not find PostgreSQL pod"
    echo ""
    echo "Available pods in namespace $NAMESPACE:"
    kubectl get pods -n $NAMESPACE
    exit 1
fi

echo "✅ Found PostgreSQL pod: $POSTGRESQL_POD"
echo "🔌 Connecting to PostgreSQL..."
echo ""

# Connect to PostgreSQL
kubectl exec -it -n $NAMESPACE $POSTGRESQL_POD -- psql -U $DB_USER -d $DB_NAME

