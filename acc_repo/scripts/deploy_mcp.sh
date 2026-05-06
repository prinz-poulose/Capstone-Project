#!/usr/bin/env bash
# Deploy the ACC MCP server to Cloud Run.
#
# Usage:
#   PROJECT_ID=my-gcp-project REGION=us-central1 ./scripts/deploy_mcp.sh
#
# Requires: gcloud CLI, authenticated (`gcloud auth login`) and a
# Firestore (Native mode) database in the same project.
set -euo pipefail

: "${PROJECT_ID:?PROJECT_ID env var is required}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-acc-mcp}"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE}:latest"

echo "==> Building image: ${IMAGE}"
gcloud builds submit \
  --project="${PROJECT_ID}" \
  --tag="${IMAGE}" \
  --file=mcp_server/Dockerfile \
  .

echo "==> Deploying to Cloud Run: ${SERVICE} (${REGION})"
gcloud run deploy "${SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --image="${IMAGE}" \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="USE_FIRESTORE=1,LOG_LEVEL=INFO" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --port=8080

URL="$(gcloud run services describe "${SERVICE}" --project="${PROJECT_ID}" --region="${REGION}" --format='value(status.url)')"
echo
echo "==> MCP server URL: ${URL}/sse"
echo "Set MCP_SERVER_URL=${URL}/sse before running the agents."
