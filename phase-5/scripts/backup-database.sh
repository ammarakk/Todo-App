#!/bin/bash
# Database Backup Script for Phase 5
# Backs up PostgreSQL database to S3-compatible storage
#
# Usage: ./backup-database.sh [snapshot|continuous]
#

set -e

# Configuration
BACKUP_TYPE=${1:-snapshot}
NAMESPACE="phase-5"
DB_DEPLOYMENT="postgres"
BACKUP_DIR="/tmp/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="todo-app-backup-${TIMESTAMP}"

# S3 Configuration (update with your values)
S3_BUCKET="s3://todo-app-backups"
S3_ENDPOINT="${S3_ENDPOINT:-https://s3.amazonaws.com}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Todo App Database Backup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Get PostgreSQL pod name
DB_POD=$(kubectl get pod -n ${NAMESPACE} -l app=${DB_DEPLOYMENT} -o jsonpath='{.items[0].metadata.name}')

if [ -z "${DB_POD}" ]; then
    echo -e "${RED}Error: PostgreSQL pod not found${NC}"
    exit 1
fi

echo -e "${YELLOW}Database Pod: ${DB_POD}${NC}"
echo -e "${YELLOW}Backup Type: ${BACKUP_TYPE}${NC}"
echo ""

case $BACKUP_TYPE in
  snapshot)
    echo -e "${YELLOW}Creating snapshot backup...${NC}"

    # Create database dump
    kubectl exec -n ${NAMESPACE} ${DB_POD} -- pg_dumpall -U postgres | gzip > "${BACKUP_DIR}/${BACKUP_NAME}.sql.gz"

    # Upload to S3
    echo -e "${YELLOW}Uploading to S3...${NC}"
    aws s3 cp "${BACKUP_DIR}/${BACKUP_NAME}.sql.gz" "${S3_BUCKET}/snapshots/" --endpoint-url "${S3_ENDPOINT}"

    # Cleanup local file
    rm "${BACKUP_DIR}/${BACKUP_NAME}.sql.gz"

    echo -e "${GREEN}✓ Snapshot backup complete: ${BACKUP_NAME}${NC}"
    ;;

  continuous)
    echo -e "${YELLOW}Setting up continuous backup (WAL archiving)...${NC}"

    # This enables WAL archiving for point-in-time recovery
    kubectl exec -n ${NAMESPACE} ${DB_POD} -- bash -c "
      echo 'archive_mode = on' >> /etc/postgresql/postgresql.conf
      echo 'archive_command = \"aws s3 cp %p ${S3_BUCKET}/wal/%f\"' >> /etc/postgresql/postgresql.conf
      psql -U postgres -c 'SELECT pg_reload_conf();'
    "

    echo -e "${GREEN}✓ Continuous backup (WAL archiving) enabled${NC}"
    ;;

  restore)
    RESTORE_FILE=${2}

    if [ -z "${RESTORE_FILE}" ]; then
      echo -e "${RED}Error: Please specify backup file to restore${NC}"
      echo "Usage: ./backup-database.sh restore <backup-file>"
      exit 1
    fi

    echo -e "${YELLOW}Restoring from backup: ${RESTORE_FILE}${NC}"
    echo -e "${RED}Warning: This will overwrite existing data!${NC}"
    read -p "Continue? (yes/no): " CONFIRM

    if [ "${CONFIRM}" != "yes" ]; then
      echo "Restore cancelled"
      exit 0
    fi

    # Download from S3
    aws s3 cp "${S3_BUCKET}/snapshots/${RESTORE_FILE}" "${BACKUP_DIR}/${RESTORE_FILE}" --endpoint-url "${S3_ENDPOINT}"

    # Restore database
    gunzip -c "${BACKUP_DIR}/${RESTORE_FILE}" | kubectl exec -i -n ${NAMESPACE} ${DB_POD} -- psql -U postgres

    # Cleanup
    rm "${BACKUP_DIR}/${RESTORE_FILE}"

    echo -e "${GREEN}✓ Restore complete${NC}"
    ;;

  list)
    echo -e "${YELLOW}Available backups:${NC}"
    aws s3 ls "${S3_BUCKET}/snapshots/" --endpoint-url "${S3_ENDPOINT}"
    ;;

  *)
    echo -e "${RED}Unknown backup type: ${BACKUP_TYPE}${NC}"
    echo "Usage: ./backup-database.sh [snapshot|continuous|restore|list]"
    exit 1
    ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
