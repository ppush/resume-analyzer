import asyncio
import json
import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from services.llm_client import query_llm, LLMConnectionError
from config import MAX_CONCURRENT_REQUESTS

logger = logging.getLogger(__name__)

@dataclass
class BlockResult:
    skills: List[Dict[str, Any]]
    roles: List[Dict[str, Any]]
    languages: List[Dict[str, Any]]
    location: str
    experience: str
    ready_to_remote: bool
    ready_to_trip: bool

class BlockProcessor:
    """Resume block processor using LLM"""
    
    def __init__(self):
        self.skill_prompts = {
            "summary": self._get_summary_prompt(),
            "skills": self._get_skills_prompt(),
            "projects": self._get_projects_prompt(),
            "education": self._get_education_prompt(),
            "languages": self._get_languages_prompt()
        }
    
    async def process_blocks_parallel(self, blocks: Dict[str, any]) -> Dict[str, BlockResult]:
        """Processes all blocks in parallel through LLM with concurrency limit"""
        tasks = []
        for block_name, content in blocks.items():
            # Handle both string and list content
            if (isinstance(content, str) and content.strip()) or (isinstance(content, list) and content):
                task = self._process_single_block(block_name, content)
                tasks.append(task)
        
        # Process with concurrency limit
        results = await self._process_with_concurrency_limit(tasks)
        
        processed_results = {}
        result_index = 0
        for block_name, content in blocks.items():
            # Handle both string and list content
            if (isinstance(content, str) and content.strip()) or (isinstance(content, list) and content):
                if isinstance(results[result_index], Exception):
                    # Re-raise all exceptions
                    raise results[result_index]
                else:
                    processed_results[block_name] = results[result_index]
                result_index += 1
        
        return processed_results
    
    async def _process_with_concurrency_limit(self, tasks: List) -> List:
        """Processes tasks with concurrency limit to avoid overwhelming LLM"""
        if len(tasks) <= MAX_CONCURRENT_REQUESTS:
            # If tasks count is within limit, process all at once
            return await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process in batches to respect concurrency limit
        results = []
        for i in range(0, len(tasks), MAX_CONCURRENT_REQUESTS):
            batch = tasks[i:i + MAX_CONCURRENT_REQUESTS]
            logger.info(f"Processing batch {i//MAX_CONCURRENT_REQUESTS + 1}/{(len(tasks) + MAX_CONCURRENT_REQUESTS - 1)//MAX_CONCURRENT_REQUESTS} ({len(batch)} tasks)")
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
        
        return results
    
    async def _process_single_block(self, block_name: str, content) -> BlockResult:
        """Processes single resume block"""
        try:
            if block_name == "projects":
                # For projects block, process each project separately
                return await self._process_projects_block(content)
            else:
                # For other blocks - normal processing with different temperature values
                prompt = self.skill_prompts.get(block_name, self._get_generic_prompt())
                prompt = prompt.format(content=content)
                
                # Set temperature depending on block type
                temperature = self._get_temperature_for_block(block_name)
                response = await query_llm(prompt, temperature=temperature, seed=42)
                result = self._parse_llm_response(response, block_name)
                return result
                
        except LLMConnectionError as e:
            logger.error(f"LLM unavailable for processing block {block_name}: {e}")
            raise LLMConnectionError(f"Block processing requires LLM: {e}")
        except Exception as e:
            logger.error(f"Error processing {block_name} block: {e}")
            return BlockResult([], [], [], "", "", False, False)
    
    async def _process_projects_block(self, projects_content) -> BlockResult:
        """Processes projects block - each project separately through LLM"""
        try:
            # Handle both string and list content
            if isinstance(projects_content, list):
                # Already split into projects array
                projects_list = [str(project).strip() for project in projects_content if str(project).strip()]
            else:
                # Split string into separate projects
                projects_list = self._split_projects(str(projects_content))
            
            # Process projects separately
            
            # Create tasks for each project
            project_tasks = []
            for i, project in enumerate(projects_list):
                task = self._process_single_project(i + 1, project)
                project_tasks.append(task)
            
            # Execute all projects with concurrency limit
            project_results = await self._process_with_concurrency_limit(project_tasks)
            
            # Process results
            processed_projects = []
            for i, result in enumerate(project_results):
                if isinstance(result, Exception):
                    logger.error(f"Error processing project {i + 1}: {result}")
                    processed_projects.append(BlockResult([], [], [], "", "", False, False))
                else:
                    processed_projects.append(result)
            
            # Merge results from all projects
            return self._merge_project_results(processed_projects)
            
        except Exception as e:
            logger.error(f"Error processing projects block: {e}")
            return BlockResult([], [], [], "", "", False, False)
    
    def _split_projects(self, projects_content: str) -> List[str]:
        """Splits project content into separate projects"""
        # First try by double line breaks
        if "\n\n" in projects_content:
            projects = [p.strip() for p in projects_content.split("\n\n") if p.strip()]
            if len(projects) > 1:
                # Split by double line breaks
                return projects
        
        # If that didn't work, try by keywords
        lines = projects_content.split('\n')
        projects = []
        current_project = []
        
        # Keywords that may indicate start of new project
        project_start_keywords = [
            'senior', 'junior', 'developer', 'architect', 'engineer', 'manager', 'lead',
            'cto', 'head of', 'director', 'consultant', 'specialist',
            'polixis', 'armenia', 'switzerland', 'russia', 'moscow',
            'oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep',
            '2020', '2021', '2022', '2023', '2024', '2025'
        ]
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            # Check if this line is start of new project
            line_lower = line_stripped.lower()
            is_new_project = any(keyword in line_lower for keyword in project_start_keywords)
            
            # If this is new project and we already have current one, save it
            if is_new_project and current_project:
                project_text = '\n'.join(current_project).strip()
                if project_text:
                    projects.append(project_text)
                current_project = []
            
            current_project.append(line_stripped)
        
        # Add last project
        if current_project:
            project_text = '\n'.join(current_project).strip()
            if project_text:
                projects.append(project_text)
        
        # If still only one project, try to split by years
        if len(projects) <= 1:
            # Look for patterns with years and positions
            import re
            year_pattern = r'\b(19|20)\d{2}\b'
            year_matches = re.findall(year_pattern, projects_content)
            
            if len(year_matches) > 1:
                # Split by years
                year_splits = re.split(r'\b(19|20)\d{2}\b', projects_content)
                projects = []
                for i in range(1, len(year_splits), 2):  # Take odd indices (after year)
                    if i < len(year_splits) - 1:
                        project_text = (year_splits[i] + year_splits[i+1]).strip()
                        if project_text:
                            projects.append(project_text)
                
                if len(projects) > 1:
                    # Split by years
                    return projects
        
        # If nothing worked, return as single project
        if not projects:
            projects = [projects_content.strip()]
        
        # Project splitting completed
        return projects
    
    async def _process_single_project(self, project_number: int, project_content: str) -> BlockResult:
        """Processes single project through LLM"""
        try:
            prompt = self._get_single_project_prompt().format(content=project_content)
            
            # For projects use temperature = 0 (deterministic)
            response = await query_llm(prompt, temperature=0.0, seed=42)
            result = self._parse_llm_response(response, f"project_{project_number}")
            return result
            
        except LLMConnectionError as e:
            logger.error(f"LLM unavailable for processing project {project_number}: {e}")
            raise LLMConnectionError(f"Project processing requires LLM: {e}")
        except Exception as e:
            logger.error(f"Error processing project {project_number}: {e}")
            return BlockResult([], [], [], "", "", False, False)
    
    def _parse_llm_response(self, response: str, block_name: str) -> BlockResult:
        """Parses LLM response into structured format"""
        try:
            # Remove markdown blocks if present
            if '```json' in response:
                # Extract JSON from markdown block
                start = response.find('```json') + 7
                end = response.find('```', start)
                if end != -1:
                    response = response[start:end].strip()
            elif '```' in response:
                # Extract JSON from regular markdown block
                start = response.find('```') + 3
                end = response.find('```', start)
                if end != -1:
                    response = response[start:end].strip()
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
            else:
                data = {}
            
            return BlockResult(
                skills=data.get('skills', []),
                roles=data.get('roles', []),
                languages=data.get('languages', []),
                location=data.get('location', ''),
                experience=data.get('experience', ''),
                ready_to_remote=data.get('ready_to_remote', False),
                ready_to_trip=data.get('ready_to_trip', False)
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {block_name}: {e}")
            return BlockResult([], [], [], "", "", False, False)
    
    def _get_summary_prompt(self) -> str:
        return """
        Analyze the following resume block (summary/about me) and extract information in JSON format:
        
        {content}
        
        Return JSON with fields:
        - skills: list of skills with base score 10
        - location: candidate location (city, country, or region) - extract from contact info, address, or location mentions
        - experience: total work experience
        - ready_to_remote: willingness to work remotely (boolean)
        - ready_to_trip: willingness to travel for business (boolean)
        
        IMPORTANT: Look for location information in:
        - Contact information (e.g., "Armenia | Tel: +374...")
        - Address fields
        - Location mentions in text
        - Geographic references
        
        Example response:
        {{
            "skills": [{{"name": "Project Management", "score": 10}}, {{"name": "Team Leadership", "score": 10}}],
            "location": "USA, New York",
            "experience": "5 years",
            "ready_to_remote": true,
            "ready_to_trip": false
        }}
        """
    
    def _get_skills_prompt(self) -> str:
        return """
        Analyze the skills block and extract direct skills with intelligent scoring:
        
        {content}
        
        Return JSON with fields:
        - skills: list of skills with intelligent scores (10-100)
        
        Scoring Rules:
        
        Base Scoring:
        - Individual skills: Base score 10
        
        Interrelated Skills Bonus:
        - If skills are related/connected, increase their scores
        - Related skills get +10 to +30 bonus points
        - Maximum score for any skill: 100
        
        Examples of Related Skills:
        - Project Management + Team Leadership + Strategic Planning = Higher scores for management expertise
        - Marketing + Digital Marketing + Social Media = Higher scores for marketing expertise
        - Sales + Customer Relationship + Negotiation = Higher scores for sales expertise
        - Finance + Accounting + Risk Management = Higher scores for financial expertise
        - Design + User Experience + Visual Communication = Higher scores for design expertise
        - Engineering + Problem Solving + Technical Design = Higher scores for engineering expertise
        - Healthcare + Patient Care + Medical Procedures = Higher scores for healthcare expertise
        - Education + Curriculum Development + Student Assessment = Higher scores for education expertise
        
        Scoring Logic:
        1. Identify individual skills (base score 10)
        2. Find related/connected skills
        3. Increase scores for related skills by 10-30 points
        4. Ensure maximum score doesn't exceed 100
        
        Example response:
        {{
            "skills": [
                {{"name": "Project Management", "score": 25}},
                {{"name": "Team Leadership", "score": 30}},
                {{"name": "Strategic Planning", "score": 28}},
                {{"name": "Marketing", "score": 10}},
                {{"name": "Sales", "score": 10}}
            ]
        }}
        
        Important:
        - Base score for individual skills: 10
        - Related skills get bonus points: +10 to +30
        - Maximum score: 100
        - Focus on identifying skill relationships
        - Return valid JSON only
        """
    
    def _get_projects_prompt(self) -> str:
        return """
        You are an expert HR professional and job title cataloger with deep knowledge of ALL industries and professions. Your task is to analyze the candidate's resume block and return ONLY valid JSON strictly in the format specified. Do not include any markdown, explanations, or extra text.
        
        {content}
    
        
        Return JSON with fields:
        - skills: list of skills with scores (0-100)
        - roles: list of roles with projects, duration and scores
        
        CRITICAL DURATION CALCULATION:
        - Calculate EXACT duration from start and end dates
        - Use precise format: "X years, Y months" or "X.Y years"
        - Example: "Oct 2023 – Jul 2025" = "1 year, 9 months" (not "2 years")
        - Example: "Oct 2021 – Sep 2023" = "2 years" (exact)
        
        CRITICAL ROLE STANDARDS (STRICT - NO EXCEPTIONS):
        - ALWAYS use FULL, DESCRIPTIVE job titles (NOT abbreviations)
        - NEVER create new variations of existing titles
        - Be CONSISTENT - same role should always get the same title
        - Use industry-standard terminology when possible
        - Prefer FULL names over abbreviations (e.g., "Project Manager" over "PM")
        - Be UNIVERSAL - work for ALL industries (IT, Marketing, Sales, Finance, Healthcare, etc.)
        
        CRITICAL PROJECT NAMING STANDARDS:
        - Use ONLY the company name and location (e.g., "Company Name (Country)")
        - NEVER add descriptive details like "Project", "System", "Platform"
        - NEVER add technical descriptions or project specifics
        - Be CONSISTENT - same company should always get the same name
        
        CRITICAL DURATION STANDARDS:
        - Calculate EXACT duration from dates
        - Use PRECISE format: "X years, Y months" or "X years" (exact)
        - NEVER approximate or round up/down
        - Be CONSISTENT - same dates should always give same duration
        
        ROLE ORDERING RULES:
        - Sort roles by score in DESCENDING order (highest first)
        - If same score, sort by duration (longest first)
        - If same duration, sort by recency (most recent first)
        - Be CONSISTENT - same data should always give same order
        
        EXAMPLES OF GOOD ROLE TITLES (for reference):
        - "Senior Software Developer" (NOT "Senior Dev", "Senior Engineer")
        - "Project Manager" (NOT "PM", "Project Lead")
        - "Team Lead" (NOT "Team Leader", "Lead Developer")
        - "Business Analyst" (NOT "BA", "Analyst")
        - "Marketing Manager" (NOT "Marketing Mgr", "Marketing Lead")
        - "Sales Director" (NOT "Sales Dir", "Sales Manager")
        - "Financial Analyst" (NOT "FA", "Finance Analyst")
        - "Healthcare Administrator" (NOT "Admin", "Healthcare Admin")
        
        Scoring Rules:
        
        For Roles:
        1. The closer the work time is to the current time, the HIGHER the role score
        2. The longer the work duration, the HIGHER the role score
        
        For Skills:
        3. The closer the work time is to the current time, the HIGHER the skill score
        4. The longer the work duration, the HIGHER the skill score
        5. If skills are interrelated/connected, the HIGHER the skill score
        
        CRITICAL TIME-BASED SCORING:
        - Skills from (ThisYear-5)-ThisYear: Score 70-100 (modern, relevant)
        - Skills from (ThisYear-10)-(ThisYear-6): Score 50-80 (somewhat relevant)
        - Skills from (ThisYear-15)-(ThisYear-11): Score 30-60 (outdated but usable)
        - Skills from (ThisYear-20)-(ThisYear-16): Score 15-40 (very outdated)
        - Skills from (ThisYear-30)-(ThisYear-21): Score 5-25 (legacy, minimal relevance)
        
        Example response:
        {{
            "skills": [
                {{"name": "Project Management", "score": 85}},
                {{"name": "Team Leadership", "score": 80}},
                {{"name": "Strategic Planning", "score": 75}}
            ],
            "roles": [
                {{"title": "Senior Software Developer", "project": "Project A", "duration": "1 year, 9 months", "score": 85, "category": ["Development", "Software Engineering"]}}
            ]
        }}
        
        Important:
        - Apply STRICT time-based scoring rules
        - ALWAYS use CRITICAL ROLE STANDARDS when applicable
        - Recent skills (ThisYear-5+) get highest scores
        - Legacy skills get significantly lower scores
        - Calculate EXACT duration from dates, not approximate
        - Return valid JSON only
        - NO CREATIVITY in role titles - use standard names only
        - Follow CRITICAL PROJECT NAMING STANDARDS strictly
        - Follow CRITICAL DURATION STANDARDS strictly
        - Follow ROLE ORDERING RULES strictly
        """
    
    def _get_single_project_prompt(self) -> str:
        """Prompt for single project processing"""
        return """
        You are an expert HR professional and job title cataloger with deep knowledge of ALL industries and professions. Your task is to analyze the following individual project/work experience and return ONLY valid JSON strictly in the format specified. Do not include any markdown, explanations, or extra text.
        
        Project/Work Experience:
        {content}
    
        
        Return JSON with fields:
        - skills: list of skills used in this specific project with scores (0-100)
        - roles: list of roles in this specific project with details
        
        JSON FORMATTING RULES:
        - Escape all quotes in text: " becomes \"
        - Escape all backslashes: \\ becomes \\\\
        - Escape all newlines: \n becomes \\n
        - Escape all tabs: \t becomes \\t
        - Ensure all strings are properly quoted
        - Do not include unescaped special characters
        
        CRITICAL DURATION CALCULATION:
        - Calculate EXACT duration from start and end dates
        - Use precise format: "X years, Y months" or "X.Y years"
        - Example: "Oct 2023 – Jul 2025" = "1 year, 9 months" (not "2 years")
        - Example: "Oct 2021 – Sep 2023" = "2 years" (exact)
        
        CRITICAL ROLE STANDARDS (STRICT - NO EXCEPTIONS):
        - ALWAYS use FULL, DESCRIPTIVE job titles (NOT abbreviations)
        - NEVER create new variations of existing titles
        - Be CONSISTENT - same role should always get the same title
        - Use industry-standard terminology when possible
        - Prefer FULL names over abbreviations (e.g., "Project Manager" over "PM")
        - Be UNIVERSAL - work for ALL industries (IT, Marketing, Sales, Finance, Healthcare, etc.)
        
        CRITICAL PROJECT NAMING STANDARDS:
        - Use ONLY the company name and location (e.g., "Company Name (Country)")
        - NEVER add descriptive details like "Project", "System", "Platform"
        - NEVER add technical descriptions or project specifics
        - Be CONSISTENT - same company should always get the same name
        
        CRITICAL DURATION STANDARDS:
        - Calculate EXACT duration from dates
        - Use PRECISE format: "X years, Y months" or "X years" (exact)
        - NEVER approximate or round up/down
        - Be CONSISTENT - same dates should always give same duration
        
        ROLE ORDERING RULES:
        - Sort roles by score in DESCENDING order (highest first)
        - If same score, sort by duration (longest first)
        - If same duration, sort by recency (most recent first)
        - Be CONSISTENT - same data should always give same order
        
        EXAMPLES OF GOOD ROLE TITLES (for reference):
        - "Senior Software Developer" (NOT "Senior Dev", "Senior Engineer")
        - "Project Manager" (NOT "PM", "Project Lead")
        - "Team Lead" (NOT "Team Leader", "Lead Developer")
        - "Business Analyst" (NOT "BA", "Analyst")
        - "Marketing Manager" (NOT "Marketing Mgr", "Marketing Lead")
        - "Sales Director" (NOT "Sales Dir", "Sales Manager")
        - "Financial Analyst" (NOT "FA", "Finance Analyst")
        - "Healthcare Administrator" (NOT "Admin", "Healthcare Admin")
        
        Scoring Rules:
        
        For Roles:
        1. The closer the work time is to the current time, the HIGHER the role score
        2. The longer the work duration, the HIGHER the role score
        
        For Skills:
        3. The closer the work time is to the current time, the HIGHER the skill score
        4. The longer the work duration, the HIGHER the skill score
        5. If skills are interrelated/connected, the HIGHER the skill score
        
        CRITICAL TIME-BASED SCORING:
        - Skills from (ThisYear-5)-ThisYear: Score 70-100 (modern, relevant)
        - Skills from (ThisYear-10)-(ThisYear-6): Score 50-80 (somewhat relevant)
        - Skills from (ThisYear-15)-(ThisYear-11): Score 30-60 (outdated but usable)
        - Skills from (ThisYear-20)-(ThisYear-16): Score 15-40 (very outdated)
        - Skills from (ThisYear-30)-(ThisYear-21): Score 5-25 (legacy, minimal relevance)
        
        Example response:
        {{
            "skills": [
                {{"name": "Project Management", "score": 85}},
                {{"name": "Team Leadership", "score": 80}},
                {{"name": "Strategic Planning", "score": 75}}
            ],
            "roles": [
                {{"title": "Senior Software Developer", "project": "Project Name", "duration": "1 year, 9 months", "score": 85, "category": ["Development", "Software Engineering"]}}
            ]
        }}
        
        Important:
        - Focus ONLY on skills and roles from THIS specific project
        - Apply STRICT time-based scoring rules
        - ALWAYS use CRITICAL ROLE STANDARDS when applicable
        - Recent skills (ThisYear-5+) get highest scores
        - Legacy skills get significantly lower scores
        - Score skills based on their importance in this project (0-100)
        - Extract role information specific to this project
        - Calculate EXACT duration from dates, not approximate
        - Return valid JSON only
        - NO CREATIVITY in role titles - use standard names only
        - Follow CRITICAL PROJECT NAMING STANDARDS strictly
        - Follow CRITICAL DURATION STANDARDS strictly
        """
    
    def _get_education_prompt(self) -> str:
        return """
        Analyze the education block:
        
        {content}
        
        Return JSON with fields:
        - skills: skills from education (if any)
        
        Example response:
        {{
            "skills": [{{"name": "Business Administration", "score": 5}}]
        }}
        """
    
    def _get_temperature_for_block(self, block_name: str) -> float:
        """Returns optimal temperature value for each block type"""
        temperature_map = {
            "summary": 0.7,    # Creativity for generalization
            "skills": 0.0,     # Deterministic for skill accuracy
            "projects": 0.0,   # Deterministic for project accuracy
            "education": 1.0,  # Maximum creativity for education
            "languages": 0.0   # Deterministic for language accuracy
        }
        return temperature_map.get(block_name, 0.5)  # Default 0.5
    
    def _get_languages_prompt(self) -> str:
        return """
        You are an expert HR professional and language skills analyzer. Your task is to analyze the following languages block and return ONLY valid JSON strictly in the format specified. Do not include any markdown, explanations, or extra text.
        
        Languages Block:
        {content}
        
        CRITICAL PARSING RULES (STRICT - NO EXCEPTIONS):
        - Return ONLY valid JSON with languages array
        - Each language must have "language" and "level" fields
        - Use standard language levels: "native", "fluent", "advanced", "intermediate", "basic"
        - If no languages found, return empty array: "languages": []
        - NO extra text, NO explanations, NO markdown
        - Be CONSISTENT in language identification
        
        Return JSON with fields:
        - languages: list of languages with levels
        
        Example response:
        {{
            "languages": [
                {{"language": "English", "level": "native"}},
                {{"language": "Spanish", "level": "fluent"}}
            ]
        }}
        
        Important:
        - Return valid JSON only
        - Be CONSISTENT in language identification
        - NO CREATIVITY - follow rules strictly
        """
    
    def _get_generic_prompt(self) -> str:
        return """
        Analyze the following resume block:
        
        {content}
        
        Extract any useful information about skills, roles, location, etc.
        
        Return JSON with fields:
        - skills: list of skills
        - roles: list of roles
        - location: location
        - languages: languages
        
        Example response:
        {{
            "skills": [],
            "roles": [],
            "location": "",
            "languages": []
        }}
        """
    
    def _merge_project_results(self, project_results: List[BlockResult]) -> BlockResult:
        """Merges results from all projects into single BlockResult"""
        try:
            all_skills = []
            all_roles = []
            all_languages = []
            all_locations = []
            all_experiences = []
            any_remote = False
            any_trip = False
            
            for result in project_results:
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
            
            # Remove duplicate skills
            unique_skills = []
            skill_names = set()
            for skill in all_skills:
                if skill.get('name') not in skill_names:
                    unique_skills.append(skill)
                    skill_names.add(skill.get('name'))
            
            # Remove duplicate roles
            unique_roles = []
            role_keys = set()
            for role in all_roles:
                role_key = f"{role.get('title', '')}_{role.get('project', '')}"
                if role_key not in role_keys:
                    unique_roles.append(role)
                    role_keys.add(role_key)
            
            # Remove duplicate languages
            unique_languages = []
            language_keys = set()
            for lang in all_languages:
                lang_key = f"{lang.get('language', '')}_{lang.get('level', '')}"
                if lang_key not in language_keys:
                    unique_languages.append(lang)
                    language_keys.add(lang_key)
            
            # Choose most frequent location and experience
            location = max(all_locations, key=all_locations.count) if all_locations else ""
            experience = max(all_experiences, key=all_experiences.count) if all_experiences else ""
            
            return BlockResult(
                skills=unique_skills,
                roles=unique_roles,
                languages=unique_languages,
                location=location,
                experience=experience,
                ready_to_remote=any_remote,
                ready_to_trip=any_trip
            )
            
        except Exception as e:
            logger.error(f"Error merging project results: {e}")
            return BlockResult([], [], [], "", "", False, False)
