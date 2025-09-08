#!/bin/bash

# Script for running Resume Analyzer in development mode

echo "🛠️  Starting Resume Analyzer in development mode..."

# Create necessary folders
mkdir -p results logs

# Start development container
docker-compose -f docker-compose.dev.yml up --build

echo "🎉 Development container finished!"
