"""
Job recommendation system using LLM analysis.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from services import query_llm
from core.prompts.job_recommendation_prompts import JobRecommendationPrompts

logger = logging.getLogger(__name__)


class JobRecommender:
    """
    Generates job recommendations based on resume analysis using LLM.
    """
    
    def __init__(self):
        """
        Initialize the job recommender.
        Uses global LLM client from services.
        """
        self.prompts = JobRecommendationPrompts()
    
    async def get_recommendations(self, resume_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get job recommendations based on resume analysis.
        
        Args:
            resume_analysis: Complete resume analysis result
            
        Returns:
            List of job recommendations with scores and reasons
        """
        try:
            # Convert resume analysis to JSON string for the prompt
            resume_json = json.dumps(resume_analysis, ensure_ascii=False, indent=2)
            
            # Generate prompt for job recommendations
            prompt = self.prompts.generate_job_recommendations_prompt(resume_json)
            
            # Get response from LLM using global client
            response = await query_llm(prompt)
            
            # Log the raw LLM response for debugging
            logger.info(f"Raw LLM response length: {len(response)}")
            logger.debug(f"Raw LLM response: {response[:500]}...")  # First 500 chars
            
            # Parse the response
            recommendations = self._parse_recommendations_response(response)
            
            if recommendations:
                logger.info(f"Generated {len(recommendations)} job recommendations")
                return recommendations
            else:
                logger.error("Failed to parse job recommendations from LLM response")
                raise ValueError("Failed to parse job recommendations from LLM response")
                
        except Exception as e:
            logger.error(f"Error getting job recommendations: {e}")
            raise e
    
    def _parse_recommendations_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response to extract job recommendations.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed list of recommendations or empty list if parsing fails
        """
        logger.info(f"Attempting to parse LLM response...")
        
        try:
            # First, try to extract JSON from markdown code blocks
            if '```json' in response:
                logger.info("Found markdown JSON block, extracting...")
                start_marker = '```json'
                end_marker = '```'
                
                start_idx = response.find(start_marker) + len(start_marker)
                end_idx = response.find(end_marker, start_idx)
                
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx].strip()
                    logger.info(f"Extracted JSON from markdown: {len(json_str)} chars")
                    logger.debug(f"Markdown JSON: {json_str[:300]}...")
                    
                    data = json.loads(json_str)
                    if 'recommendations' in data and isinstance(data['recommendations'], list):
                        logger.info(f"Successfully parsed {len(data['recommendations'])} recommendations from markdown")
                        return data['recommendations']
            
            # Try to find JSON in the response (fallback method)
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            logger.info(f"JSON boundaries: start={start_idx}, end={end_idx}")
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                logger.info(f"Extracted JSON string length: {len(json_str)}")
                logger.debug(f"Extracted JSON: {json_str[:300]}...")
                
                data = json.loads(json_str)
                
                if 'recommendations' in data and isinstance(data['recommendations'], list):
                    logger.info(f"Successfully parsed {len(data['recommendations'])} recommendations")
                    return data['recommendations']
                else:
                    logger.warning(f"JSON parsed but no 'recommendations' field found. Keys: {list(data.keys())}")
            
            # If no valid JSON found, try to extract from the entire response
            logger.info("Trying to parse entire response as JSON...")
            data = json.loads(response)
            if 'recommendations' in data and isinstance(data['recommendations'], list):
                logger.info(f"Successfully parsed entire response: {len(data['recommendations'])} recommendations")
                return data['recommendations']
                
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse recommendations JSON: {e}")
            logger.debug(f"Raw response: {response}")
        except Exception as e:
            logger.error(f"Unexpected error during parsing: {e}")
            logger.debug(f"Raw response: {response}")
        
        logger.warning("Failed to parse any recommendations from LLM response")
        return []
    
