#!/bin/bash

# Script to check workflows in PostgreSQL
# Usage: ./check-workflows.sh [workflow_name_pattern]

NAMESPACE="n8n-ha"
DB_USER="postgres"
DB_NAME="n8n"

# Get PostgreSQL pod name
echo "🔍 Finding PostgreSQL pod..."
POSTGRESQL_POD=$(kubectl get pods -n $NAMESPACE -l app=postgresql -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$POSTGRESQL_POD" ]; then
    # Try HA setup with role=primary
    POSTGRESQL_POD=$(kubectl get pods -n $NAMESPACE -l app=postgresql,role=primary -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
fi

if [ -z "$POSTGRESQL_POD" ]; then
    echo "❌ Error: Could not find PostgreSQL pod"
    echo "Available pods:"
    kubectl get pods -n $NAMESPACE
    exit 1
fi

echo "✅ Found PostgreSQL pod: $POSTGRESQL_POD"
echo ""

# Check if workflow name pattern is provided
if [ -n "$1" ]; then
    PATTERN="$1"
    echo "📋 Searching for workflows matching: '$PATTERN'"
    echo ""
    kubectl exec -n $NAMESPACE $POSTGRESQL_POD -- psql -U $DB_USER -d $DB_NAME -c "SELECT id, name, active, \"createdAt\", \"updatedAt\" FROM workflow_entity WHERE name LIKE '%$PATTERN%' ORDER BY \"createdAt\" DESC;"
else
    echo "📊 Listing all workflows:"
    echo ""
    kubectl exec -n $NAMESPACE $POSTGRESQL_POD -- psql -U $DB_USER -d $DB_NAME -c "SELECT id, name, active, \"createdAt\", \"updatedAt\" FROM workflow_entity ORDER BY \"createdAt\" DESC;"
fi

echo ""
echo "📈 Workflow Statistics:"
kubectl exec -n $NAMESPACE $POSTGRESQL_POD -- psql -U $DB_USER -d $DB_NAME -c "
SELECT 
    COUNT(*) as total_workflows,
    COUNT(*) FILTER (WHERE active = true) as active_workflows,
    COUNT(*) FILTER (WHERE active = false) as inactive_workflows
FROM workflow_entity;
"

echo ""
echo "🔄 Recent Executions:"
kubectl exec -n $NAMESPACE $POSTGRESQL_POD -- psql -U $DB_USER -d $DB_NAME -c "
SELECT 
    e.id,
    w.name as workflow_name,
    e.finished,
    e.mode,
    e.\"startedAt\",
    e.\"stoppedAt\"
FROM execution_entity e
LEFT JOIN workflow_entity w ON e.\"workflowId\" = w.id
ORDER BY e.\"startedAt\" DESC
LIMIT 10;
"

