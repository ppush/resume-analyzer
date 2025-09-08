#!/usr/bin/env python3
"""
Script for running Resume Analyzer service
"""

import uvicorn
import logging
from main import app

if __name__ == "__main__":
    # Logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('resume_analyzer.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Resume Analyzer service...")
    
    # Start service
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

