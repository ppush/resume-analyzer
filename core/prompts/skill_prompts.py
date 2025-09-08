"""
Prompts for skills processing
"""

from .prompt_base import PromptBase


class SkillPrompts(PromptBase):
    """Skills prompt generator"""
    
    def generate_skills_prompt(self, skills_text: str) -> str:
        """Generates prompt for skills extraction"""
        prompt = f"""You are an expert skills cataloger specializing in comprehensive skill extraction from resumes.

## TASK
Analyze the following text and extract all mentioned skills with scores.

## TEXT FOR ANALYSIS
{skills_text}

## CRITICAL EXTRACTION RULES (STRICT - NO EXCEPTIONS)
- Extract ALL mentioned skills, technologies, and competencies
- Assign scores from 0-100 based on relevance and frequency
- Use descriptive skill names (e.g., "Java Development", "Project Management")
- Be UNIVERSAL - work for any industry, not just IT
- Return ONLY valid JSON array

## EXPECTED JSON FORMAT
```json
[
  {{
    "name": "Java Development",
    "score": 85
  }},
  {{
    "name": "Project Management",
    "score": 78
  }}
]
```

## IMPORTANT
- Extract all mentioned skills
- Be accurate in naming
- Work for any industry
- Return only valid JSON"""
        
        return self._add_common_instructions(prompt)
    
    def generate_prompt(self, **kwargs) -> str:
        """Generates skills prompt (abstract method implementation)"""
        skills_text = kwargs.get('skills_text', '')
        if 'merge' in kwargs:
            return self.generate_skills_merge_prompt(skills_text)
        else:
            return self.generate_skills_prompt(skills_text)
    
    def generate_skills_merge_prompt(self, skills_list: str) -> str:
        """Generates prompt for skills merging"""
        prompt = f"""You are a skills analyzer. Your task is to MERGE similar skills into single entries.

INPUT SKILLS:
{skills_list}

## MERGING RULES:
1. **MERGE similar skills**: "Java" + "Java Development" → "Java Development"
2. **DO NOT MERGE different programming languages**: "Java" ≠ "Python" ≠ "JavaScript" ≠ "PHP" ≠ "Delphi"
3. **DO NOT MERGE different technologies**: "AWS" ≠ "Azure", "Spring" ≠ "Django"
4. **DO NOT MERGE different frameworks**: "Spring Boot" ≠ "Quarkus", "React" ≠ "Vue"
5. **Choose the BEST name**: Prefer full names over abbreviations
6. **Score calculation**: Take highest score + 1% bonus per merged skill

## PROGRAMMING LANGUAGES - CRITICAL RULE:
- Java, Python, JavaScript, PHP, Delphi, C++, C#, Go, Rust, Swift, Kotlin, Scala, Ruby, Perl, R, MATLAB
- Each programming language is a SEPARATE skill - NEVER combine them
- Only merge variations of the SAME language: "Java" + "Java Development" = "Java Development"
- If you see "Java" and "Python" in the list, they must remain as TWO separate skills
- If you see "JavaScript" and "PHP" in the list, they must remain as TWO separate skills

## OUTPUT FORMAT:
Return ONLY valid JSON array. Each skill must have:
- "name": Best name from merged skills
- "merged_names": All names joined with "&"
- "merge_reason": Why skills were merged
- "score": Calculated score (highest + bonus)

## EXAMPLES:
Input: "- Java (score: 85)" + "- Java Development (score: 90)"
Output: {{"name": "Java Development", "merged_names": "Java & Java Development", "merge_reason": "Same language, different specificity", "score": 92}}

Input: "- Java (score: 85)" + "- Python (score: 90)" + "- JavaScript (score: 80)"
Output: THREE separate skills - DO NOT MERGE:
[
  {{"name": "Java", "merged_names": "Java", "merge_reason": "No merge needed", "score": 85}},
  {{"name": "Python", "merged_names": "Python", "merge_reason": "No merge needed", "score": 90}},
  {{"name": "JavaScript", "merged_names": "JavaScript", "merge_reason": "No merge needed", "score": 80}}
]

## IMPORTANT FORMATTING RULES:
- In merged_names, use ONLY the skill names, NOT the scores
- Example: "Java (8–21)" should be "Java (8–21)" in merged_names, NOT "Java (85)"
- The score in merged_names should be the original skill name, not a number

## CRITICAL:
- Return ONLY valid JSON array
- Each skill must have all 4 fields
- NEVER merge different programming languages
- Be consistent in merging decisions
- Work for ANY industry"""
        
        return self._add_common_instructions(prompt)
    
    def get_temperature(self) -> float:
        """Returns temperature for skills (0.0 for determinism)"""
        return 0.0
