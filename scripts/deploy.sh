#!/bin/bash

set -e

PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}

echo "🚀 Deploying Weaver to GCP"
echo "=========================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

echo "🔨 Building Docker images..."
docker build -t gcr.io/$PROJECT_ID/weaver-api:latest -f infra/docker/Dockerfile --target api .
docker build -t gcr.io/$PROJECT_ID/weaver-worker:latest -f infra/docker/Dockerfile --target worker .

echo ""
echo "📤 Pushing images to GCR..."
docker push gcr.io/$PROJECT_ID/weaver-api:latest
docker push gcr.io/$PROJECT_ID/weaver-worker:latest

echo ""
echo "🔐 Creating secrets (if not exists)..."
gcloud secrets create weaver-secrets --data-file=backend/.env --project=$PROJECT_ID || echo "Secrets already exist"

echo ""
echo "☁️  Deploying API to Cloud Run..."
gcloud run deploy weaver-api \
  --image gcr.io/$PROJECT_ID/weaver-api:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --project $PROJECT_ID

echo ""
echo "⚙️  Deploying workers..."
echo "Note: Workers should be deployed to GKE or Compute Engine"
echo "See infra/deploy/cloudrun.yaml for configuration"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Get the API URL:"
echo "  gcloud run services describe weaver-api --region $REGION --format 'value(status.url)'"

