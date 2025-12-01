#!/bin/bash

# Script to access PostgreSQL database for n8n HA POC

set -e

NAMESPACE="n8n-ha"
DB_NAME="n8n"
DB_USER="postgres"
DB_PASSWORD="postgres123"
SERVICE="postgresql-ha"

echo "=========================================="
echo "PostgreSQL Access Options"
echo "=========================================="
echo ""

# Check if PostgreSQL pod is running
PRIMARY_POD=$(kubectl get pods -n $NAMESPACE -l app=postgresql,role=primary -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$PRIMARY_POD" ]; then
    echo "✗ PostgreSQL primary pod not found"
    echo "   Make sure PostgreSQL is deployed: ./deploy.sh"
    exit 1
fi

echo "✓ PostgreSQL pod found: $PRIMARY_POD"
echo ""

# Option 1: Port forward and use psql
echo "Option 1: Port Forward + psql (Command Line)"
echo "--------------------------------------------"
echo "1. Start port-forwarding (in a separate terminal):"
echo "   kubectl port-forward -n $NAMESPACE $PRIMARY_POD 5432:5432"
echo ""
echo "2. Connect with psql:"
echo "   PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME"
echo ""
echo "3. Useful psql commands:"
echo "   \\dt              - List all tables"
echo "   \\d+ table_name  - Describe table structure"
echo "   SELECT * FROM workflow LIMIT 10;  - View workflows"
echo "   \\q               - Quit"
echo ""

# Option 2: Direct kubectl exec
echo "Option 2: Direct kubectl exec"
echo "--------------------------------------------"
echo "Connect directly:"
echo "  kubectl exec -it -n $NAMESPACE $PRIMARY_POD -- psql -U $DB_USER -d $DB_NAME"
echo ""

# Option 3: Port forward for GUI tools
echo "Option 3: Port Forward for GUI Tools (pgAdmin, DBeaver, etc.)"
echo "--------------------------------------------"
echo "1. Start port-forwarding:"
echo "   kubectl port-forward -n $NAMESPACE $PRIMARY_POD 5432:5432"
echo ""
echo "2. Use GUI tool with these settings:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: $DB_NAME"
echo "   Username: $DB_USER"
echo "   Password: $DB_PASSWORD"
echo ""

# Option 4: Quick query
echo "Option 4: Quick Query (Run Now)"
echo "--------------------------------------------"
read -p "Run a quick query to list tables? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Listing tables in database '$DB_NAME':"
    kubectl exec -n $NAMESPACE $PRIMARY_POD -- psql -U $DB_USER -d $DB_NAME -c "\dt" 2>/dev/null || \
    kubectl exec -n $NAMESPACE $PRIMARY_POD -- psql -U $DB_USER -d $DB_NAME -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
    echo ""
    
    read -p "Show workflow table structure? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl exec -n $NAMESPACE $PRIMARY_POD -- psql -U $DB_USER -d $DB_NAME -c "\d+ workflow" 2>/dev/null || \
        kubectl exec -n $NAMESPACE $PRIMARY_POD -- psql -U $DB_USER -d $DB_NAME -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'workflow';"
    fi
fi

echo ""
echo "=========================================="
echo "Recommended: Use pgAdmin or DBeaver"
echo "=========================================="
echo ""
echo "1. Install pgAdmin (https://www.pgadmin.org/) or DBeaver (https://dbeaver.io/)"
echo "2. Start port-forwarding: kubectl port-forward -n $NAMESPACE $PRIMARY_POD 5432:5432"
echo "3. Connect with the credentials shown above"
echo ""

