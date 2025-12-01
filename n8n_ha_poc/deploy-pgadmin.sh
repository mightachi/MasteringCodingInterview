#!/bin/bash

# Deploy pgAdmin for visual PostgreSQL management

set -e

NAMESPACE="n8n-ha"

echo "=========================================="
echo "Deploying pgAdmin for PostgreSQL Access"
echo "=========================================="
echo ""

# Check if pgAdmin already exists
if kubectl get deployment pgadmin -n $NAMESPACE &> /dev/null; then
    echo "⚠ pgAdmin already exists. Delete it first if you want to redeploy."
    echo "   kubectl delete deployment,svc pgadmin -n $NAMESPACE"
    exit 1
fi

# Create pgAdmin deployment
kubectl create deployment pgadmin \
    --image=dpage/pgadmin4:latest \
    --namespace=$NAMESPACE \
    --env="PGADMIN_DEFAULT_EMAIL=admin@n8n.local" \
    --env="PGADMIN_DEFAULT_PASSWORD=admin123" \
    --env="PGADMIN_CONFIG_SERVER_MODE=False" \
    --env="PGADMIN_CONFIG_MASTER_PASSWORD_REQUIRED=False" \
    -o yaml --dry-run=client | kubectl apply -f -

# Create service
kubectl create service clusterip pgadmin \
    --tcp=80:80 \
    --namespace=$NAMESPACE \
    -o yaml --dry-run=client | kubectl apply -f -

# Wait for deployment
echo "Waiting for pgAdmin to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/pgadmin -n $NAMESPACE

echo ""
echo "=========================================="
echo "pgAdmin Deployed Successfully"
echo "=========================================="
echo ""
echo "1. Port forward pgAdmin:"
echo "   kubectl port-forward -n $NAMESPACE svc/pgadmin 5050:80"
echo ""
echo "2. Access pgAdmin:"
echo "   http://localhost:5050"
echo ""
echo "3. Login credentials:"
echo "   Email: admin@n8n.local"
echo "   Password: admin123"
echo ""
echo "4. Add PostgreSQL server in pgAdmin:"
echo "   - Host: postgresql-ha.n8n-ha.svc.cluster.local"
echo "   - Port: 5432"
echo "   - Database: n8n"
echo "   - Username: postgres"
echo "   - Password: postgres123"
echo ""
echo "To remove pgAdmin:"
echo "  kubectl delete deployment,svc pgadmin -n $NAMESPACE"
echo ""

