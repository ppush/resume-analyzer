#!/bin/bash

# Script for building Resume Analyzer Docker image

echo "🐳 Building Resume Analyzer Docker image..."

# Build image
docker build -t resume-analyzer:latest .

if [ $? -eq 0 ]; then
    echo "✅ Image built successfully!"
    echo "📦 Image name: resume-analyzer:latest"
    echo ""
    echo "🚀 To run use:"
    echo "   docker-compose up"
    echo "   or"
    echo "   docker run -it resume-analyzer:latest"
else
    echo "❌ Error building image!"
    exit 1
fi
