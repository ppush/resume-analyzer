"""
Restructured aggregator for resume block processing results
"""

import logging
from typing import Dict, Any, List

from core.block_processor import BlockResult
from .skill_merger import SkillMerger
from .experience_analyzer import ExperienceAnalyzer
from .job_recommender import JobRecommender
from services.llm_client import LLMConnectionError

logger = logging.getLogger(__name__)


class ResumeResultAggregator:
    """Aggregator for forming final JSON from block processing results"""
    
    def __init__(self):
        self.skill_merger = SkillMerger()
        self.experience_analyzer = ExperienceAnalyzer()
        self.job_recommender = JobRecommender()
    
    async def aggregate_results(self, block_results: Dict[str, BlockResult], projects_content: str = None) -> Dict[str, Any]:
        """
        Forms final JSON from block processing results
        
        Args:
            block_results: Block processing results
            projects_content: Projects block content for experience analysis
            
        Returns:
            Dict[str, Any]: Final JSON result
        """
        try:
            logger.info("🚀 Starting results aggregation...")
            
            # Initialize final result
            final_result = {
                "skills": [],
                "roles": [],
                "location": "",
                "languages": [],
                "ready_to_remote": False,
                "ready_to_trip": False,
                "experience": "",
                "recommendations": []
            }
            
            # Collect data from block results
            collected_data = self._collect_block_data(block_results)
            
            # Merge skills through LLM to eliminate duplication
            logger.info("🔍 Merging skills through LLM...")
            merged_skills = await self.skill_merger.merge_skills(collected_data["skills"])
            
            # Analyze work experience
            logger.info("📊 Analyzing work experience...")
            experience_analysis = await self.experience_analyzer.analyze_experience(
                projects_content, 
                collected_data["experiences"], 
                collected_data["roles"]
            )
            
            # Update final result
            final_result.update({
                "skills": merged_skills,
                "roles": collected_data["roles"],
                "languages": collected_data["languages"],
                "location": collected_data["location"],
                "experience": experience_analysis,
                "ready_to_remote": collected_data["any_remote"],
                "ready_to_trip": collected_data["any_trip"]
            })

            # Get job recommendations
            if self.job_recommender:
                logger.info("💼 Getting job recommendations...")
                recommendations = await self.job_recommender.get_recommendations(final_result)
                final_result["recommendations"] = recommendations
            else:
                logger.warning("⚠️ LLM client not available, recommendations will not be obtained")
                final_result["recommendations"] = []
                        
            # Sort skills by score (descending)
            logger.info("📊 Sorting skills by score...")
            final_result["skills"] = self._sort_skills_by_score(final_result["skills"])
            
            logger.info("✅ Results aggregation completed")
            return final_result
            
        except LLMConnectionError as e:
            logger.error(f"LLM connection error during aggregation: {e}")
            raise LLMConnectionError(f"Results aggregation requires LLM: {e}")
        except Exception as e:
            logger.error(f"Error aggregating results: {e}")
            return self._create_error_result()
    
    def _collect_block_data(self, block_results: Dict[str, BlockResult]) -> Dict[str, Any]:
        """Collects data from block results"""
        try:
            all_skills = []
            all_roles = []
            all_languages = []
            all_locations = []
            all_experiences = []
            any_remote = False
            any_trip = False
            
            for block_name, result in block_results.items():
                if result.skills:
                    all_skills.extend(result.skills)
                if result.roles:
                    all_roles.extend(result.roles)
                if result.languages:
                    all_languages.extend(result.languages)
                if result.location:
                    all_locations.append(result.location)
                if result.experience:
                    all_experiences.append(result.experience)
                if result.ready_to_remote:
                    any_remote = True
                if result.ready_to_trip:
                    any_trip = True
            
            # Choose the most frequent location
            location = max(all_locations, key=all_locations.count) if all_locations else ""
            
            return {
                "skills": all_skills,
                "roles": all_roles,
                "languages": all_languages,
                "location": location,
                "experiences": all_experiences,
                "any_remote": any_remote,
                "any_trip": any_trip
            }
            
        except Exception as e:
            logger.error(f"Error collecting block data: {e}")
            return {
                "skills": [],
                "roles": [],
                "languages": [],
                "location": "",
                "experiences": [],
                "any_remote": False,
                "any_trip": False
            }
    
    def _sort_skills_by_score(self, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sorts skills by score in descending order"""
        try:
            if not skills:
                return []
            
            # Sort by score (descending)
            sorted_skills = sorted(skills, key=lambda x: x.get('score', 0), reverse=True)
            
            logger.info(f"Skills sorted by score (total: {len(sorted_skills)})")
            return sorted_skills
            
        except Exception as e:
            logger.error(f"Error sorting skills by score: {e}")
            return skills
    
    def _create_error_result(self) -> Dict[str, Any]:
        """Creates error result"""
        return {
            "skills": [],
            "roles": [],
            "location": "",
            "languages": [],
            "ready_to_remote": False,
            "ready_to_trip": False,
            "experience": "Error processing resume",
            "recommendations": [],
            "error": True
        }
    
    def get_aggregation_summary(self, final_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns aggregation summary
        
        Args:
            final_result: Final aggregation result
            
        Returns:
            Dict[str, Any]: Aggregation summary
        """
        try:
            skills_count = len(final_result.get("skills", []))
            roles_count = len(final_result.get("roles", []))
            languages_count = len(final_result.get("languages", []))
            
            return {
                "skills_count": skills_count,
                "roles_count": roles_count,
                "languages_count": languages_count,
                "location": final_result.get("location", ""),
                "ready_to_remote": final_result.get("ready_to_remote", False),
                "ready_to_trip": final_result.get("ready_to_trip", False),
                "experience": final_result.get("experience", ""),
                "has_error": final_result.get("error", False)
            }
            
        except Exception as e:
            logger.error(f"Error getting aggregation summary: {e}")
            return {
                "skills_count": 0,
                "roles_count": 0,
                "languages_count": 0,
                "location": "",
                "ready_to_remote": False,
                "ready_to_trip": False,
                "experience": "",
                "has_error": True
            }
