#!/bin/bash
set -euo pipefail

APP_PORT="${1:?app port required}"
DB_NAME="${2:?db name required}"
APP_DIR="/opt/major_frontend"

if [ -z "${AWS_REGION:-}" ]; then
  echo "AWS_REGION is required"
  exit 1
fi

APP_SECRET_KEY="$(aws ssm get-parameter --name "/tomato/app/secret_key" --with-decryption --region "${AWS_REGION}" --query "Parameter.Value" --output text)"
DB_ROOT_PASSWORD="$(aws ssm get-parameter --name "/tomato/db/root_password" --with-decryption --region "${AWS_REGION}" --query "Parameter.Value" --output text)"

cat >"${APP_DIR}/.env" <<ENVFILE
APP_HOST_PORT=${APP_PORT}
SECRET_KEY=${APP_SECRET_KEY}
DB_HOST=db
DB_USER=root
DB_PASSWORD=${DB_ROOT_PASSWORD}
DB_NAME=${DB_NAME}
MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
MYSQL_DATABASE=${DB_NAME}
ENVFILE
