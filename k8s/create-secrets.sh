#!/bin/bash
set -e

NAMESPACE="apps"

# Slack Credentials
kubectl create secret generic slack-credentials \
  --from-literal=bot-token="{SLACK_BOT_TOKEN}" \
  --from-literal=app-token="{SLACK_APP_TOKEN}" \
  --namespace=$NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

# Gateway Credentials
kubectl create secret generic gateway-credentials \
  --from-literal=client-id="{COGNITO_CLIENT_ID_1}" \
  --from-literal=client-secret="{COGNITO_CLIENT_SECRET_3}" \
  --namespace=$NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✓ Secrets created"
