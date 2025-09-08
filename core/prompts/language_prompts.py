"""
Prompts for languages processing
"""

from .prompt_base import PromptBase


class LanguagePrompts(PromptBase):
    """Languages prompt generator"""
    
    def generate_languages_prompt(self, languages_text: str) -> str:
        """Generates prompt for languages extraction"""
        prompt = f"""You are an expert HR analyst specializing in language extraction from resumes.

## TASK
Analyze the following text and extract all mentioned languages with proficiency levels.

## TEXT FOR ANALYSIS
{languages_text}

## CRITICAL PARSING RULES (STRICT - NO EXCEPTIONS)
- Return ONLY valid JSON array
- Each language must have "language" and "level" fields
- Use standard language levels: "Native", "Fluent", "Advanced", "Intermediate", "Basic"
- If no languages found, return empty array []
- NO extra text before or after JSON
- Be CONSISTENT in language identification

## EXPECTED JSON FORMAT
```json
[
  {{
    "language": "English",
    "level": "Fluent"
  }},
  {{
    "language": "Russian",
    "level": "Native"
  }}
]
```

## IMPORTANT
- Follow CRITICAL PARSING RULES strictly
- Return only valid JSON
- Do not add extra text
- Be consistent in language identification"""
        
        return self._add_common_instructions(prompt)
    
    def generate_prompt(self, **kwargs) -> str:
        """Generates languages prompt (abstract method implementation)"""
        languages_text = kwargs.get('languages_text', '')
        return self.generate_languages_prompt(languages_text)
    
    def get_temperature(self) -> float:
        """Returns temperature for languages (0.0 for determinism)"""
        return 0.0
