# Quick Start Guide

Get the n8n HA POC running in 5 minutes!

## Step 1: Deploy Everything

```bash
./deploy.sh
```

Wait 2-3 minutes for all pods to be ready.

## Step 2: Port Forward Services

In a **new terminal**, run:

```bash
./port-forward.sh
```

Keep this running. You'll see:
- n8n: http://localhost:5678
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## Step 3: Setup Grafana Dashboard

1. Open http://localhost:3000
2. Login: `admin` / `admin123`
3. Go to **Dashboards** → **Import**
4. Upload `grafana-dashboard.json` or paste its contents
5. Select **Prometheus** as data source
6. Click **Import**

The dashboard should now show all components.

## Step 4: Run HA Tests

### Test n8n Editor HA

**Important**: Make sure port-forwarding is active before running this test!

```bash
./test-editor-ha.sh
```

**What it tests:**
- Pod failover and recovery
- Service connectivity
- **Workflow persistence** (creates a test workflow, deletes pod, verifies workflow still exists)

**Watch Grafana**: Editor pod count should drop to 1, then recover to 2.

**Note**: The workflow persistence test requires n8n API access. If port-forwarding is not active, the test will skip workflow verification but still test pod failover.

### Test PostgreSQL HA

```bash
./test-postgres-ha.sh
```

**Watch Grafana**: PostgreSQL primary status should drop to 0, then recover to 1.

### Test n8n Worker HA

**Important**: Make sure port-forwarding is active before running this test!

```bash
./test-worker-ha.sh
```

**What it tests:**
- Worker pod failover and recovery
- Redis queue connectivity
- **Job processing continuity** (creates workflow, triggers execution, deletes worker pod, verifies execution completes)
- Worker process health

**Watch Grafana**: Worker pod count should drop to 1, then recover to 2.

**Note**: The workflow execution test requires n8n API access. If port-forwarding is not active, the test will skip execution verification but still test pod failover and queue connectivity.

### Test Redis HA

```bash
./test-redis-ha.sh
```

**Watch Grafana**: Redis master status should drop to 0, then recover to 1.

### Run All Tests

```bash
./run-all-tests.sh
```

## Access Services

- **n8n Editor**: http://localhost:5678
  - Use your n8n account credentials
  - (Basic auth may be enabled - check deployment config)

- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin123`

- **Prometheus**: http://localhost:9090

## Cleanup

When done:

```bash
./cleanup.sh
```

Or press Ctrl+C in the port-forward terminal, then:

```bash
kubectl delete namespace n8n-ha
```

## Troubleshooting

**Pods not starting?**
```bash
kubectl get pods -n n8n-ha
kubectl describe pod <pod-name> -n n8n-ha
```

**Grafana no data?**
- Check Prometheus targets: http://localhost:9090/targets
- Verify n8n metrics: `kubectl exec -it <n8n-pod> -n n8n-ha -- curl localhost:5678/metrics`

**Port already in use?**
```bash
lsof -i :5678
lsof -i :3000
lsof -i :9090
```

## What to Watch in Grafana

During each test, watch for:
1. **Pod count changes** - Should drop then recover
2. **Status graphs** - Show pod up/down over time
3. **All pods table** - Complete status overview

See `TEST_GUIDE.md` for detailed test explanations.
