"""
Prompts for projects and roles processing
"""

from .prompt_base import PromptBase


class ProjectPrompts(PromptBase):
    """Projects and roles prompt generator"""
    
    def generate_projects_prompt(self, projects_text: str) -> str:
        """Generates prompt for projects extraction"""
        prompt = f"""You are an expert HR analyst specializing in project and role extraction from resumes.

## TASK
Analyze the following text and extract all projects with roles, duration, and scores.

## TEXT FOR ANALYSIS
{projects_text}

## CRITICAL ROLE STANDARDS (STRICT - NO EXCEPTIONS)
- ALWAYS use FULL, DESCRIPTIVE job titles (NOT abbreviations)
- NEVER create new variations - use EXISTING titles from the text
- Be CONSISTENT across all projects
- Use industry-standard terminology
- Be UNIVERSAL - work for any industry, not just IT

## CRITICAL PROJECT NAMING STANDARDS
- Use ONLY the company name and location (e.g., "Company Name (Country)")
- NEVER add descriptive details
- NEVER add technical descriptions
- Be CONSISTENT

## CRITICAL DURATION STANDARDS
- Calculate EXACT duration from dates
- Use PRECISE format: "X years, Y months" or "X years"
- NEVER approximate
- Be CONSISTENT

## ROLE ORDERING RULES
- Sort roles by score in DESCENDING order (highest first)
- If same score, sort by duration (longest first)
- If same duration, sort by recency (most recent first)
- Be CONSISTENT - same data should always give same order

## IMPORTANT
- Follow CRITICAL ROLE STANDARDS strictly
- Follow CRITICAL PROJECT NAMING STANDARDS strictly
- Follow CRITICAL DURATION STANDARDS strictly
- Follow ROLE ORDERING RULES strictly
- Return ONLY valid JSON array
- Each role must have: title, project, duration, score, category

## EXPECTED JSON FORMAT
```json
[
  {{
    "title": "Senior Java Developer",
    "project": "Energize Global Services (Armenia)",
    "duration": "1 year, 4 months",
    "score": 85,
    "category": ["Development", "Software Engineering"]
  }}
]
```"""
        
        return self._add_common_instructions(prompt)
    
    def generate_prompt(self, **kwargs) -> str:
        """Generates projects prompt (abstract method implementation)"""
        projects_text = kwargs.get('projects_text', '')
        if 'single' in kwargs:
            return self.generate_single_project_prompt(projects_text)
        else:
            return self.generate_projects_prompt(projects_text)
    
    def generate_single_project_prompt(self, project_text: str) -> str:
        """Generates prompt for single project analysis"""
        prompt = f"""You are an expert HR analyst specializing in detailed project analysis.

## TASK
Analyze the following project and extract detailed role information.

## PROJECT TEXT
{project_text}

## CRITICAL ROLE STANDARDS (STRICT - NO EXCEPTIONS)
- ALWAYS use FULL, DESCRIPTIVE job titles (NOT abbreviations)
- NEVER create new variations - use EXISTING titles from the text
- Be CONSISTENT across all projects
- Use industry-standard terminology
- Be UNIVERSAL - work for any industry, not just IT

## CRITICAL PROJECT NAMING STANDARDS
- Use ONLY the company name and location (e.g., "Company Name (Country)")
- NEVER add descriptive details
- NEVER add technical descriptions
- Be CONSISTENT

## CRITICAL DURATION STANDARDS
- Calculate EXACT duration from dates
- Use PRECISE format: "X years, Y months" or "X years"
- NEVER approximate
- Be CONSISTENT

## ROLE ORDERING RULES
- Sort roles by score in DESCENDING order (highest first)
- If same score, sort by duration (longest first)
- If same duration, sort by recency (most recent first)
- Be CONSISTENT - same data should always give same order

## IMPORTANT
- Follow CRITICAL ROLE STANDARDS strictly
- Follow CRITICAL PROJECT NAMING STANDARDS strictly
- Follow CRITICAL DURATION STANDARDS strictly
- Follow ROLE ORDERING RULES strictly
- Return ONLY valid JSON array
- Each role must have: title, project, duration, score, category

## EXPECTED JSON FORMAT
```json
[
  {{
    "title": "Senior Java Developer",
    "project": "Energize Global Services (Armenia)",
    "duration": "1 year, 4 months",
    "score": 85,
    "category": ["Development", "Software Engineering"]
  }}
]```"""
        
        return self._add_common_instructions(prompt)
    
    def get_temperature(self) -> float:
        """Returns temperature for projects (0.0 for determinism)"""
        return 0.0
