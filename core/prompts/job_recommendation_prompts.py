"""
Job recommendation prompts for LLM analysis.
"""

from abc import ABC
from core.prompts.prompt_base import PromptBase


class JobRecommendationPrompts(PromptBase):
    """Job recommendations prompts"""
    
    def generate_job_recommendations_prompt(self, resume_data: str) -> str:
        """
        Generates prompt for job recommendations based on resume analysis.
        
        Args:
            resume_data: JSON string with resume analysis results
            
        Returns:
            LLM prompt with instructions for generating recommendations
        """
        return f"""You are an expert HR consultant and career advisor. Analyze the following resume analysis and provide job recommendations.

RESUME ANALYSIS DATA:
{resume_data}

TASK: Based on the skills, experience, and roles in this resume, recommend the TOP 5-8 job positions where this candidate would be most productive and successful.

REQUIREMENTS:
1. Focus on positions that match the candidate's strongest skills and experience
2. Consider the candidate's experience level (entry, mid, senior)
3. Recommend positions from various industries where their skills transfer well
4. Each recommendation should include a confidence score (0-100)

OUTPUT FORMAT - Return ONLY valid JSON:
{{
  "recommendations": [
    {{
      "title": "Job Title",
      "score": 85,
      "category": ["Primary Category", "Secondary Category"],
      "reason": "Brief explanation why this position fits"
    }}
  ]
}}

CRITICAL: You MUST return ONLY the JSON object above. No additional text, no explanations, no markdown formatting. Just the raw JSON.

RULES:
- Return ONLY the JSON, no additional text
- Use realistic job titles from the current market
- Score should reflect how well the candidate fits (0-100)
- Categories should be relevant to the position
- Reason should be 1-2 sentences explaining the fit
- Focus on positions where the candidate can excel based on their profile

EXAMPLES OF GOOD RECOMMENDATIONS:
- For HR professionals: "HR Business Partner", "Talent Acquisition Specialist", "Recruitment Manager"
- For sales professionals: "Sales Manager", "Business Development Representative", "Account Executive"
- For technical roles: "Software Engineer", "Data Analyst", "Product Manager"

Analyze the resume data and provide the most relevant job recommendations.

REMEMBER: Return ONLY the JSON object. No other text, no explanations, no formatting."""
    
    def get_temperature(self) -> float:
        """Returns temperature for recommendations (0.1 for slight creativity)"""
        return 0.1
    
    def generate_prompt(self, **kwargs) -> str:
        """
        Generates recommendations prompt (abstract method implementation)
        
        Args:
            **kwargs: May contain resume_data
            
        Returns:
            LLM prompt
        """
        resume_data = kwargs.get('resume_data', '')
        return self.generate_job_recommendations_prompt(resume_data)
