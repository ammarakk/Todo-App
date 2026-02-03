#!/bin/bash
# Create Kafka Topics using Redpanda CLI

set -e

echo "Creating Kafka topics..."

# Wait for Redpanda to be ready
until docker exec redpanda rpk cluster health &> /dev/null; do
  echo "Waiting for Redpanda to be ready..."
  sleep 2
done

# Create topics
docker exec redpanda rpk topic create task-events -p 3 --replication-factor 1 || echo "Topic task-events may already exist"
docker exec redpanda rpk topic create reminders -p 3 --replication-factor 1 || echo "Topic reminders may already exist"
docker exec redpanda rpk topic create task-updates -p 3 --replication-factor 1 || echo "Topic task-updates may already exist"
docker exec redpanda rpk topic create audit-events -p 3 --replication-factor 1 || echo "Topic audit-events may already exist"

# List topics
echo "Topics created:"
docker exec redpanda rpk topic list

echo "Done!"
