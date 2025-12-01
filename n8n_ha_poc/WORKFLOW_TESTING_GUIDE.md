# n8n Workflow Testing & Monitoring Guide

This guide walks you through creating a workflow in n8n, verifying it's saved in PostgreSQL, checking logs, and connecting to Grafana for monitoring.

## 📋 Complete Workflow Overview

Here's the complete process from creating a workflow to monitoring it:

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Create Workflow in n8n Dashboard                        │
│ • Access http://localhost:5678                                  │
│ • Login: admin/admin123                                          │
│ • Create workflow with Manual Trigger + Set node                │
│ • Save workflow                                                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Verify in PostgreSQL                                     │
│ • Run: ./check-workflows.sh                                      │
│ • Or connect manually: kubectl exec -it <POD> -- psql -U n8n -d n8n │
│ • Query: SELECT * FROM workflow_entity;                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Check Logs                                              │
│ • Run: ./view-logs.sh editor -g "workflow"                       │
│ • Or: kubectl logs -n n8n-ha -l app=n8n-editor                  │
│ • Verify workflow save operations in logs                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Connect to Grafana                                      │
│ • Access http://localhost:3000                                  │
│ • Login: admin/admin123                                          │
│ • Configure Prometheus data source                               │
│ • Import grafana-dashboard.json                                  │
│ • Monitor n8n metrics                                            │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. Ensure all services are deployed and running:
   ```bash
   kubectl get pods -n n8n-ha
   ```

2. Start port forwarding (in a separate terminal):
   ```bash
   cd n8n_ha_poc
   ./port-forward.sh
   ```

## Quick Start - Helper Scripts

This guide includes helper scripts to make the process easier:

- **`./check-workflows.sh`** - Quickly check workflows in PostgreSQL
  ```bash
  ./check-workflows.sh                    # List all workflows
  ./check-workflows.sh "Test Workflow"    # Search for specific workflow
  ```

- **`./view-logs.sh`** - View logs from n8n components
  ```bash
  ./view-logs.sh editor -f                # Follow editor logs
  ./view-logs.sh worker -t 50            # Show last 50 worker log lines
  ./view-logs.sh editor -g "workflow"    # Search for 'workflow' in editor logs
  ./view-logs.sh all                      # Show all component logs
  ```

- **`./connect-postgresql.sh`** - Connect to PostgreSQL interactively
  ```bash
  ./connect-postgresql.sh    # Opens psql shell
  ```

- **`./check-redis-queue.sh`** - Check Redis queue status and job distribution
  ```bash
  ./check-redis-queue.sh              # Show queue statistics
  ./check-redis-queue.sh -m           # Monitor queue in real-time
  ./check-redis-queue.sh -c           # Check connection only
  ```

- **`./check-worker-jobs.sh`** - Check if workers are processing jobs
  ```bash
  ./check-worker-jobs.sh              # Check worker activity
  ./check-worker-jobs.sh -f           # Follow worker logs in real-time
  ```

- **`./setup-grafana-monitoring.sh`** - Setup Grafana monitoring for all components
  ```bash
  ./setup-grafana-monitoring.sh    # Updates Prometheus and provides setup instructions
  ```

- **`grafana-dashboard.json`** - Basic Grafana dashboard (see Step 4.3)
- **`grafana-dashboard-complete.json`** - Complete dashboard with all components (n8n, PostgreSQL, Redis)

> **📖 For detailed setup instructions, see [SETUP_GRAFANA_MONITORING.md](./SETUP_GRAFANA_MONITORING.md)**  
> **📖 For detailed Redis queue and worker verification, see [VERIFY_REDIS_QUEUE_AND_WORKERS.md](./VERIFY_REDIS_QUEUE_AND_WORKERS.md)**

## Step 1: Create a Workflow Manually in n8n Dashboard

### 1.1 Access n8n Dashboard

1. Open your browser and navigate to: **http://localhost:5678**
2. Login with credentials:
   - Username: `admin`
   - Password: `admin123`

### 1.2 Create a Simple Test Workflow

1. **Click "Add workflow"** button (top right) or use the "+" icon
2. **Add a Start Node**:
   - Click the "+" button in the canvas
   - Search for "Manual Trigger" or "Webhook"
   - Select "Manual Trigger" (for testing)
   - This node will be your workflow entry point

3. **Add a Test Node**:
   - Click the "+" button again
   - Search for "HTTP Request" or "Set"
   - Select "Set" node (to set some data)
   - Configure it:
     - Click "Add Value"
     - Name: `message`
     - Value: `Hello from n8n HA!`
     - Keep Value Type: `String`

4. **Add Another Node** (Optional):
   - Add "HTTP Request" node
   - Set Method: `GET`
   - Set URL: `https://httpbin.org/get`
   - This will make an external API call

5. **Connect the Nodes**:
   - Drag from the output of "Manual Trigger" to "Set" node
   - Drag from "Set" node to "HTTP Request" node (if you added it)

6. **Save the Workflow**:
   - Click "Save" button (top right)
   - Enter a workflow name: `Test Workflow - HA Verification`
   - Click "Save" again

7. **Test the Workflow**:
   - Click "Execute Workflow" button (top right)
   - Or click the "Play" button on the Manual Trigger node
   - You should see the execution results

### 1.3 Verify Workflow is Visible

- The workflow should appear in your workflow list
- Note the workflow ID (visible in the URL or workflow details)

## Step 2: Verify Workflow is Saved in PostgreSQL

> **📖 For detailed verification guide, see [VERIFY_WORKFLOWS_IN_DB.md](./VERIFY_WORKFLOWS_IN_DB.md)**

### 2.1 Connect to PostgreSQL Pod

**Quick Method (Using Helper Script):**
```bash
# Connect to PostgreSQL interactively
./connect-postgresql.sh
```

**Manual Method:**
```bash
# Get PostgreSQL pod (tries standard deployment first, then HA with role=primary)
POSTGRESQL_POD=$(kubectl get pods -n n8n-ha -l app=postgresql -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -z "$POSTGRESQL_POD" ]; then
    POSTGRESQL_POD=$(kubectl get pods -n n8n-ha -l app=postgresql,role=primary -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
fi

# Connect to PostgreSQL
kubectl exec -it -n n8n-ha $POSTGRESQL_POD -- psql -U n8n -d n8n
```

**Manual Method:**
```bash
# List PostgreSQL pods
kubectl get pods -n n8n-ha -l app=postgresql

# Connect to PostgreSQL (replace POD_NAME with actual pod name)
kubectl exec -it -n n8n-ha <POD_NAME> -- psql -U n8n -d n8n
```

**Alternative: Using PgBouncer service (if available)**
```bash
# Get PgBouncer pod
kubectl get pods -n n8n-ha -l app=pgbouncer

# Connect via PgBouncer
kubectl exec -it -n n8n-ha <PGBOUNCER_POD_NAME> -- psql -h localhost -p 6432 -U n8n -d n8n
```

### 2.2 Query Workflow Data

Once connected to PostgreSQL, run these queries:

```sql
-- List all workflows
SELECT id, name, active, "createdAt", "updatedAt" 
FROM workflow_entity 
ORDER BY "createdAt" DESC;

-- Get specific workflow details
SELECT id, name, active, nodes, connections, settings, "staticData"
FROM workflow_entity 
WHERE name LIKE '%Test Workflow%';

-- Count workflows
SELECT COUNT(*) as total_workflows FROM workflow_entity;

-- List recent workflows
SELECT id, name, active, "createdAt" 
FROM workflow_entity 
ORDER BY "createdAt" DESC 
LIMIT 10;

-- Check workflow executions
SELECT id, "workflowId", finished, mode, "startedAt", "stoppedAt"
FROM execution_entity
ORDER BY "startedAt" DESC
LIMIT 10;

-- Exit PostgreSQL
\q
```

### 2.3 Verify Workflow Persistence

**Quick Method (Using Helper Script):**
```bash
# Check all workflows
./check-workflows.sh

# Search for specific workflow
./check-workflows.sh "Test Workflow"
```

**Manual Method:**

1. **Check workflow exists**:
   ```bash
   kubectl exec -n n8n-ha <POSTGRESQL_POD> -- psql -U n8n -d n8n -c "SELECT id, name, active FROM workflow_entity WHERE name LIKE '%Test%';"
   ```

2. **Verify workflow data structure**:
   ```bash
   kubectl exec -n n8n-ha <POSTGRESQL_POD> -- psql -U n8n -d n8n -c "SELECT id, name, jsonb_pretty(nodes::jsonb) FROM workflow_entity LIMIT 1;"
   ```

## Step 3: Check Logs

### 3.1 View n8n Editor Logs

**Quick Method (Using Helper Script):**
```bash
# Follow editor logs in real-time
./view-logs.sh editor -f

# View last 100 lines
./view-logs.sh editor

# Search for workflow-related logs
./view-logs.sh editor -g "workflow"
```

**Manual Method:**

```bash
# List all n8n editor pods
kubectl get pods -n n8n-ha -l app=n8n-editor

# View logs from a specific pod
kubectl logs -n n8n-ha <POD_NAME> -f

# View logs from all editor pods
kubectl logs -n n8n-ha -l app=n8n-editor --tail=100

# View logs with timestamps
kubectl logs -n n8n-ha -l app=n8n-editor --tail=100 --timestamps
```

### 3.2 View n8n Worker Logs

**Quick Method (Using Helper Script):**
```bash
# Follow worker logs in real-time
./view-logs.sh worker -f

# View last 50 lines
./view-logs.sh worker -t 50

# Search for execution logs
./view-logs.sh worker -g "execution"
```

**Manual Method:**

```bash
# List all worker pods
kubectl get pods -n n8n-ha -l app=n8n-worker

# View logs from all workers
kubectl logs -n n8n-ha -l app=n8n-worker --tail=100

# Follow logs from a specific worker
kubectl logs -n n8n-ha <WORKER_POD_NAME> -f
```

### 3.3 Search for Workflow-Related Logs

```bash
# Search for workflow creation logs
kubectl logs -n n8n-ha -l app=n8n-editor | grep -i "workflow"

# Search for database operations
kubectl logs -n n8n-ha -l app=n8n-editor | grep -i "database\|postgres"

# Search for errors
kubectl logs -n n8n-ha -l app=n8n-editor | grep -i "error\|fail"
```

### 3.4 View PostgreSQL Logs

**Quick Method (Using Helper Script):**
```bash
# View PostgreSQL logs
./view-logs.sh postgresql

# Follow PostgreSQL logs
./view-logs.sh postgresql -f

# Search for n8n operations in PostgreSQL logs
./view-logs.sh postgresql -g "n8n"
```

**Manual Method:**
```bash
# Get PostgreSQL pod (tries standard deployment first, then HA with role=primary)
POSTGRESQL_POD=$(kubectl get pods -n n8n-ha -l app=postgresql -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -z "$POSTGRESQL_POD" ]; then
    POSTGRESQL_POD=$(kubectl get pods -n n8n-ha -l app=postgresql,role=primary -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
fi

# View PostgreSQL logs
kubectl logs -n n8n-ha $POSTGRESQL_POD -f

# Search for n8n database operations
kubectl logs -n n8n-ha $POSTGRESQL_POD | grep -i "n8n"
```

### 3.5 View All Component Logs at Once

```bash
# Create a script to view all logs
cat > /tmp/view-all-logs.sh << 'EOF'
#!/bin/bash
echo "=== n8n Editor Logs ==="
kubectl logs -n n8n-ha -l app=n8n-editor --tail=20
echo ""
echo "=== n8n Worker Logs ==="
kubectl logs -n n8n-ha -l app=n8n-worker --tail=20
echo ""
echo "=== PostgreSQL Logs ==="
POSTGRESQL_POD=$(kubectl get pods -n n8n-ha -l app=postgresql -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -z "$POSTGRESQL_POD" ]; then
    POSTGRESQL_POD=$(kubectl get pods -n n8n-ha -l app=postgresql,role=primary -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
fi
kubectl logs -n n8n-ha $POSTGRESQL_POD --tail=20
EOF

chmod +x /tmp/view-all-logs.sh
/tmp/view-all-logs.sh
```

## Step 4: Connect to Grafana Dashboard

### 4.1 Access Grafana

1. Open your browser and navigate to: **http://localhost:3000**
2. Login with default credentials:
   - Username: `admin`
   - Password: `admin123`
3. You'll be prompted to change the password (optional - you can skip for testing)

### 4.2 Configure Prometheus Data Source

1. **Go to Configuration → Data Sources** (gear icon in left sidebar)
2. **Click "Add data source"**
3. **Select "Prometheus"**
4. **Configure the connection**:
   - URL: `http://prometheus:9090` (internal Kubernetes service)
   - Or if accessing from outside: `http://localhost:9090`
   - Click "Save & Test"
   - You should see "Data source is working"

### 4.3 Create a Dashboard for n8n Monitoring

#### Option A: Import Complete Dashboard (Recommended)

1. **Go to Dashboards → Import** (plus icon → Import)
2. **Import via JSON**:
   - Click "Upload JSON file"
   - Select `grafana-dashboard-complete.json` from the `n8n_ha_poc` directory
   - Or paste the JSON content from the file
3. **Configure the dashboard**:
   - Select Prometheus as the data source
   - Click "Import"
   - The dashboard will show:
     - **n8n Main Pods Status** - Status of all n8n main pods
     - **n8n Worker Pods Status** - Status of all worker pods
     - **PostgreSQL Status** - Database pod status
     - **Redis Status** - Cache pod status
     - **CPU Usage** - For n8n main, workers, PostgreSQL, and Redis
     - **Memory Usage** - For all components
     - **PostgreSQL Active Connections** - Database connection count
     - **Pod Restarts** - Track pod stability
     - **Network I/O** - Network traffic for all components

**Note:** The complete dashboard (`grafana-dashboard-complete.json`) includes monitoring for all components: n8n main, n8n workers, PostgreSQL, and Redis.

**Alternative:** Use `grafana-dashboard.json` for a basic dashboard with fewer panels.

#### Option B: Create Custom Dashboard Manually

1. **Create New Dashboard**:
   - Click "Dashboards" → "New Dashboard"
   - Click "Add visualization"

2. **Add Panel 1: n8n Editor Status**:
   - Data source: Prometheus
   - Query: `up{job="n8n-editor"}`
   - Visualization: Stat or Graph
   - Title: "n8n Editor Pods Status"

3. **Add Panel 2: n8n Worker Status**:
   - Query: `up{job="n8n-worker"}`
   - Title: "n8n Worker Pods Status"

4. **Add Panel 3: CPU Usage**:
   - Query: `rate(container_cpu_usage_seconds_total{pod=~"n8n-.*"}[5m])`
   - Title: "n8n CPU Usage"

5. **Add Panel 4: Memory Usage**:
   - Query: `container_memory_usage_bytes{pod=~"n8n-.*"}`
   - Title: "n8n Memory Usage"

6. **Add Panel 5: PostgreSQL Connections**:
   - Query: `pg_stat_database_numbackends{datname="n8n"}`
   - Title: "PostgreSQL Active Connections"

7. **Add Panel 6: Redis Status**:
   - Query: `redis_up`
   - Title: "Redis Status"

8. **Save Dashboard**:
   - Click "Save dashboard" (top right)
   - Enter dashboard name: "n8n HA Monitoring"
   - Click "Save"

### 4.4 Create Workflow-Specific Queries

To monitor workflow executions, add these panels:

1. **Workflow Execution Rate** (if n8n exposes this metric):
   ```promql
   rate(n8n_workflow_executions_total[5m])
   ```

2. **Active Workflows**:
   ```promql
   n8n_workflows_active
   ```

3. **Failed Executions**:
   ```promql
   rate(n8n_workflow_executions_failed_total[5m])
   ```

### 4.5 Set Up Alerts (Optional)

1. **Go to Alerting → Alert Rules** (bell icon)
2. **Create New Alert Rule**:
   - Name: "n8n Editor Down"
   - Query: `up{job="n8n-editor"} == 0`
   - Condition: Alert when value is below 1
   - Evaluation: Every 1 minute
   - Save

## Step 5: Complete Verification Workflow

### 5.1 End-to-End Test

1. **Create workflow** in n8n dashboard ✅
2. **Verify in PostgreSQL**:
   ```bash
   kubectl exec -n n8n-ha <POSTGRESQL_POD> -- psql -U n8n -d n8n -c "SELECT COUNT(*) FROM workflow_entity WHERE name LIKE '%Test%';"
   ```
   Should return: `1` (or more if you created multiple)

3. **Check logs for workflow save**:
   ```bash
   kubectl logs -n n8n-ha -l app=n8n-editor --tail=50 | grep -i "workflow\|save"
   ```

4. **Verify in Grafana**:
   - Check that n8n pods are showing as "up" (value = 1)
   - Monitor resource usage
   - Check for any alerts

### 5.2 Test Workflow Execution

1. **Execute the workflow** in n8n dashboard
2. **Check worker logs**:
   ```bash
   kubectl logs -n n8n-ha -l app=n8n-worker --tail=50 | grep -i "execution"
   ```

3. **Verify execution in PostgreSQL**:
   ```bash
   kubectl exec -n n8n-ha <POSTGRESQL_POD> -- psql -U n8n -d n8n -c "SELECT id, \"workflowId\", finished, mode FROM execution_entity ORDER BY \"startedAt\" DESC LIMIT 5;"
   ```

4. **Monitor in Grafana**:
   - Watch for execution metrics
   - Check CPU/Memory spikes during execution

## Troubleshooting

### Workflow Not Saving

1. **Check database connectivity**:
   ```bash
   kubectl logs -n n8n-ha -l app=n8n-editor | grep -i "database\|postgres\|error"
   ```

2. **Verify PostgreSQL is accessible**:
   ```bash
   kubectl exec -n n8n-ha <POSTGRESQL_POD> -- psql -U n8n -d n8n -c "SELECT 1;"
   ```

3. **Check PgBouncer connection**:
   ```bash
   kubectl logs -n n8n-ha -l app=pgbouncer
   ```

### Grafana Not Showing Data

1. **Verify Prometheus is scraping**:
   - Go to Prometheus: http://localhost:9090
   - Navigate to Status → Targets
   - Check that all targets are "UP"

2. **Check Prometheus data source**:
   - In Grafana: Configuration → Data Sources
   - Test the Prometheus connection

3. **Verify metrics are available**:
   - In Prometheus: Go to Graph
   - Try query: `up{job="n8n-editor"}`

### Logs Not Showing

1. **Check pod status**:
   ```bash
   kubectl get pods -n n8n-ha
   ```

2. **Check if pods are running**:
   ```bash
   kubectl describe pod <POD_NAME> -n n8n-ha
   ```

3. **Restart port forwarding**:
   ```bash
   ./stop-port-forward.sh
   ./port-forward.sh
   ```

## Quick Reference Commands

### Helper Scripts (Recommended)

```bash
# Check workflows in PostgreSQL
./check-workflows.sh                    # List all workflows
./check-workflows.sh "Test Workflow"    # Search for specific workflow

# View logs
./view-logs.sh editor -f                # Follow editor logs
./view-logs.sh worker -t 50             # Show last 50 worker log lines
./view-logs.sh editor -g "workflow"     # Search for 'workflow' in editor logs
./view-logs.sh all                      # Show all component logs
./view-logs.sh -h                       # Show help

# Port forwarding
./port-forward.sh                       # Start port forwarding
./stop-port-forward.sh                  # Stop port forwarding
```

### Manual Commands

```bash
# View all pods
kubectl get pods -n n8n-ha

# View n8n editor logs
kubectl logs -n n8n-ha -l app=n8n-editor -f

# View n8n worker logs
kubectl logs -n n8n-ha -l app=n8n-worker -f

# Connect to PostgreSQL (using helper script)
./connect-postgresql.sh

# Or manually
kubectl exec -it -n n8n-ha <POSTGRESQL_POD> -- psql -U n8n -d n8n

# Check workflow count
kubectl exec -n n8n-ha <POSTGRESQL_POD> -- psql -U n8n -d n8n -c "SELECT COUNT(*) FROM workflow_entity;"
```

## Next Steps

- Create more complex workflows
- Set up custom Grafana dashboards
- Configure alerting rules
- Test failover scenarios
- Monitor performance metrics

