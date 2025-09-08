
"""
Prompts for resume parsing
"""

from .prompt_base import PromptBase


class ParsingPrompts(PromptBase):
    """Resume parsing prompt generator"""
    
    def generate_parsing_prompt(self, resume_text: str) -> str:
        """Generates prompt for splitting resume into blocks"""
        prompt = f"""You are an expert HR analyst. Analyze this resume and divide it into blocks.

RESUME:
{resume_text}

## TASK
Extract these blocks:
- "projects" - work experience and projects
- "skills" - technical skills and competencies  
- "education" - education and certifications
- "languages" - language proficiency
- "summary" - general information and overview

## OUTPUT
Return ONLY valid JSON with these 5 blocks. Each block contains relevant text only.

```json
{{
  "projects": "work experience text...",
  "skills": "skills text...",
  "education": "education text...",
  "languages": "languages text...",
  "summary": "summary text..."
}}
```"""
        
        return self._add_common_instructions(prompt)
    
    def generate_html_parsing_prompt(self, html_content: str) -> str:
        """Generates prompt for parsing HTML resume chunk"""
        prompt = f"""You are an expert HR analyst. Analyze this HTML resume chunk and extract relevant information.

HTML CHUNK:
{html_content}

## TASK
Extract information for these blocks:
- "projects" - ONLY actual work experience with company names, job titles, dates, and achievements (as array of individual project descriptions)
- "skills" - technical skills, technologies, competencies, and expertise areas
- "education" - education, degrees, certifications, and academic background
- "languages" - language proficiency levels
- "summary" - general information, overview, professional summary, and contact information (name, location, phone, email)

## IMPORTANT RULES
- For "projects": ONLY include actual work experience with company names, job titles, and dates. Each project should be a complete description including company, role, and key achievements.
- For "skills": include technical skills, technologies, methodologies, and competencies
- For "education": look for sections titled "EDUCATION", "EDUCATION & PROFESSIONAL DEVELOPMENT", "ACADEMIC BACKGROUND", universities, degrees, certifications, training programs
- For "languages": look for sections titled "LANGUAGES", "LANGUAGE SKILLS", language proficiency levels (native, fluent, intermediate, basic)
- For other blocks: return as single text string
- Only include information that is clearly present in this chunk
- If a block has no relevant information, return empty string or empty array
- DO NOT mix skills/competencies with actual work projects

## JSON FORMATTING RULES
- Escape all quotes in text: " becomes \"
- Escape all backslashes: \\ becomes \\\\
- Escape all newlines: \n becomes \\n
- Escape all tabs: \t becomes \\t
- Ensure all strings are properly quoted
- Do not include unescaped special characters

## OUTPUT
Return ONLY valid JSON with these 5 blocks:

```json
{{
  "projects": ["project1 description", "project2 description"],
  "skills": "skills text...",
  "education": "education text...",
  "languages": "languages text...",
  "summary": "summary text..."
}}
```"""
        
        return self._add_common_instructions(prompt)

    def generate_prompt(self, **kwargs) -> str:
        """Generates parsing prompt (abstract method implementation)"""
        resume_text = kwargs.get('resume_text', '')
        return self.generate_parsing_prompt(resume_text)
    
    def get_temperature(self) -> float:
        """Returns temperature for parsing (0.0 for determinism)"""
        return 0.0
