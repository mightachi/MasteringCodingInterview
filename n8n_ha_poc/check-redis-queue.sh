#!/bin/bash

# Script to check messages in Redis queue for n8n

set -e

NAMESPACE="n8n-ha"
REDIS_POD=$(kubectl get pods -n $NAMESPACE -l app=redis,role=master -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$REDIS_POD" ]; then
    echo "✗ Redis master pod not found"
    exit 1
fi

echo "=========================================="
echo "Redis Queue Inspector for n8n"
echo "=========================================="
echo ""
echo "Redis Pod: $REDIS_POD"
echo ""

# Function to run redis-cli command
redis_cmd() {
    kubectl exec -n $NAMESPACE $REDIS_POD -- redis-cli "$@" 2>/dev/null
}

# 1. List all Bull queue keys
echo "1. Bull Queue Keys:"
echo "--------------------------------------"
QUEUE_KEYS=$(redis_cmd KEYS "*bull*queue*" | grep -v "^$" || echo "")
if [ -n "$QUEUE_KEYS" ]; then
    echo "$QUEUE_KEYS" | while read key; do
        echo "  • $key"
    done
else
    echo "  No Bull queue keys found"
    echo "  (This is normal if no workflows are queued)"
fi
echo ""

# 2. Check for n8n-specific queue patterns
echo "2. n8n Queue Patterns:"
echo "--------------------------------------"
ALL_KEYS=$(redis_cmd KEYS "*" | grep -v "^$" || echo "")
if [ -n "$ALL_KEYS" ]; then
    echo "$ALL_KEYS" | grep -E "(bull|queue|n8n)" | head -20 | while read key; do
        KEY_TYPE=$(redis_cmd TYPE "$key")
        KEY_LEN=$(redis_cmd LLEN "$key" 2>/dev/null || redis_cmd ZCARD "$key" 2>/dev/null || redis_cmd HLEN "$key" 2>/dev/null || echo "N/A")
        echo "  • $key (type: $KEY_TYPE, items: $KEY_LEN)"
    done
else
    echo "  No keys found"
fi
echo ""

# 3. Check queue statistics
echo "3. Queue Statistics:"
echo "--------------------------------------"
# Common Bull queue key patterns
for pattern in "*bull*:wait" "*bull*:active" "*bull*:completed" "*bull*:failed" "*bull*:delayed"; do
    KEYS=$(redis_cmd KEYS "$pattern" 2>/dev/null | grep -v "^$" || echo "")
    if [ -n "$KEYS" ]; then
        echo "$KEYS" | while read key; do
            COUNT=$(redis_cmd ZCARD "$key" 2>/dev/null || redis_cmd LLEN "$key" 2>/dev/null || echo "0")
            if [ "$COUNT" != "0" ] && [ "$COUNT" != "" ]; then
                echo "  • $key: $COUNT items"
            fi
        done
    fi
done
echo ""

# 4. Show sample queue items
echo "4. Sample Queue Items (if any):"
echo "--------------------------------------"
WAIT_KEY=$(redis_cmd KEYS "*bull*:wait" 2>/dev/null | head -1 | grep -v "^$" || echo "")
if [ -n "$WAIT_KEY" ]; then
    COUNT=$(redis_cmd ZCARD "$WAIT_KEY" 2>/dev/null || echo "0")
    if [ "$COUNT" != "0" ] && [ "$COUNT" != "" ] && [ "$COUNT" != "N/A" ]; then
        echo "  Waiting queue: $WAIT_KEY"
        echo "  Items: $COUNT"
        echo "  Sample (first item):"
        redis_cmd ZRANGE "$WAIT_KEY" 0 0 WITHSCORES 2>/dev/null | head -2 || echo "    (Could not retrieve)"
    fi
fi

ACTIVE_KEY=$(redis_cmd KEYS "*bull*:active" 2>/dev/null | head -1 | grep -v "^$" || echo "")
if [ -n "$ACTIVE_KEY" ]; then
    COUNT=$(redis_cmd ZCARD "$ACTIVE_KEY" 2>/dev/null || echo "0")
    if [ "$COUNT" != "0" ] && [ "$COUNT" != "" ] && [ "$COUNT" != "N/A" ]; then
        echo "  Active queue: $ACTIVE_KEY"
        echo "  Items: $COUNT"
    fi
fi
echo ""

# 5. Redis Info
echo "5. Redis Information:"
echo "--------------------------------------"
redis_cmd INFO memory | grep -E "used_memory_human|used_memory_peak_human" || echo "  (Info not available)"
redis_cmd INFO clients | grep -E "connected_clients" || echo "  (Info not available)"
echo ""

# 6. Instructions
echo "=========================================="
echo "Manual Commands"
echo "=========================================="
echo ""
echo "To connect to Redis directly:"
echo "  kubectl exec -it -n $NAMESPACE $REDIS_POD -- redis-cli"
echo ""
echo "Useful Redis commands:"
echo "  KEYS *bull*              - List all Bull queue keys"
echo "  KEYS *bull*:wait         - List waiting queues"
echo "  KEYS *bull*:active      - List active queues"
echo "  ZCARD <key>             - Count items in sorted set"
echo "  LLEN <key>              - Count items in list"
echo "  ZRANGE <key> 0 -1       - View all items in sorted set"
echo "  LRANGE <key> 0 -1       - View all items in list"
echo "  TYPE <key>              - Check data type"
echo "  GET <key>               - Get string value"
echo ""
echo "To monitor queue in real-time:"
echo "  kubectl exec -it -n $NAMESPACE $REDIS_POD -- redis-cli MONITOR"
echo ""
echo "To clear all queues (CAUTION - deletes all data):"
echo "  kubectl exec -n $NAMESPACE $REDIS_POD -- redis-cli FLUSHALL"
echo ""


