# HA Test Cases Guide

This guide explains how to run each HA test case and what to observe in the Grafana dashboard.

## Prerequisites

1. Deploy the POC: `./deploy.sh`
2. Start port forwarding: `./port-forward.sh` (in a separate terminal)
3. Access Grafana: http://localhost:3000 (admin/admin123)
4. Import the dashboard from `grafana-dashboard.json` if not auto-provisioned

## Test Cases

### 1. n8n Editor HA Test

**Script:** `./test-editor-ha.sh`

**What it tests:**
- Pod failure and automatic recovery
- Service availability during failover
- Session persistence with load balancer
- **Workflow persistence after pod failure** (NEW)

**Test Steps:**
1. Verifies initial state (2 editor pods)
2. Checks n8n API accessibility (requires port-forwarding)
3. Creates a test workflow and saves it to the database
4. Deletes one editor pod
5. Waits for Kubernetes to automatically restart it
6. Verifies service connectivity
7. **Verifies the test workflow still exists after failover** (NEW)

**Prerequisites:**
- Port forwarding must be active: `./port-forward.sh` or `kubectl port-forward -n n8n-ha svc/n8n-editor 5678:5678`
- n8n API must be accessible at `http://localhost:5678`

**Grafana Metrics to Watch:**
- **n8n Editor Pods (Healthy)**: Should drop from 2 to 1, then recover to 2
- **n8n Editor Pod Status Over Time**: Graph showing pod status (1 = up, 0 = down)
- **All Pods Status**: Table showing all pods and their status

**Expected Behavior:**
- Pod count drops temporarily
- New pod starts automatically
- Service remains accessible throughout
- **Workflow persists in database and is accessible after failover** (NEW)
- Dashboard shows recovery in real-time

**Workflow Persistence Test:**
The test creates a simple workflow with:
- A Start node
- A Set node with a test message
- Saves it to PostgreSQL database

After pod failover, the test verifies:
- The workflow ID still exists
- The workflow can be retrieved via API
- Data persistence is maintained across pod restarts

This proves that:
- Database connectivity is maintained
- Workflows are stored persistently (not in pod memory)
- HA setup correctly handles stateful data

---

### 2. PostgreSQL HA Test

**Script:** `./test-postgres-ha.sh`

**What it tests:**
- Primary database pod failure
- Automatic pod restart
- Data persistence
- Service connectivity

**Test Steps:**
1. Creates test data in primary database
2. Deletes primary pod
3. Waits for new primary pod to start
4. Verifies data persistence
5. Tests database connectivity

**Grafana Metrics to Watch:**
- **PostgreSQL Primary Status**: Should drop to 0, then recover to 1
- **All Pods Status**: Shows PostgreSQL pod status changes
- **Database Connections**: May show connection drops during failover

**Expected Behavior:**
- Primary pod restarts automatically
- Data persists (if using persistent volumes)
- Service remains accessible
- Dashboard shows status recovery

**Note:** For a minimal POC, this tests pod restart. For true HA with automatic failover to replica, you would need Patroni or similar.

---

### 3. n8n Worker HA Test

**Script:** `./test-worker-ha.sh`

**What it tests:**
- Worker pod failure and automatic recovery
- Redis queue connectivity
- Worker process health
- **Job processing continuity during failover** (NEW)
- **Workflow execution persistence** (NEW)

**Test Steps:**
1. Verifies initial state (2 worker pods)
2. Checks Redis queue connectivity
3. Verifies worker processes are running
4. Creates a test workflow and triggers execution (if API accessible)
5. Monitors queue status (waiting/active/completed jobs)
6. Deletes one worker pod
7. Waits for Kubernetes to automatically restart it
8. Verifies worker process in new pod
9. Checks execution status after recovery
10. Verifies Redis connectivity maintained

**Prerequisites:**
- Port forwarding must be active: `./port-forward.sh` or `kubectl port-forward -n n8n-ha svc/n8n-editor 5678:5678`
- n8n API must be accessible at `http://localhost:5678` (for execution tests)
- Redis must be running and accessible

**Grafana Metrics to Watch:**
- **n8n Worker Pods (Healthy)**: Should drop from 2 to 1, then recover to 2
- **n8n Worker Pod Status Over Time**: Graph showing pod status (1 = up, 0 = down)
- **Redis Queue Metrics**: Queue length, active jobs, completed jobs
- **All Pods Status**: Table showing all pods and their status

**Expected Behavior:**
- Pod count drops temporarily
- New pod starts automatically
- Worker process starts in new pod
- Redis queue connectivity maintained
- **Jobs continue processing or are picked up by remaining workers** (NEW)
- **Executions complete successfully after recovery** (NEW)
- Dashboard shows recovery in real-time

**Queue Processing Test:**
The test creates and executes a workflow that:
- Gets queued in Redis
- Is picked up by a worker
- Executes successfully
- Results are stored in PostgreSQL

After worker pod failover, the test verifies:
- Remaining workers continue processing
- New worker can pick up jobs from queue
- Executions complete successfully
- Queue state is maintained

This proves that:
- Queue-based architecture works correctly
- Jobs are not lost during worker failures
- Multiple workers can share the queue
- HA setup maintains job processing continuity

---

### 4. Redis HA Test

**Script:** `./test-redis-ha.sh`

**What it tests:**
- Redis master pod failure
- Automatic pod restart
- Data persistence (AOF)
- Sentinel failover (if configured)

**Test Steps:**
1. Sets test data in Redis master
2. Deletes master pod
3. Waits for new master pod to start
4. Verifies data persistence
5. Checks Sentinel status

**Grafana Metrics to Watch:**
- **Redis Master Status**: Should drop to 0, then recover to 1
- **All Pods Status**: Shows Redis pod status changes
- **Redis Memory Usage**: May show changes during failover

**Expected Behavior:**
- Master pod restarts automatically
- Data persists (AOF enabled)
- Service remains accessible
- Dashboard shows status recovery

**Note:** For true HA with automatic failover, Sentinel would promote a replica. This POC tests pod restart.

---

## Running All Tests

To run all tests in sequence:

```bash
./run-all-tests.sh
```

This will:
1. Run editor HA test
2. Wait for you to review Grafana
3. Run PostgreSQL HA test
4. Wait for you to review Grafana
5. Run Redis HA test
6. Show final summary

## Grafana Dashboard Overview

The dashboard shows:

1. **Component Status Panels** (Top Row):
   - n8n Editor Pods count
   - n8n Worker Pods count
   - PostgreSQL Primary Status
   - Redis Master Status

2. **Time Series Graphs** (Middle):
   - Editor pod status over time
   - Worker pod status over time

3. **All Pods Table** (Bottom):
   - Complete status of all pods
   - Shows which pods are up/down

## Interpreting Results

### Successful HA Test:
- ✅ Pod count drops temporarily
- ✅ Pod count recovers automatically
- ✅ Service remains accessible
- ✅ Dashboard shows recovery within 30-60 seconds

### Failed HA Test:
- ❌ Pod doesn't restart
- ❌ Service becomes unavailable
- ❌ Dashboard shows persistent failures

## Troubleshooting

### Tests Fail Immediately:
- Check pods are running: `kubectl get pods -n n8n-ha`
- Check services: `kubectl get svc -n n8n-ha`
- Review pod logs: `kubectl logs <pod-name> -n n8n-ha`

### Grafana Shows No Data:
- Verify Prometheus is scraping: http://localhost:9090/targets
- Check n8n metrics endpoint: `kubectl exec -it <pod> -n n8n-ha -- curl localhost:5678/metrics`
- Restart Prometheus if needed: `kubectl delete pod -n n8n-ha -l app=prometheus`

### Pods Don't Recover:
- Check resource limits: `kubectl describe pod <pod-name> -n n8n-ha`
- Check events: `kubectl get events -n n8n-ha --sort-by='.lastTimestamp'`
- Verify cluster has resources: `kubectl top nodes`

## Next Steps

After running tests:
1. Review Grafana dashboards for each component
2. Verify service availability during failover
3. Check application logs for errors
4. Test with actual n8n workflows to ensure end-to-end functionality

