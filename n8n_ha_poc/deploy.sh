#!/bin/bash

# Deployment script for n8n HA POC
# This script deploys all components in the correct order

set -e

NAMESPACE="n8n-ha"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "n8n HA POC Deployment"
echo "=========================================="
echo ""

# Check prerequisites
echo "Step 1: Checking Prerequisites"
if ! command -v kubectl &> /dev/null; then
    echo "✗ kubectl not found. Please install kubectl."
    exit 1
fi
echo "✓ kubectl found"

if ! kubectl cluster-info &> /dev/null; then
    echo "✗ Kubernetes cluster not accessible. Please ensure cluster is running."
    exit 1
fi
echo "✓ Kubernetes cluster accessible"
echo ""

# Create namespace
echo "Step 2: Creating Namespace"
kubectl apply -f "$SCRIPT_DIR/namespace.yaml"
echo "✓ Namespace created"
echo ""

# Deploy PostgreSQL HA
echo "Step 3: Deploying PostgreSQL HA"
kubectl apply -f "$SCRIPT_DIR/postgresql-ha.yaml"
echo "✓ PostgreSQL HA configuration applied"
echo "Waiting for PostgreSQL primary to be ready..."
kubectl wait --for=condition=ready pod -l app=postgresql,role=primary -n $NAMESPACE --timeout=120s || echo "⚠ Timeout waiting for PostgreSQL primary"
echo ""

# Deploy Redis HA
echo "Step 4: Deploying Redis HA"
kubectl apply -f "$SCRIPT_DIR/redis-ha.yaml"
echo "✓ Redis HA configuration applied"
echo "Waiting for Redis master to be ready..."
kubectl wait --for=condition=ready pod -l app=redis,role=master -n $NAMESPACE --timeout=120s || echo "⚠ Timeout waiting for Redis master"
echo ""

# Wait a bit for databases to be fully ready
echo "Waiting 15 seconds for databases to stabilize..."
sleep 15
echo ""

# Verify PostgreSQL is ready and database exists
echo "Verifying PostgreSQL connection..."
PRIMARY_POD=$(kubectl get pods -n $NAMESPACE -l app=postgresql,role=primary -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [ -n "$PRIMARY_POD" ]; then
    echo "Checking if PostgreSQL is accepting connections..."
    for i in {1..12}; do
        if kubectl exec -n $NAMESPACE $PRIMARY_POD -- pg_isready -U postgres > /dev/null 2>&1; then
            echo "✓ PostgreSQL is ready"
            # Verify database exists
            DB_EXISTS=$(kubectl exec -n $NAMESPACE $PRIMARY_POD -- psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='n8n'" 2>/dev/null || echo "0")
            if [ "$DB_EXISTS" != "1" ]; then
                echo "⚠ Database 'n8n' does not exist, but PostgreSQL will create it on first connection"
            else
                echo "✓ Database 'n8n' exists"
            fi
            break
        fi
        if [ $i -eq 12 ]; then
            echo "⚠ PostgreSQL may not be fully ready, but continuing..."
        else
            echo "  Waiting for PostgreSQL... ($i/12)"
            sleep 5
        fi
    done
else
    echo "⚠ PostgreSQL pod not found yet"
fi
echo ""

# Deploy n8n Editor and Workers
echo "Step 5: Deploying n8n Editor and Workers"
kubectl apply -f "$SCRIPT_DIR/n8n-editor-ha.yaml"
echo "✓ n8n configuration applied"
echo "Waiting for n8n editor pods to be ready..."
kubectl wait --for=condition=ready pod -l app=n8n-editor -n $NAMESPACE --timeout=180s || echo "⚠ Timeout waiting for n8n editor"
echo "Waiting for n8n worker pods to be ready..."
kubectl wait --for=condition=ready pod -l app=n8n-worker -n $NAMESPACE --timeout=180s || echo "⚠ Timeout waiting for n8n worker"
echo ""

# Deploy Monitoring
echo "Step 6: Deploying Monitoring (Prometheus & Grafana)"
kubectl apply -f "$SCRIPT_DIR/monitoring.yaml"
echo "✓ Monitoring configuration applied"
echo "Waiting for Prometheus to be ready..."
kubectl wait --for=condition=ready pod -l app=prometheus -n $NAMESPACE --timeout=120s || echo "⚠ Timeout waiting for Prometheus"
echo "Waiting for Grafana to be ready..."
kubectl wait --for=condition=ready pod -l app=grafana -n $NAMESPACE --timeout=120s || echo "⚠ Timeout waiting for Grafana"
echo ""

# Import Grafana dashboard
echo "Step 7: Setting up Grafana Dashboard"
echo "Waiting 10 seconds for Grafana to initialize..."
sleep 10

# Create dashboard via API (if Grafana is ready)
GRAFANA_POD=$(kubectl get pods -n $NAMESPACE -l app=grafana -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [ -n "$GRAFANA_POD" ]; then
    echo "Grafana dashboard will be available after port-forwarding"
    echo "Run: ./port-forward.sh"
    echo "Then import dashboard from: grafana-dashboard.json"
fi
echo ""

# Show status
echo "Step 8: Deployment Status"
echo ""
echo "Pods:"
kubectl get pods -n $NAMESPACE
echo ""
echo "Services:"
kubectl get svc -n $NAMESPACE
echo ""

echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. If you see database connection issues, run: ./fix-postgres-connection.sh"
echo "2. Port forward services: ./port-forward.sh"
echo "3. Access n8n: http://localhost:5678 (admin/admin123)"
echo "4. Access Grafana: http://localhost:3000 (admin/admin123)"
echo "5. Import Grafana dashboard from: grafana-dashboard.json"
echo "6. Run HA tests:"
echo "   - ./test-editor-ha.sh"
echo "   - ./test-postgres-ha.sh"
echo "   - ./test-worker-ha.sh"
echo "   - ./test-redis-ha.sh"
echo ""
