#!/usr/bin/env python3
"""
SkillMerger - class for merging and deduplicating skills using LLM
"""

import json
import logging
from typing import List, Dict, Any, Optional, Union, TypedDict
from dataclasses import dataclass

from services.llm_client import query_llm
from core.prompts.skill_prompts import SkillPrompts

logger = logging.getLogger(__name__)


class SkillDict(TypedDict, total=False):
    """Type definition for skill dictionary structure"""
    name: str
    score: Union[int, float]
    category: Optional[str]
    description: Optional[str]


class MergedSkillDict(TypedDict):
    """Type definition for merged skill result"""
    name: str
    score: Union[int, float]


class SkillMerger:
    """
    Class for merging skills through LLM processing.
    
    This class provides functionality to merge and deduplicate skills by sending
    them to a Language Model (LLM) for intelligent analysis and combination.
    It handles various edge cases and provides fallback mechanisms for error handling.
    
    Attributes:
        skill_prompts: Instance of SkillPrompts for generating LLM prompts
        logger: Logger instance for debugging and error reporting
    """
    
    def __init__(self) -> None:
        """
        Initialize the SkillMerger.
        
        Creates a new instance with SkillPrompts for generating LLM prompts.
        """
        self.skill_prompts: SkillPrompts = SkillPrompts()
    
    async def merge_skills(self, skills: List[SkillDict]) -> List[MergedSkillDict]:
        """
        Merge skills through LLM to eliminate duplication.
        
        This method sends a list of skills to a Language Model (LLM) for intelligent
        analysis and merging. It identifies similar skills and combines them into
        unique, normalized representations while preserving the highest skill scores.
        
        Args:
            skills: List of skill dictionaries to merge. Each skill should have:
                   - name: str - Skill name/description
                   - score: Union[int, float] - Skill proficiency score
                   - category: Optional[str] - Skill category (optional)
                   - description: Optional[str] - Additional description (optional)
        
        Returns:
            List[MergedSkillDict]: List of merged, deduplicated skills with:
                - name: str - Normalized skill name
                - score: Union[int, float] - Highest score among similar skills
        
        Raises:
            No exceptions are raised. On error, returns original skills list.
        
        Examples:
            >>> skills = [
            ...     {"name": "Python", "score": 85},
            ...     {"name": "python programming", "score": 90},
            ...     {"name": "Java", "score": 75}
            ... ]
            >>> merger = SkillMerger()
            >>> merged = await merger.merge_skills(skills)
            >>> print(f"Merged {len(merged)} skills from {len(skills)} original")
            Merged 2 skills from 3 original
        """
        try:
            if not skills:
                logger.info("📝 No skills to merge")
                return []
            
            if len(skills) == 1:
                logger.info("📝 Only one skill, no merging required")
                return [{"name": skills[0]["name"], "score": skills[0]["score"], "merged_names": "", "merge_reason": ""}]
            
            logger.info(f"🔍 Merging {len(skills)} skills through LLM...")
            
            # Format skills list for LLM
            skills_text = self._format_skills_for_llm(skills)
            
            # Generate merge prompt
            prompt = self.skill_prompts.generate_skills_merge_prompt(skills_text)
            
            # Send request to LLM
            response = await query_llm(
                prompt,
                temperature=self.skill_prompts.get_temperature(),
                seed=self.skill_prompts.get_seed()
            )
            
            # Parse response
            logger.info(f"🔍 Received response from LLM: {len(response)} characters")
            logger.debug(f"LLM response: {response[:500]}...")
            
            merged_skills = self._parse_merged_skills(response)
            
            logger.info(f"✅ Merged into {len(merged_skills)} unique skills")
            return merged_skills
            
        except Exception as e:
            logger.error(f"Error merging skills: {e}")
            logger.warning("Returning original skills without merging")
            # Return original skills with empty fields for new attributes
            return [{"name": skill["name"], "score": skill["score"], "merged_names": "", "merge_reason": ""} for skill in skills]
    
    def _format_skills_for_llm(self, skills: List[SkillDict]) -> str:
        """
        Format skills for LLM processing.
        
        This method converts a list of skill dictionaries into a formatted text
        string that can be sent to the LLM for analysis and merging.
        
        Args:
            skills: List of skill dictionaries to format
        
        Returns:
            str: Formatted text representation of skills for LLM processing
        
        Example:
            >>> skills = [{"name": "Python", "score": 85}, {"name": "Java", "score": 75}]
            >>> formatted = merger._format_skills_for_llm(skills)
            >>> print(formatted)
            - Python (score: 85)
            - Java (score: 75)
        """
        try:
            formatted_skills: List[str] = []
            for skill in skills:
                name: str = skill.get('name', 'Unknown Skill')
                score: Union[int, float] = skill.get('score', 0)
                formatted_skills.append(f"- {name} (score: {score})")
            
            return "\n".join(formatted_skills)
            
        except Exception as e:
            logger.error(f"Error formatting skills for LLM: {e}")
            return str(skills)
    
    def _parse_merged_skills(self, response: str) -> List[MergedSkillDict]:
        """
        Parse LLM response with merged skills.
        
        This method processes the LLM response to extract merged skills. It first
        attempts to parse the response as JSON, and if that fails, it tries to
        clean the response and parse it again. It validates the structure and
        ensures the result is a list of skills.
        
        Args:
            response: Raw response string from LLM
        
        Returns:
            List[MergedSkillDict]: Parsed and validated list of merged skills
        
        Raises:
            ValueError: If LLM response is not a list of skills
        
        Example:
            >>> response = '[{"name": "Python", "score": 90}, {"name": "Java", "score": 75}]'
            >>> skills = merger._parse_merged_skills(response)
            >>> print(f"Parsed {len(skills)} skills")
            Parsed 2 skills
        """
        try:
            # First try to parse the original response
            try:
                original_data: Any = json.loads(response)
                # Check if the original response is a list
                if isinstance(original_data, list):
                    return self._validate_merged_skills(original_data)
                else:
                    error_msg: str = f"LLM returned non-list skills, got type: {type(original_data).__name__}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to clean the response
                pass
            
            # Clean response from extra text
            cleaned_response = self._clean_llm_response(response)
            
            # Parse cleaned JSON
            data = json.loads(cleaned_response)
            
            # Validate structure
            if isinstance(data, list):
                return self._validate_merged_skills(data)
            else:
                error_msg = f"LLM returned non-list skills, got type: {type(data).__name__}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from merged skills: {e}")
            logger.debug(f"Raw response: {response}")
            raise ValueError(f"Failed to parse JSON from merged skills: {e}")
        except Exception as e:
            logger.error(f"Error parsing merged skills: {e}")
            raise
    
    def _clean_llm_response(self, response: str) -> str:
        """Cleans LLM response from extra text"""
        # Remove markdown blocks
        if '```json' in response:
            # Extract JSON from markdown block
            start = response.find('```json') + 7
            end = response.find('```', start)
            if end != -1:
                response = response[start:end].strip()
        elif '```' in response:
            # Extract JSON from regular markdown block
            start = response.find('```') + 3
            end = response.find('```', start)
            if end != -1:
                response = response[start:end].strip()
        
        # Look for JSON array in response
        start = response.find('[')
        end = response.rfind(']') + 1
        
        if start != -1 and end != 0:
            return response[start:end]
        
        # If JSON is truncated (no closing bracket), try to complete it
        if start != -1 and end == 0:
            # Look for last comma and close JSON
            last_comma = response.rfind(',')
            if last_comma != -1:
                # Remove last comma and add closing bracket
                response = response[:last_comma] + ']'
                return response
        
        # If JSON not found, return original response
        return response
    
    def _validate_merged_skills(self, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validates merged skills"""
        try:
            validated_skills = []
            
            for skill in skills:
                if isinstance(skill, dict):
                    name = skill.get('name', '')
                    score = skill.get('score')
                    merged_names = skill.get('merged_names', '')
                    merge_reason = skill.get('merge_reason', '')
                    
                    # Check required fields - score must be present
                    if name and score is not None and isinstance(score, (int, float)):
                        # Normalize score
                        score = int(score)
                        score = max(0, min(100, score))  # Limit to 0-100
                        
                        validated_skills.append({
                            'name': str(name),
                            'score': score,
                            'merged_names': str(merged_names) if merged_names else '',
                            'merge_reason': str(merge_reason) if merge_reason else ''
                        })
                    else:
                        logger.warning(f"Invalid skill structure: {skill}")
                else:
                    logger.warning(f"Skill is not a dict: {skill}")
            
            return validated_skills
            
        except Exception as e:
            logger.error(f"Error validating merged skills: {e}")
            return []
    

    

