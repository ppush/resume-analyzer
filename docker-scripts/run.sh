#!/bin/bash

# Script for running Resume Analyzer in Docker

echo "🚀 Starting Resume Analyzer in Docker..."

# Check that LM Studio is running
echo "🔍 Checking LM Studio availability..."
if curl -s http://localhost:1234/v1/models > /dev/null; then
    echo "✅ LM Studio available on localhost:1234"
else
    echo "⚠️  LM Studio not available on localhost:1234"
    echo "   Make sure LM Studio is running locally"
    echo "   or use docker-compose with LM Studio in container"
fi

# Create necessary folders
mkdir -p results logs

# Start container
docker-compose up --build

echo "🎉 Resume Analyzer finished!"
