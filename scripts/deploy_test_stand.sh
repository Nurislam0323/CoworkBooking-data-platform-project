#!/usr/bin/env bash
set -euo pipefail
: "${DEPLOY_HOST:?DEPLOY_HOST is required}"
: "${DEPLOY_USER:=ubuntu}"
ssh -o StrictHostKeyChecking=no "$DEPLOY_USER@$DEPLOY_HOST" 'cd /opt/platform/repo && git pull && docker compose pull && docker compose up -d'
