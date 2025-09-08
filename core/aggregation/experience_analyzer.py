"""
Experience analysis module

This module provides comprehensive analysis of work experience from multiple sources,
including project content, stated experience, and role-based calculations. It implements
business logic for determining the final experience display format based on comparison
between stated and calculated experience.
"""

import logging
from typing import Dict, List, Any, Optional, Union, TypedDict

from core.experience_calculator import ExperienceCalculator, ProjectPeriod

logger = logging.getLogger(__name__)


class RoleDict(TypedDict, total=False):
    """Type definition for role dictionary structure"""
    title: str
    project: str
    duration: str
    score: Optional[Union[int, float]]
    category: Optional[str]


class ExperienceComparisonResult(TypedDict):
    """Type definition for experience comparison result"""
    match: bool
    difference_percent: float
    stated_months: int
    calculated_months: int


class ExperienceAnalyzer:
    """
    Class for comprehensive work experience analysis.
    
    This class analyzes work experience from multiple sources including project content,
    stated experience from resumes, and role-based duration calculations. It implements
    business logic for determining the final experience display format based on
    comparison between stated and calculated experience with configurable tolerance.
    
    Attributes:
        experience_calculator: Instance of ExperienceCalculator for duration calculations
        logger: Logger instance for debugging and error reporting
    """
    
    def __init__(self) -> None:
        """
        Initialize the ExperienceAnalyzer.
        
        Creates a new instance with ExperienceCalculator for duration calculations.
        """
        self.experience_calculator: ExperienceCalculator = ExperienceCalculator()
    
    async def analyze_experience(self, projects_content: str, all_experiences: List[str], all_roles: List[RoleDict]) -> str:
        """
        Analyze work experience from various sources.
        
        This method processes work experience from multiple sources including project content,
        stated experience from resumes, and role-based duration calculations. It implements
        business logic to determine the final experience display format based on comparison
        between stated and calculated experience.
        
        Args:
            projects_content: Content of projects block from resume parsing.
                            Currently not used for calculation (LLM processes projects).
            all_experiences: List of stated experience strings from resume.
                           Multiple entries may exist for different sections.
            all_roles: List of role dictionaries with duration information.
                      Each role should have 'title', 'project', and 'duration' fields.
        
        Returns:
            str: Formatted work experience string following business rules:
                 - If no stated experience: calculated experience only
                 - If stated experience matches calculated (within 20%): stated experience only
                 - If significant difference: "concret X | calculated Y" format
        
        Raises:
            No exceptions are raised. On error, returns error message string.
        
        Examples:
            >>> analyzer = ExperienceAnalyzer()
            >>> result = await analyzer.analyze_experience(
            ...     "Project A: 2 years", 
            ...     ["5 years"], 
            ...     [{"title": "Developer", "project": "A", "duration": "2 years"}]
            ... )
            >>> print(result)
            concret 5 years | calculated 2 years
        """
        try:
            logger.info("Analyzing work experience...")
            
            # Calculate experience from roles only (LLM already processes projects)
            roles_months, role_periods = self.experience_calculator.calculate_experience_from_roles(all_roles)
            
            # Analyze stated experience
            stated_experience = self._analyze_stated_experience(all_experiences)
            
            # Generate final analysis
            analysis = self._generate_experience_analysis(
                0, roles_months, stated_experience, [], role_periods
            )
            
            logger.info(f"Experience analysis completed: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing experience: {e}")
            return "Error analyzing work experience"
    
    def _analyze_stated_experience(self, all_experiences: List[str]) -> str:
        """
        Analyze stated experience from resume.
        
        This method processes a list of stated experience strings from different
        resume sections and returns the first valid (non-empty) experience entry.
        
        Args:
            all_experiences: List of stated experience strings from resume sections
        
        Returns:
            str: First valid stated experience string, or empty string if none found
        
        Examples:
            >>> experiences = ["", "5 years", "3 years"]
            >>> result = analyzer._analyze_stated_experience(experiences)
            >>> print(result)
            5 years
        """
        try:
            if not all_experiences:
                return ""
            
            # Take first non-empty experience
            for experience in all_experiences:
                if experience and experience.strip():
                    return experience.strip()
            
            return ""
            
        except Exception as e:
            logger.error(f"Error analyzing stated experience: {e}")
            return ""
    
    def _generate_experience_analysis(self, projects_months: int, roles_months: int, 
                                    stated_experience: str, project_periods: List[ProjectPeriod], 
                                    role_periods: List[ProjectPeriod]) -> str:
        """
        Generate final experience analysis according to business requirements.
        
        This method implements the business logic for determining the final experience
        display format based on comparison between stated and calculated experience.
        It follows specific rules for when to show stated vs calculated vs both.
        
        Args:
            projects_months: Total months from project analysis (currently unused)
            roles_months: Total months calculated from role durations
            stated_experience: String representation of stated experience
            project_periods: List of project periods (currently unused)
            role_periods: List of role periods with duration information
        
        Returns:
            str: Formatted experience string following business rules:
                 - If no stated experience: calculated experience only
                 - If stated experience matches calculated (within 20%): stated experience only
                 - If significant difference: "concret X | calculated Y" format
        
        Business Rules:
            - 20% tolerance threshold for considering experiences "matching"
            - Priority given to stated experience when close to calculated
            - Both values shown when significant difference exists
        """
        try:
            # Calculate calculated experience (from projects or roles)
            calculated_months = projects_months if projects_months > 0 else roles_months
            
            # Format calculated experience
            calculated_formatted = self._format_duration(calculated_months)
            
            # If no stated experience, return calculated
            if not stated_experience:
                return calculated_formatted
            
            # If stated experience exists, compare with calculated
            comparison = self.experience_calculator.compare_experience(stated_experience, calculated_months)
            
            # If experience matches or is close (difference < 20%), return only stated
            if comparison.get('match', False) or comparison.get('difference_percent', 100) < 20:
                return stated_experience
            
            # If experience differs significantly, return both
            return f"concret {stated_experience} | calculated {calculated_formatted}"
            
        except Exception as e:
            logger.error(f"Error generating experience analysis: {e}")
            return "Error generating experience analysis"
    
    def _format_duration(self, months: int) -> str:
        """
        Format duration in months to human readable format.
        
        This method converts a duration in months to a human-readable string format
        that displays years and months in a natural language format with proper
        pluralization.
        
        Args:
            months: Duration in months (must be non-negative integer)
        
        Returns:
            str: Human-readable duration string with proper pluralization
        
        Examples:
            >>> analyzer = ExperienceAnalyzer()
            >>> analyzer._format_duration(0)
            '0 months'
            >>> analyzer._format_duration(12)
            '1 year'
            >>> analyzer._format_duration(18)
            '1 year, 6 months'
            >>> analyzer._format_duration(24)
            '2 years'
            >>> analyzer._format_duration(30)
            '2 years, 6 months'
        
        Edge Cases:
            - 0 months: "0 months"
            - 1 month: "1 month"
            - 12 months: "1 year"
            - 13 months: "1 year, 1 month"
        """
        if months <= 0:
            return "0 months"
        
        years: int = months // 12
        remaining_months: int = months % 12
        
        if years > 0 and remaining_months > 0:
            year_text: str = "year" if years == 1 else "years"
            month_text: str = "month" if remaining_months == 1 else "months"
            return f"{years} {year_text}, {remaining_months} {month_text}"
        elif years > 0:
            year_text: str = "year" if years == 1 else "years"
            return f"{years} {year_text}"
        else:
            month_text: str = "month" if remaining_months == 1 else "months"
            return f"{remaining_months} {month_text}"
    
    def get_experience_summary(self, projects_months: int, roles_months: int) -> Dict[str, Union[int, str]]:
        """
        Get comprehensive work experience summary.
        
        This method provides a detailed summary of work experience including total months,
        years, months, formatted duration string, and primary source information.
        It determines the primary source based on which calculation method provided
        valid results.
        
        Args:
            projects_months: Experience calculated from projects in months.
                           Should be non-negative integer.
            roles_months: Experience calculated from roles in months.
                        Should be non-negative integer.
        
        Returns:
            Dict[str, Union[int, str]]: Comprehensive experience summary containing:
                - total_months: int - Total experience in months
                - years: int - Complete years component
                - months: int - Remaining months component
                - formatted_duration: str - Human-readable duration string
                - primary_source: str - Source of primary calculation ("projects", "roles", or "none")
                - projects_months: int - Original projects months value
                - roles_months: int - Original roles months value
        
        Examples:
            >>> analyzer = ExperienceAnalyzer()
            >>> summary = analyzer.get_experience_summary(24, 18)
            >>> print(f"Total: {summary['total_months']} months, Source: {summary['primary_source']}")
            Total: 24 months, Source: projects
        """
        try:
            # Determine primary experience source
            if projects_months > 0:
                primary_source = "projects"
                primary_months = projects_months
            elif roles_months > 0:
                primary_source = "roles"
                primary_months = roles_months
            else:
                primary_source = "none"
                primary_months = 0
            
            # Format for output
            years = primary_months // 12
            months = primary_months % 12
            
            if years > 0 and months > 0:
                if years == 1 and months == 1:
                    formatted_duration = f"{years} year, {months} month"
                elif years == 1:
                    formatted_duration = f"{years} year, {months} months"
                elif months == 1:
                    formatted_duration = f"{years} years, {months} month"
                else:
                    formatted_duration = f"{years} years, {months} months"
            elif years > 0:
                if years == 1:
                    formatted_duration = f"{years} year"
                else:
                    formatted_duration = f"{years} years"
            else:
                if months == 1:
                    formatted_duration = f"{months} month"
                else:
                    formatted_duration = f"{months} months"
            
            return {
                "total_months": primary_months,
                "years": years,
                "months": months,
                "formatted_duration": formatted_duration,
                "primary_source": primary_source,
                "projects_months": projects_months,
                "roles_months": roles_months
            }
            
        except Exception as e:
            logger.error(f"Error getting experience summary: {e}")
            return {
                "total_months": 0,
                "years": 0,
                "months": 0,
                "formatted_duration": "0 months",
                "primary_source": "none",
                "projects_months": 0,
                "roles_months": 0
            }
