"""
Base class for LLM prompt generation

This module provides an abstract base class for generating Language Model (LLM) prompts
with common functionality including validation, common instructions, and configuration
parameters for temperature and seed values.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PromptBase(ABC):
    """
    Abstract base class for LLM prompt generation.
    
    This class provides a foundation for generating prompts for Language Models (LLM)
    with common functionality including validation, common instructions, and configuration
    parameters. It enforces consistent prompt structure and validation across all
    prompt generators.
    
    Attributes:
        logger: Logger instance for debugging and error reporting
    """
    
    def __init__(self) -> None:
        """
        Initialize the PromptBase.
        
        Creates a new instance with logger for debugging and error reporting.
        """
        self.logger: logging.Logger = logger
    
    @abstractmethod
    def generate_prompt(self, **kwargs) -> str:
        """
        Generate prompt for LLM.
        
        This abstract method must be implemented by subclasses to generate
        specific prompts for different types of LLM tasks.
        
        Args:
            **kwargs: Keyword arguments specific to the prompt type.
                     Implementation details vary by subclass.
        
        Returns:
            str: Generated prompt string for LLM processing
        
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass
    
    def _add_common_instructions(self, prompt: str) -> str:
        """
        Add common instructions to prompt.
        
        This method appends standardized instructions to all prompts to ensure
        consistent behavior and output format from the LLM.
        
        Args:
            prompt: Base prompt string to enhance
        
        Returns:
            str: Enhanced prompt with common instructions appended
        
        Common Instructions:
            - Always return valid JSON
            - Do not add extra text before or after JSON
            - Be accurate and consistent
            - Follow all specified rules without exceptions
        """
        common_instructions: str = """
        
## IMPORTANT
- Always return valid JSON
- Do not add extra text before or after JSON
- Be accurate and consistent
- Follow all specified rules without exceptions
"""
        return prompt + common_instructions
    
    def _validate_prompt(self, prompt: str) -> bool:
        """
        Validate prompt correctness.
        
        This method performs basic validation on generated prompts to ensure
        they meet minimum requirements for length and content.
        
        Args:
            prompt: Prompt string to validate
        
        Returns:
            bool: True if prompt is valid, False otherwise
        
        Validation Rules:
            - Prompt must be at least 100 characters long
            - Prompt must contain "JSON" reference
            - Prompt must not be empty or whitespace-only
        """
        if not prompt or len(prompt.strip()) < 100:
            self.logger.warning("Prompt is too short")
            return False
        
        if "JSON" not in prompt.upper():
            self.logger.warning("Prompt does not contain JSON reference")
            return False
        
        return True
    
    def get_temperature(self) -> float:
        """
        Get temperature setting for LLM.
        
        Temperature controls the randomness of LLM responses. Lower values
        produce more deterministic, consistent outputs.
        
        Returns:
            float: Temperature value (0.0 for deterministic behavior)
        
        Note:
            Default implementation returns 0.0 for maximum consistency.
            Subclasses may override for different behavior.
        """
        return 0.0
    
    def get_seed(self) -> int:
        """
        Get seed value for LLM.
        
        Seed value ensures reproducible results from LLM calls when
        combined with low temperature settings.
        
        Returns:
            int: Seed value (42 for deterministic behavior)
        
        Note:
            Default implementation returns 42 for consistency.
            Subclasses may override for different behavior.
        """
        return 42
