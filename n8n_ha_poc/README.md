# n8n High Availability Proof of Concept

This POC demonstrates a minimal high availability setup for n8n with PostgreSQL and Redis, including comprehensive test cases and Grafana monitoring.

## Architecture

```
┌─────────────────┐
│   n8n Editor    │  (2 replicas with session affinity)
│   (Load Bal.)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Postgres│ │ Redis │
│Primary │ │Master │
└───┬───┘ └───┬───┘
    │         │
┌───▼───┐ ┌──▼────┐
│Postgres│ │ Redis │
│Replica │ │Replica│
└────────┘ └───────┘
```

## Components

- **n8n Editor**: 2 replicas with session affinity for HA
- **n8n Workers**: 2 replicas for queue processing
- **PostgreSQL**: Primary-Replica setup for database HA
- **Redis**: Master-Replica with Sentinel for queue HA
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards

## Prerequisites

- Kubernetes cluster (Docker Desktop, minikube, or cloud)
- kubectl configured
- At least 4GB RAM available

## Quick Start

### 1. Deploy Everything

```bash
chmod +x *.sh
./deploy.sh
```

This will deploy all components in the correct order.

### 2. Port Forward Services

In a new terminal:

```bash
./port-forward.sh
```

Keep this running. Access:
- **n8n**: http://localhost:5678 (use your n8n account credentials)
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090

### 3. Setup Grafana Dashboard

1. Open Grafana: http://localhost:3000
2. Login with admin/admin123
3. Go to Dashboards → Import
4. Upload `grafana-dashboard.json` or paste its contents
5. Select Prometheus as data source
6. Click Import

### 4. Run HA Tests

#### Test n8n Editor HA

```bash
./test-editor-ha.sh
```

This test:
- Deletes one editor pod
- Verifies auto-recovery
- Checks service connectivity
- **Watch Grafana** to see pod count drop and recover

#### Test PostgreSQL HA

```bash
./test-postgres-ha.sh
```

This test:
- Creates test data in primary
- Deletes primary pod
- Verifies new primary comes up
- Checks data persistence
- **Watch Grafana** to see database connection metrics

#### Test n8n Worker HA

```bash
./test-worker-ha.sh
```

This test:
- Verifies worker pod failover
- Checks Redis queue connectivity
- Creates and executes a test workflow
- Deletes worker pod during execution
- Verifies jobs continue processing
- **Watch Grafana** to see worker pod metrics and queue status

#### Test Redis HA

```bash
./test-redis-ha.sh
```

This test:
- Sets test data in master
- Deletes master pod
- Verifies new master (or replica promotion)
- Checks data persistence
- **Watch Grafana** to see Redis metrics and failover events

## Test Cases Overview

### n8n Editor HA Test

**What it tests:**
- Pod failure and auto-recovery
- Service availability during failover
- Session persistence

**Grafana Metrics to Watch:**
- Editor pod count (should drop to 1, then recover to 2)
- Editor pod status over time
- Service response times

### PostgreSQL HA Test

**What it tests:**
- Primary database failure
- Automatic pod restart
- Data persistence
- Service connectivity

**Grafana Metrics to Watch:**
- PostgreSQL primary status
- Database connections
- Query performance

### Redis HA Test

**What it tests:**
- Master node failure
- Automatic pod restart
- Data persistence (AOF)
- Sentinel failover (if configured)

**Grafana Metrics to Watch:**
- Redis master status
- Memory usage
- Failover events

## Monitoring Dashboard

The Grafana dashboard shows:

1. **Component Status**: Real-time status of all pods
2. **Editor Pods**: Count and status over time
3. **Worker Pods**: Count and status over time
4. **PostgreSQL**: Connection metrics
5. **Redis**: Memory usage and status
6. **All Pods Table**: Complete status overview

## Cleanup

To remove all resources:

```bash
./cleanup.sh
```

Or manually:

```bash
kubectl delete namespace n8n-ha
```

## Troubleshooting

### Pods Not Starting

```bash
kubectl get pods -n n8n-ha
kubectl describe pod <pod-name> -n n8n-ha
kubectl logs <pod-name> -n n8n-ha
```

### Services Not Accessible

```bash
kubectl get svc -n n8n-ha
kubectl get endpoints -n n8n-ha
```

### Grafana No Data

1. **Run verification script**: `./verify-prometheus.sh`
2. **Check Prometheus targets**: Port forward and visit http://localhost:9090/targets
3. **Verify RBAC**: Prometheus needs ServiceAccount with ClusterRole to discover pods
4. **Check Grafana datasource**: Visit http://localhost:3000/connections/datasources
5. **Test query in Grafana**: Go to Explore and try `up{namespace="n8n-ha"}`
6. **See detailed guide**: `GRAFANA_TROUBLESHOOTING.md`

### Database Connection Issues

**After cleanup and redeployment, if n8n cannot connect to PostgreSQL:**

1. **Run the automatic fix script** (recommended):
   ```bash
   ./fix-postgres-connection.sh
   ```

2. **Manual troubleshooting**:
   ```bash
   # Check PostgreSQL pod status
   kubectl get pods -n n8n-ha -l app=postgresql,role=primary
   
   # Verify PostgreSQL is ready
   kubectl exec -n n8n-ha postgresql-primary-0 -- pg_isready -U postgres
   
   # Check if database exists
   kubectl exec -n n8n-ha postgresql-primary-0 -- psql -U postgres -c "\l" | grep n8n
   
   # Restart n8n pods to force reconnection
   kubectl delete pods -n n8n-ha -l app=n8n-editor
   kubectl delete pods -n n8n-ha -l app=n8n-worker
   
   # Check n8n logs for database errors
   kubectl logs -n n8n-ha -l app=n8n-editor --tail=50 | grep -i "database\|postgres\|error"
   ```

3. **See detailed guide**: `POSTGRES_CONNECTION_FIX.md`

**Check Redis**:
```bash
kubectl exec -it -n n8n-ha <redis-pod> -- redis-cli ping
```

## Files

- `namespace.yaml` - Kubernetes namespace
- `postgresql-ha.yaml` - PostgreSQL primary-replica setup
- `redis-ha.yaml` - Redis master-replica with Sentinel
- `n8n-editor-ha.yaml` - n8n editor and worker deployments
- `monitoring.yaml` - Prometheus and Grafana
- `grafana-dashboard.json` - Grafana dashboard configuration
- `deploy.sh` - Automated deployment
- `port-forward.sh` - Port forwarding helper
- `test-editor-ha.sh` - Editor HA test
- `test-postgres-ha.sh` - PostgreSQL HA test
- `test-redis-ha.sh` - Redis HA test
- `cleanup.sh` - Cleanup script

## Notes

- This is a minimal POC setup for demonstration
- For production, consider:
  - Persistent volumes for data
  - Proper secrets management
  - SSL/TLS certificates
  - Network policies
  - Resource limits and requests
  - Backup strategies
  - More sophisticated HA (Patroni for PostgreSQL, Redis Cluster)

## Reference

Based on: https://lumadock.com/blog/tutorials/n8n-high-availability/
