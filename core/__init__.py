"""
Core module for resume analysis
"""

# Core classes
from .experience_calculator import ExperienceCalculator, ProjectPeriod
from .resume_parser import ResumeParser
from .block_processor import BlockProcessor, BlockResult

# Aggregation
from .aggregation.resume_result_aggregator import ResumeResultAggregator
from .aggregation.skill_merger import SkillMerger
from .aggregation.experience_analyzer import ExperienceAnalyzer

# Prompts
from .prompts.prompt_base import PromptBase
from .prompts.project_prompts import ProjectPrompts
from .prompts.language_prompts import LanguagePrompts
from .prompts.skill_prompts import SkillPrompts
from .prompts.parsing_prompts import ParsingPrompts
from .prompts.job_recommendation_prompts import JobRecommendationPrompts

__all__ = [
    # Core classes
    'ExperienceCalculator',
    'ProjectPeriod',
    'ResumeParser',
    'BlockProcessor',
    'BlockResult',
    
    # Aggregation
    'ResumeResultAggregator',
    'SkillMerger',
    'ExperienceAnalyzer',
    
    # Prompts
    'PromptBase',
    'ProjectPrompts',
    'LanguagePrompts',
    'SkillPrompts',
    'ParsingPrompts',
    'JobRecommendationPrompts'
]
