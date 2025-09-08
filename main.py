#!/usr/bin/env python3
"""
FastAPI application for resume analysis
"""

import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from services import read_resume_as_html_chunks, LLMConnectionError
from core import ResumeParser, BlockProcessor, ResumeResultAggregator

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('resume_analyzer.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Resume Analyzer", version="1.0")

# Component initialization
resume_parser = ResumeParser()
block_processor = BlockProcessor()
result_aggregator = ResumeResultAggregator()

@app.get("/health")
async def health_check():
    """Service health check"""
    return {"status": "healthy", "service": "resume-analyzer"}

@app.post("/analyze")
async def load_resume_html(file: UploadFile = File(...)):
    """
    Uploads and analyzes resume using HTML chunking for better structure preservation
    """
    try:
        # File validation
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not file.filename.lower().endswith(('.docx', '.pdf')):
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file format. Only DOCX and PDF are supported"
            )
        
        # Process resume file with HTML chunking
        
        # 1. Read as HTML chunks
        html_chunks = await read_resume_as_html_chunks(file)
        logger.info(f"Resume loaded as {len(html_chunks)} HTML chunks")
        
        # 2. Parse HTML chunks into blocks
        blocks = await resume_parser.parse_resume_from_html_chunks(html_chunks)
        logger.info(f"Resume parsed into {len(blocks)} blocks")
        
        # 3. Process blocks through LLM
        processed_results = await block_processor.process_blocks_parallel(blocks)
        logger.info("Blocks processed through LLM")
        
        # 4. Aggregate results
        final_result = await result_aggregator.aggregate_results(processed_results)
        logger.info("Results aggregated")
        
        return JSONResponse(content=final_result)
        
    except LLMConnectionError as e:
        logger.error(f"LLM connection error: {e}")
        raise HTTPException(status_code=503, detail=f"LLM service unavailable: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing resume with HTML chunking: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Resume Analyzer",
        "version": "1.0",
        "description": "AI-powered resume analysis service using LLM",
        "endpoints": {
            "/analyze": "POST - Upload and analyze resume with HTML chunking (DOCX/PDF)",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        }
    }
