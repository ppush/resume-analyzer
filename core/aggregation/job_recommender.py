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
    
    def _extract_essential_data(self, resume_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract essential data from resume analysis for job recommendations
        
        Args:
            resume_analysis: Complete resume analysis result
            
        Returns:
            Dict with essential data for job recommendations
        """
        # Extract ALL skills (sorted by score)
        all_skills = sorted(
            resume_analysis.get('skills', []), 
            key=lambda x: x.get('score', 0), 
            reverse=True
        )
        
        # Extract top 10 roles
        top_roles = resume_analysis.get('roles', [])[:10]
        
        # Extract essential info
        essential_data = {
            "all_skills": [
                {
                    "name": skill.get('name', ''),
                    "score": skill.get('score', 0)
                }
                for skill in all_skills
            ],
            "top_roles": [
                {
                    "title": role.get('title', ''),
                    "project": role.get('project', ''),
                    "duration": role.get('duration', '')
                }
                for role in top_roles
            ],
            "experience": resume_analysis.get('experience', ''),
            "location": resume_analysis.get('location', ''),
            "ready_to_remote": resume_analysis.get('ready_to_remote', False),
            "ready_to_trip": resume_analysis.get('ready_to_trip', False)
        }
        
        return essential_data

    def _generate_optimized_prompt(self, essential_data: Dict[str, Any]) -> str:
        """
        Generate optimized prompt with all skills and top 10 roles
        
        Args:
            essential_data: Essential resume data
            
        Returns:
            Optimized LLM prompt
        """
        # Format all skills (show top 20 for brevity, but mention total count)
        all_skills = essential_data['all_skills']
        skills_display = ', '.join([f"{s['name']} ({s['score']})" for s in all_skills[:20]])
        if len(all_skills) > 20:
            skills_display += f" ... and {len(all_skills) - 20} more skills"
        
        # Format top 10 roles
        top_roles = essential_data['top_roles']
        roles_display = ', '.join([f"{r['title']} at {r['project']}" for r in top_roles[:5]])
        if len(top_roles) > 5:
            roles_display += f" ... and {len(top_roles) - 5} more roles"
        
        return f"""You are an expert HR consultant. Based on this candidate's comprehensive profile, recommend 5-7 job positions.

CANDIDATE PROFILE:
- All Skills ({len(all_skills)} total): {skills_display}
- Top Roles ({len(top_roles)} total): {roles_display}
- Experience: {essential_data['experience']}
- Location: {essential_data['location']}
- Remote Ready: {essential_data['ready_to_remote']}
- Travel Ready: {essential_data['ready_to_trip']}

TASK: Recommend job positions where this candidate would excel based on their complete skill set and experience.

OUTPUT FORMAT - Return ONLY valid JSON:
{{
  "recommendations": [
    {{
      "title": "Job Title",
      "score": 85,
      "category": ["Primary Category"],
      "reason": "Brief explanation"
    }}
  ]
}}

CRITICAL: Return ONLY the JSON object. No additional text, no markdown."""

    async def get_recommendations(self, resume_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get job recommendations based on resume analysis using optimized data.
        
        Args:
            resume_analysis: Complete resume analysis result
            
        Returns:
            List of job recommendations with scores and reasons
        """
        try:
            # Extract only essential data to reduce payload size
            essential_data = self._extract_essential_data(resume_analysis)
            
            # Generate optimized prompt
            prompt = self._generate_optimized_prompt(essential_data)
            
            logger.info(f"Optimized prompt size: {len(prompt)} characters")
            logger.info(f"Original data size: {len(json.dumps(resume_analysis))} characters")
            logger.info(f"Optimized data size: {len(json.dumps(essential_data))} characters")
            
            # Get response from LLM using global client
            response = await query_llm(prompt, temperature=0.3)
            
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
                return []  # Return empty list instead of raising exception
                
        except Exception as e:
            logger.error(f"Error getting job recommendations: {e}")
            return []  # Return empty list instead of raising exception
    
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
    
