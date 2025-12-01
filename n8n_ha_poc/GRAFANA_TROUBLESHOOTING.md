# Grafana Troubleshooting Guide

## Issue: No Data in Grafana Dashboard

### Step 1: Verify Prometheus is Running

```bash
kubectl get pods -n n8n-ha -l app=prometheus
```

Should show: `1/1 Running`

### Step 2: Check Prometheus Targets

Port forward Prometheus:
```bash
kubectl port-forward -n n8n-ha svc/prometheus 9090:9090
```

Then visit: http://localhost:9090/targets

**Expected**: You should see targets for:
- `n8n-editor` (2 targets)
- `n8n-worker` (2 targets)
- `kubernetes-pods` (pods with prometheus.io/scrape annotation)

**If targets show as DOWN**:
- Check if pods are running: `kubectl get pods -n n8n-ha`
- Check if n8n metrics are enabled: `N8N_METRICS=true` in pod env
- Verify metrics endpoint: `kubectl exec -n n8n-ha <pod> -- wget -qO- http://localhost:5678/metrics`

### Step 3: Verify RBAC Permissions

Run the verification script:
```bash
./verify-prometheus.sh
```

This checks:
- ServiceAccount exists
- ClusterRole exists
- ClusterRoleBinding exists
- No errors in Prometheus logs

### Step 4: Check Grafana Datasource

Port forward Grafana:
```bash
kubectl port-forward -n n8n-ha svc/grafana 3000:3000
```

Then visit: http://localhost:3000/connections/datasources

**Expected**: 
- Datasource named "Prometheus"
- URL: `http://prometheus:9090`
- Status: Green (working)

**If datasource is missing or not working**:
1. Check datasource ConfigMap:
   ```bash
   kubectl get configmap -n n8n-ha grafana-datasources -o yaml
   ```
2. Restart Grafana:
   ```bash
   kubectl delete pod -n n8n-ha -l app=grafana
   ```

### Step 5: Test Prometheus Query in Grafana

1. Go to: http://localhost:3000/explore
2. Select "Prometheus" datasource
3. Try query: `up{namespace="n8n-ha"}`
4. Click "Run query"

**Expected**: Should return results showing pod status (1 = up, 0 = down)

**If no results**:
- Check time range (should be "Last 15 minutes" or similar)
- Verify Prometheus has data: http://localhost:9090/graph?g0.expr=up

### Step 6: Verify Dashboard Queries

The dashboard uses these queries:
- `count(up{job="n8n-editor"} == 1)` - Editor pod count
- `count(up{job="n8n-worker"} == 1)` - Worker pod count
- `up{job="n8n-editor"}` - Editor pod status over time
- `up{job="n8n-worker"}` - Worker pod status over time
- `up{namespace="n8n-ha"}` - All pods status

Test each query in Grafana Explore to see if they return data.

### Step 7: Check Prometheus Configuration

Verify Prometheus config:
```bash
kubectl exec -n n8n-ha <prometheus-pod> -- cat /etc/prometheus/prometheus.yml
```

Should show:
- `job_name: 'n8n-editor'`
- `job_name: 'n8n-worker'`
- `job_name: 'kubernetes-pods'`

### Step 8: Reload Prometheus Configuration

If you made changes to Prometheus config:
```bash
# Apply changes
kubectl apply -f monitoring.yaml

# Restart Prometheus
kubectl delete pod -n n8n-ha -l app=prometheus

# Wait for restart
kubectl wait --for=condition=ready pod -l app=prometheus -n n8n-ha --timeout=60s
```

### Common Issues

#### Issue: "No data points"
**Solution**: 
- Check time range in Grafana (top right)
- Verify Prometheus has data for that time range
- Check if targets are UP in Prometheus

#### Issue: "Datasource not found"
**Solution**:
- Check Grafana datasource ConfigMap
- Restart Grafana pod
- Manually add datasource in Grafana UI

#### Issue: "Query returned no data"
**Solution**:
- Verify the query syntax is correct
- Check if metrics exist: `up{namespace="n8n-ha"}`
- Verify job names match: `up{job="n8n-editor"}`

#### Issue: Prometheus can't discover pods
**Solution**:
- Verify RBAC is set up: `./verify-prometheus.sh`
- Check ServiceAccount is assigned to Prometheus pod
- Verify ClusterRoleBinding exists

### Quick Fix Script

Run this to fix common issues:

```bash
# Reapply monitoring config
kubectl apply -f monitoring.yaml

# Restart Prometheus
kubectl delete pod -n n8n-ha -l app=prometheus

# Restart Grafana
kubectl delete pod -n n8n-ha -l app=grafana

# Wait for pods
kubectl wait --for=condition=ready pod -l app=prometheus -n n8n-ha --timeout=60s
kubectl wait --for=condition=ready pod -l app=grafana -n n8n-ha --timeout=60s

# Verify
./verify-prometheus.sh
```

### Verification Checklist

- [ ] Prometheus pod is running
- [ ] No errors in Prometheus logs
- [ ] RBAC permissions are set up
- [ ] Prometheus has active targets
- [ ] Grafana pod is running
- [ ] Grafana datasource is configured
- [ ] Test query works in Grafana Explore
- [ ] Dashboard queries return data

### Getting Help

If issues persist:
1. Check Prometheus logs: `kubectl logs -n n8n-ha -l app=prometheus`
2. Check Grafana logs: `kubectl logs -n n8n-ha -l app=grafana`
3. Verify all pods are running: `kubectl get pods -n n8n-ha`
4. Check service endpoints: `kubectl get endpoints -n n8n-ha`
