#!/bin/bash

# Comprehensive health check for n8n HA cluster

set -e

NAMESPACE="n8n-ha"
EXIT_CODE=0

echo "=========================================="
echo "n8n HA Cluster Health Check"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check pod status
check_pods() {
    local app=$1
    local expected=$2
    local label=$3
    
    if [ -z "$label" ]; then
        label="app=$app"
    fi
    
    local pods=$(kubectl get pods -n $NAMESPACE -l "$label" --no-headers 2>/dev/null || echo "")
    local running=$(echo "$pods" | grep -c "Running" || echo "0")
    local total=$(echo "$pods" | wc -l | tr -d ' ')
    
    if [ "$total" -eq 0 ]; then
        echo -e "${RED}✗${NC} $app: No pods found"
        return 1
    elif [ "$running" -eq "$expected" ]; then
        echo -e "${GREEN}✓${NC} $app: $running/$expected pods running"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $app: $running/$expected pods running (expected $expected)"
        echo "$pods" | grep -v "Running" | while read line; do
            if [ -n "$line" ]; then
                pod_name=$(echo "$line" | awk '{print $1}')
                status=$(echo "$line" | awk '{print $3}')
                echo "    Pod $pod_name: $status"
            fi
        done
        return 1
    fi
}

# Function to check service
check_service() {
    local service=$1
    
    if kubectl get svc -n $NAMESPACE $service &> /dev/null; then
        local endpoints=$(kubectl get endpoints -n $NAMESPACE $service -o jsonpath='{.subsets[0].addresses[*].ip}' 2>/dev/null || echo "")
        if [ -n "$endpoints" ]; then
            echo -e "${GREEN}✓${NC} Service $service: Has endpoints"
            return 0
        else
            echo -e "${YELLOW}⚠${NC} Service $service: No endpoints"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} Service $service: Not found"
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    local pod=$(kubectl get pods -n $NAMESPACE -l app=postgresql,role=primary -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [ -z "$pod" ]; then
        echo -e "${RED}✗${NC} PostgreSQL: Pod not found"
        return 1
    fi
    
    if kubectl exec -n $NAMESPACE $pod -- psql -U postgres -d n8n -c "SELECT 1;" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} PostgreSQL: Database accessible"
        return 0
    else
        echo -e "${RED}✗${NC} PostgreSQL: Database not accessible"
        return 1
    fi
}

# Function to check Redis connectivity
check_redis() {
    local pod=$(kubectl get pods -n $NAMESPACE -l app=redis,role=master -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [ -z "$pod" ]; then
        echo -e "${RED}✗${NC} Redis: Pod not found"
        return 1
    fi
    
    if kubectl exec -n $NAMESPACE $pod -- redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Redis: Accessible"
        return 0
    else
        echo -e "${RED}✗${NC} Redis: Not accessible"
        return 1
    fi
}

# Function to check n8n API
check_n8n_api() {
    local pod=$(kubectl get pods -n $NAMESPACE -l app=n8n-editor -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [ -z "$pod" ]; then
        echo -e "${YELLOW}⚠${NC} n8n API: Pod not found (cannot test)"
        return 1
    fi
    
    # Check if pod is ready
    local ready=$(kubectl get pod -n $NAMESPACE $pod -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "False")
    if [ "$ready" != "True" ]; then
        echo -e "${YELLOW}⚠${NC} n8n API: Pod not ready"
        return 1
    fi
    
    # Try to exec into pod and check health endpoint
    if kubectl exec -n $NAMESPACE $pod -- wget -q -O- http://localhost:5678/healthz > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} n8n API: Health endpoint responding"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} n8n API: Health endpoint not responding (may need port-forwarding to test externally)"
        return 1
    fi
}

# 1. Check namespace
echo "1. Namespace:"
if kubectl get namespace $NAMESPACE &> /dev/null; then
    echo -e "${GREEN}✓${NC} Namespace $NAMESPACE exists"
else
    echo -e "${RED}✗${NC} Namespace $NAMESPACE not found"
    EXIT_CODE=1
fi
echo ""

# 2. Check PostgreSQL
echo "2. PostgreSQL:"
check_pods "postgresql" 1 "app=postgresql,role=primary" || EXIT_CODE=1
check_service "postgresql-ha" || EXIT_CODE=1
check_database || EXIT_CODE=1
echo ""

# 3. Check Redis
echo "3. Redis:"
check_pods "redis" 1 "app=redis,role=master" || EXIT_CODE=1
check_pods "redis" 2 "app=redis,role=replica" || EXIT_CODE=1
check_pods "redis-sentinel" 3 || EXIT_CODE=1
check_service "redis-master" || EXIT_CODE=1
check_service "redis-sentinel" || EXIT_CODE=1
check_redis || EXIT_CODE=1
echo ""

# 4. Check n8n Editor
echo "4. n8n Editor:"
check_pods "n8n-editor" 2 || EXIT_CODE=1
check_service "n8n-editor" || EXIT_CODE=1
check_n8n_api || EXIT_CODE=1
echo ""

# 5. Check n8n Worker
echo "5. n8n Worker:"
check_pods "n8n-worker" 2 || EXIT_CODE=1
echo ""

# 6. Check Monitoring
echo "6. Monitoring:"
check_pods "prometheus" 1 || EXIT_CODE=1
check_service "prometheus" || EXIT_CODE=1
check_pods "grafana" 1 || EXIT_CODE=1
check_service "grafana" || EXIT_CODE=1
echo ""

# 7. Overall status
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Cluster Status: HEALTHY${NC}"
    echo ""
    echo "All components are running correctly!"
else
    echo -e "${YELLOW}⚠ Cluster Status: NEEDS ATTENTION${NC}"
    echo ""
    echo "Some components have issues. Check the details above."
    echo ""
    echo "To restart components:"
    echo "  ./restart-cluster.sh        - Restart all components"
    echo "  kubectl delete pod -n $NAMESPACE <pod-name>  - Restart specific pod"
fi
echo "=========================================="
echo ""

# Show pod summary
echo "Pod Summary:"
kubectl get pods -n $NAMESPACE -o wide | head -1
kubectl get pods -n $NAMESPACE -o wide | grep -E "NAME|postgresql|redis|n8n|prometheus|grafana" | head -20

echo ""
echo "For detailed logs:"
echo "  kubectl logs -n $NAMESPACE <pod-name>"
echo ""

exit $EXIT_CODE


