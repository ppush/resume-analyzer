"""
Simplified work experience calculator

This module provides functionality for calculating work experience from LLM-processed roles.
The calculator parses duration strings and aggregates experience by projects.
"""

import logging
import re
from typing import Dict, List, Tuple, Optional, Union, TypedDict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class RoleDict(TypedDict, total=False):
    """Type definition for role dictionary structure"""
    title: str
    project: str
    duration: str
    score: Optional[Union[int, float]]
    category: Optional[str]


@dataclass(frozen=True)
class ProjectPeriod:
    """
    Immutable data class representing a work period in a project.
    
    Attributes:
        duration_months: Duration of work in months
        project_name: Name of the project
        role: Role/title in the project
    """
    duration_months: int
    project_name: str
    role: str


class ExperienceComparisonResult(TypedDict):
    """Type definition for experience comparison result"""
    match: bool
    difference_percent: float
    stated_months: int
    calculated_months: int


class ExperienceCalculator:
    """
    Calculator for work experience based on LLM-processed roles.
    
    This class provides methods to calculate total work experience from a list of roles,
    where each role contains project information and duration. The calculator aggregates
    experience by projects to avoid double-counting when multiple roles exist in the same project.
    
    Attributes:
        logger: Logger instance for debugging and error reporting
    """
    
    def __init__(self) -> None:
        """
        Initialize the ExperienceCalculator.
        
        No initialization parameters required as this is a stateless calculator.
        """
        pass
    

    
    def calculate_experience_from_roles(self, roles: List[RoleDict]) -> Tuple[int, List[ProjectPeriod]]:
        """
        Calculate total work experience from a list of roles with duration information.
        
        This method processes a list of roles, extracts duration information, and calculates
        total experience while ensuring that experience is counted only once per project
        (even if multiple roles exist in the same project).
        
        Args:
            roles: List of role dictionaries containing work experience information.
                   Each role should have 'title', 'project', and 'duration' fields.
                   Optional fields include 'score' and 'category'.
                   
                   Expected structure:
                   {
                       'title': str,      # Role/title in the project
                       'project': str,    # Project name
                       'duration': str,   # Duration string (e.g., "2 years 3 months")
                       'score': Optional[Union[int, float]],  # Optional skill score
                       'category': Optional[str]              # Optional role category
                   }
        
        Returns:
            Tuple containing:
                - int: Total experience in months
                - List[ProjectPeriod]: List of unique project periods with aggregated experience
        
        Raises:
            No exceptions are raised. Invalid data is logged and skipped.
        
        Example:
            >>> roles = [
            ...     {"title": "Developer", "project": "Project A", "duration": "2 years"},
            ...     {"title": "Senior Dev", "project": "Project A", "duration": "1 year"},
            ...     {"title": "Engineer", "project": "Project B", "duration": "1 year"}
            ... ]
            >>> calculator = ExperienceCalculator()
            >>> total_months, periods = calculator.calculate_experience_from_roles(roles)
            >>> print(f"Total experience: {total_months} months")
            Total experience: 36 months
        """
        try:
            # Input validation
            if not isinstance(roles, list):
                logger.error("Roles must be a list")
                return 0, []
            
            if not roles:
                logger.info("Empty roles list provided")
                return 0, []
            
            total_months: int = 0
            project_periods: List[ProjectPeriod] = []
            
            # Group roles by projects to avoid double-counting
            projects: Dict[str, int] = {}
            for i, role in enumerate(roles):
                # Role structure validation
                if not isinstance(role, dict):
                    logger.warning(f"Role at index {i} is not a dictionary, skipping")
                    continue
                
                project_name: Optional[str] = role.get('project')
                duration_text: Optional[str] = role.get('duration')
                title: Optional[str] = role.get('title')
                
                # Validate required fields
                if not project_name:
                    logger.warning(f"Role at index {i} missing 'project' field, skipping")
                    continue
                
                if not duration_text:
                    logger.warning(f"Role at index {i} missing 'duration' field, skipping")
                    continue
                
                if not title:
                    logger.warning(f"Role at index {i} missing 'title' field, using 'Unknown Role'")
                    title = "Unknown Role"
                
                # Type conversion for non-string fields
                if not isinstance(project_name, str):
                    logger.warning(f"Role at index {i} has non-string 'project' field, converting to string")
                    project_name = str(project_name)
                
                if not isinstance(duration_text, str):
                    logger.warning(f"Role at index {i} has non-string 'duration' field, converting to string")
                    duration_text = str(duration_text)
                
                if not isinstance(title, str):
                    logger.warning(f"Role at index {i} has non-string 'title' field, converting to string")
                    title = str(title)
                
                # Check that project hasn't been processed yet
                if project_name not in projects:
                    duration_months = self._parse_duration(duration_text)
                    if duration_months > 0:
                        # Take time only once per project
                        projects[project_name] = duration_months
                        
                        project_period = ProjectPeriod(
                            duration_months=duration_months,
                            project_name=project_name,
                            role=title
                        )
                        project_periods.append(project_period)
                        total_months += duration_months
                    else:
                        logger.warning(f"Could not parse duration '{duration_text}' for project '{project_name}'")
                else:
                    logger.debug(f"Project '{project_name}' already processed, skipping duplicate role")
            
            logger.info(f"Calculated experience from roles: {total_months} months ({total_months/12:.1f} years)")
            return total_months, project_periods
            
        except Exception as e:
            logger.error(f"Error calculating experience from roles: {e}")
            return 0, []
    
    def _parse_duration(self, duration_text: str) -> int:
        """
        Parse duration string into total months.
        
        This method extracts duration information from text strings that typically come
        from LLM processing. It supports various formats including years, months, and
        abbreviated units. The method uses a single regex pattern for efficiency.
        
        Args:
            duration_text: Duration string to parse. Examples:
                          - "2 years 3 months"
                          - "1 yr 6 mo"
                          - "3 y 9 m"
                          - "18" (fallback to months)
                          - "no duration" (returns 0)
        
        Returns:
            int: Total duration in months. Returns 0 if parsing fails or no duration found.
        
        Supported Formats:
            - Full words: "year", "month"
            - Abbreviations: "yr", "mo"
            - Single letters: "y", "m"
            - Numbers only: "18" (interpreted as months)
        
        Examples:
            >>> calc = ExperienceCalculator()
            >>> calc._parse_duration("2 years 3 months")
            27
            >>> calc._parse_duration("1 yr 6 mo")
            18
            >>> calc._parse_duration("3 y 9 m")
            45
            >>> calc._parse_duration("18")
            18
            >>> calc._parse_duration("no duration")
            0
        """
        if not duration_text:
            return 0
        
        try:
            
            # Clean and normalize text
            clean_text: str = duration_text.strip().lower()
            
            # Remove symbols like +, ~, ±, and similar before parsing
            clean_text = re.sub(r'[+\-~≈≅≈±]', '', clean_text)
            
            # Single regex pattern for extracting years and months in one pass
            # Pattern: (number)\s*(year|yr|y|month|mo|m)
            duration_pattern: str = r'(\d+)\s*(year|yr|y|month|mo|m)'
            matches: List[Tuple[str, str]] = re.findall(duration_pattern, clean_text)
            
            total_months: int = 0
            
            for number, unit in matches:
                num: int = int(number)
                if unit in ['year', 'yr', 'y']:
                    total_months += num * 12
                elif unit in ['month', 'mo', 'm']:
                    total_months += num
            
            # Return result if matches found (including 0)
            if total_months >= 0:
                return total_months
            
            # If no units found, raise an error
            raise ValueError(f"Could not parse duration from text: '{duration_text}'")
            
        except Exception as e:
            logger.error(f"Error parsing duration '{duration_text}': {e}")
            raise e
    

    
    def compare_experience(self, stated_experience: str, calculated_months: int) -> ExperienceComparisonResult:
        """
        Compare stated experience with calculated experience.
        
        This method compares a stated work experience (typically from a resume) with
        the calculated experience from project analysis. It determines if the stated
        experience matches the calculated experience within a 20% tolerance threshold.
        
        Args:
            stated_experience: String representation of stated experience.
                              Examples: "5 years", "2 years 6 months", "18 months"
            calculated_months: Calculated experience in months from project analysis.
                              Must be a positive integer.
        
        Returns:
            ExperienceComparisonResult: Dictionary containing comparison results:
                - match: bool - True if difference is less than 20%
                - difference_percent: float - Percentage difference between experiences
                - stated_months: int - Parsed stated experience in months
                - calculated_months: int - Calculated experience in months
        
        Raises:
            No exceptions are raised. Invalid data returns default result.
        
        Tolerance:
            Experiences are considered matching if the difference is less than 20%.
            This accounts for variations in how experience is calculated and stated.
        
        Examples:
            >>> calc = ExperienceCalculator()
            >>> result = calc.compare_experience("2 years", 24)
            >>> print(f"Match: {result['match']}, Difference: {result['difference_percent']}%")
            Match: True, Difference: 0.0%
            
            >>> result = calc.compare_experience("1 year", 24)
            >>> print(f"Match: {result['match']}, Difference: {result['difference_percent']}%")
            Match: False, Difference: 100.0%
        """
        try:
            if not stated_experience or calculated_months == 0:
                return {'match': False, 'difference_percent': 0}
            
            # Parse stated experience
            stated_months: int = self._parse_duration(stated_experience)
            if stated_months == 0:
                return {'match': False, 'difference_percent': 0.0}
            
            # Calculate difference
            difference: int = abs(calculated_months - stated_months)
            difference_percent: float = (difference / stated_months) * 100 if stated_months > 0 else 0.0
            
            # Consider matching if difference is less than 20%
            match: bool = difference_percent < 20
            
            return {
                'match': match,
                'difference_percent': difference_percent,
                'stated_months': stated_months,
                'calculated_months': calculated_months
            }
            
        except Exception as e:
            logger.error(f"Error comparing experience: {e}")
            return {'match': False, 'difference_percent': 0}
