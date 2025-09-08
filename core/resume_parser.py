import re
import json
import logging
import asyncio
from typing import Dict, List, Any
from services.llm_client import query_llm, LLMConnectionError
from config import MAX_CONCURRENT_REQUESTS, PAGE_SIZE_LINES, LARGE_RESUME_THRESHOLD

logger = logging.getLogger(__name__)

class ResumeParser:
    """LLM-based resume parser for splitting into blocks"""
    
    def __init__(self):
        pass
    
    async def parse_resume(self, text: str) -> Dict[str, str]:
        """
        Splits resume into blocks using LLM:
        - projects / experience (each job as separate block)
        - skills (only from dedicated skills section, not from projects)
        - education (education)
        - languages (languages)
        - summary / about me (summary of everything else)
        """
        try:
            # Clean text
            cleaned_text = self._clean_text(text)
            
            # Check if text is large enough to need page-based processing
            lines_count = len(cleaned_text.split('\n'))
            if lines_count > LARGE_RESUME_THRESHOLD:  # More than threshold lines
                logger.info(f"Large resume detected ({lines_count} lines), using page-based processing")
                blocks = await self._parse_large_resume_by_pages(cleaned_text)
            else:
                # Use LLM to split into blocks
                blocks = await self._split_into_blocks_with_llm(cleaned_text)
            
            # Standardize blocks for consistency
            standardized_blocks = self._standardize_blocks(blocks)
            
            # Resume split into blocks using LLM
            return standardized_blocks
            
        except LLMConnectionError as e:
            logger.error(f"LLM unavailable for resume parsing: {e}")
            raise LLMConnectionError(f"Resume parsing requires LLM: {e}")
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            raise e

    async def parse_resume_from_html_chunks(self, html_chunks: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Parse resume from HTML chunks for better structure preservation
        
        Args:
            html_chunks: List of HTML chunks with metadata
            
        Returns:
            Dictionary of parsed blocks
        """
        try:
            logger.info(f"Parsing resume from {len(html_chunks)} HTML chunks")
            
            # Process chunks with LLM in parallel with concurrency control
            logger.info(f"Processing {len(html_chunks)} chunks with max {MAX_CONCURRENT_REQUESTS} concurrent requests")
            
            # Create semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
            
            async def process_chunk_with_semaphore(chunk, chunk_index):
                """Process single chunk with semaphore control"""
                async with semaphore:
                    logger.info(f"Processing chunk {chunk_index+1}/{len(html_chunks)} (type: {chunk['type']})")
                    return await self._parse_html_chunk_with_llm(chunk['content'])
            
            # Create tasks for parallel processing with concurrency control
            tasks = []
            for i, chunk in enumerate(html_chunks):
                task = process_chunk_with_semaphore(chunk, i)
                tasks.append(task)
            
            # Execute all tasks in parallel with concurrency limit
            logger.info(f"Executing {len(tasks)} LLM requests with max {MAX_CONCURRENT_REQUESTS} concurrent")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect successful results
            all_blocks = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error processing chunk {i+1}: {result}")
                    # Re-raise LLM connection errors
                    if isinstance(result, LLMConnectionError):
                        raise result
                elif result:
                    all_blocks.append(result)
            
            # Combine blocks from all chunks
            combined_blocks = self._combine_html_chunk_blocks(all_blocks)
            
            # Standardize blocks for consistency
            standardized_blocks = self._standardize_blocks(combined_blocks)
            
            logger.info(f"HTML chunk parsing completed: {len(standardized_blocks)} blocks")
            return standardized_blocks
            
        except LLMConnectionError as e:
            logger.error(f"LLM unavailable for HTML chunk parsing: {e}")
            raise LLMConnectionError(f"HTML chunk parsing requires LLM: {e}")
        except Exception as e:
            logger.error(f"Error parsing HTML chunks: {e}")
            raise e
    
    def _clean_text(self, text: str) -> str:
        """Cleans and normalizes text for uniform processing"""
        # Ensure text is a string
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='ignore')
        
        # Remove multiple consecutive empty lines (more than 2)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove extra spaces but preserve single line breaks
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
        text = re.sub(r'\n[ \t]+', '\n', text)  # Remove spaces at line start
        text = re.sub(r'[ \t]+\n', '\n', text)  # Remove spaces at line end
        
        # Remove empty lines at start and end
        text = text.strip()
        
        # Normalization for consistency between formats
        text = self._normalize_text_format(text)
        
        return text.strip()
    
    def _normalize_text_format(self, text: str) -> str:
        """Normalizes text format for uniform processing"""
        # Standardize line breaks
        text = re.sub(r'\r\n', '\n', text)  # Windows -> Unix
        text = re.sub(r'\r', '\n', text)    # Mac -> Unix
        
        # Remove multiple spaces at line start
        text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)
        
        # Standardize section separators
        text = re.sub(r'[-=]{3,}', '---', text)  # Section separators
        text = re.sub(r'_{3,}', '---', text)     # Alternative separators
        
        # Normalize date formatting
        text = re.sub(r'(\d{4})\s*[-–]\s*(\d{4})', r'\1–\2', text)  # Years
        text = re.sub(r'(\w{3})\s+(\d{4})\s*[-–]\s*(\w{3})\s+(\d{4})', r'\1 \2–\3 \4', text)  # Month-year
        
        # Remove extra formatting characters
        text = re.sub(r'[•·▪▫]\s*', '• ', text)  # List markers
        text = re.sub(r'[^\w\s\-–—•.,;:()\[\]{}"\']', '', text)  # Only needed characters
        
        # Standardize spaces around separators
        text = re.sub(r'\s*[|]\s*', ' | ', text)  # Vertical bars
        text = re.sub(r'\s*[-–]\s*', ' – ', text)  # Dashes
        
        return text
    
    def _split_text_into_pages(self, text: str, lines_per_page: int = None) -> List[str]:
        """
        Splits text into pages based on line count
        
        Args:
            text: Text to split
            lines_per_page: Number of lines per page (uses config default if None)
            
        Returns:
            List[str]: List of text pages
        """
        if lines_per_page is None:
            lines_per_page = PAGE_SIZE_LINES
            
        lines = text.split('\n')
        
        if len(lines) <= lines_per_page:
            return [text]
        
        pages = []
        current_page = []
        
        for i, line in enumerate(lines):
            current_page.append(line)
            
            # Check if we've reached the page limit
            if len(current_page) >= lines_per_page:
                # Look for a good break point (empty line or section header)
                break_point = len(current_page)
                
                # Try to find a natural break point in the last few lines
                for j in range(len(current_page) - 1, max(0, len(current_page) - 10), -1):
                    if (not current_page[j].strip() or  # Empty line
                        current_page[j].strip().isupper() or  # Section header
                        current_page[j].strip().endswith(':')):  # Section ending with colon
                        break_point = j + 1
                        break
                
                # Create page from current content
                page_content = '\n'.join(current_page[:break_point])
                if page_content.strip():
                    pages.append(page_content.strip())
                
                # Start new page with remaining content
                current_page = current_page[break_point:]
        
        # Add the last page if it's not empty
        if current_page:
            page_content = '\n'.join(current_page)
            if page_content.strip():
                pages.append(page_content.strip())
        
        return pages
    
    async def _parse_large_resume_by_pages(self, text: str) -> Dict[str, str]:
        """
        Parses large resume by splitting into pages and processing each page
        
        Args:
            text: Large resume text
            
        Returns:
            Dict[str, str]: Combined blocks from all pages
        """
        # Split text into pages
        pages = self._split_text_into_pages(text)
        logger.info(f"Split resume into {len(pages)} pages (page size: {PAGE_SIZE_LINES} lines)")
        
        # Process each page
        all_blocks = []
        for i, page in enumerate(pages):
            logger.info(f"Processing page {i+1}/{len(pages)} ({len(page)} chars)")
            try:
                page_blocks = await self._split_into_blocks_with_llm(page)
                all_blocks.append(page_blocks)
            except Exception as e:
                logger.error(f"Error processing page {i+1}: {e}")
                raise e
        
        # Combine blocks from all pages
        combined_blocks = self._combine_page_blocks(all_blocks)
        logger.info(f"Combined {len(all_blocks)} pages into final blocks")
        
        return combined_blocks
    
    def _combine_page_blocks(self, all_blocks: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Combines blocks from multiple pages into single result
        
        Args:
            all_blocks: List of block dictionaries from each page
            
        Returns:
            Dict[str, str]: Combined blocks
        """
        combined = {
            "projects": "",
            "skills": "",
            "education": "",
            "languages": "",
            "summary": ""
        }
        
        for page_blocks in all_blocks:
            for block_name, block_content in page_blocks.items():
                # Handle both string and list content
                if block_content:
                    if isinstance(block_content, str) and block_content.strip():
                        if combined[block_name]:
                            # Add separator between pages
                            combined[block_name] += "\n\n" + block_content
                        else:
                            combined[block_name] = block_content
                    elif isinstance(block_content, list) and block_content:
                        if combined[block_name]:
                            # Extend existing list
                            combined[block_name].extend(block_content)
                        else:
                            combined[block_name] = block_content
        
        return combined
    
    async def _split_into_blocks_with_llm(self, text: str) -> Dict[str, str]:
        """Splits resume into blocks using LLM"""
        prompt = self._get_parsing_prompt(text)
        
        try:
            # For block splitting use temperature = 0.5 (balance between speed and quality)
            response = await query_llm(prompt, temperature=0.5, seed=42)
            blocks = self._parse_llm_response(response)
            return blocks
        except Exception as e:
            logger.error(f"Error in LLM parsing: {e}")
            raise
    
    def _get_parsing_prompt(self, text: str) -> str:
        """Creates prompt for LLM resume parsing"""
        return f"""
        You are an expert HR professional and resume parser with deep knowledge of ALL industries and professions. Your task is to analyze the following resume and divide it into blocks according to these rules.
        
        Resume:
        {text}
        
        Divide the resume into the following blocks in this order:
        
        1. projects - Each job/work experience should be a separate block. Extract work experience, projects, positions. Each job = separate block.
        2. skills - ONLY if there is a dedicated skills section in the resume. Do NOT include skills mentioned in projects section.
        3. education - Education, certifications, courses
        4. languages - Language skills
        5. summary - Generalize and summarize all other information not covered above (personal info, objectives, etc.)
        
        CRITICAL PARSING RULES (STRICT - NO EXCEPTIONS):
        - Each job/work experience should be a separate item in projects array
        - Skills should only come from dedicated skills section, not from project descriptions
        - Summary should contain general information not covered in other blocks
        - If a block is not found, leave it empty
        - Be CONSISTENT in block identification
        - Use clear boundaries between different work experiences
        
        Return the result in JSON format:
        {{
            "projects": ["job1 description", "job2 description", "job3 description"],
            "skills": "skills section content (only if exists)",
            "education": "education content",
            "languages": "languages content", 
            "summary": "summary of everything else"
        }}
        
        Important:
        - Follow CRITICAL PARSING RULES exactly
        - Return valid JSON only
        - Be CONSISTENT in block identification
        - NO CREATIVITY in parsing - follow rules strictly
        """
    
    def _parse_llm_response(self, response: str) -> Dict[str, str]:
        """Parses LLM response into resume blocks"""
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
                
                # Clean blocks from extra spaces
                cleaned_blocks = {}
                for key, value in data.items():
                    if key == "projects" and isinstance(value, list):
                        # Keep projects as array for proper processing
                        if value:
                            cleaned_blocks[key] = [str(item).strip() for item in value if str(item).strip()]
                        else:
                            cleaned_blocks[key] = []
                    elif isinstance(value, str) and value.strip():
                        cleaned_blocks[key] = value.strip()
                    else:
                        cleaned_blocks[key] = ""
                
                return cleaned_blocks
            else:
                logger.error("No JSON found in LLM response")
                raise ValueError("No JSON found in LLM response")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            raise e
    
    
    def _standardize_blocks(self, blocks: Dict[str, str]) -> Dict[str, str]:
        """
        Standardizes blocks to ensure consistency between formats
        
        Args:
            blocks: Source blocks
            
        Returns:
            Dict[str, str]: Standardized blocks
        """
        try:
            standardized = {}
            
            # Standard block keys
            standard_keys = ['projects', 'skills', 'education', 'languages', 'summary']
            
            # Process each block
            for key in standard_keys:
                if key in blocks:
                    content = blocks[key]
                    
                    # Standardize block content
                    if isinstance(content, list):
                        # Keep projects as list, others as string
                        if key == 'projects':
                            standardized[key] = [str(item).strip() for item in content if str(item).strip()]
                        else:
                            standardized[key] = '\n\n'.join(str(item) for item in content if str(item).strip())
                    else:
                        # If it's a string, standardize it
                        standardized[key] = self._standardize_block_content(content, key)
                else:
                    # If block doesn't exist, create empty one
                    standardized[key] = ""
            
            # Remove extra blocks not in standard
            for key in list(blocks.keys()):
                if key not in standard_keys:
                    logger.info(f"ℹ️ Removed non-standard block: {key}")
            
            logger.info(f"✅ Standardized {len(standardized)} blocks")
            return standardized
            
        except Exception as e:
            logger.error(f"❌ Error standardizing blocks: {e}")
            return blocks
    
    def _standardize_block_content(self, content: str, block_type: str) -> str:
        """
        Standardizes content of specific block
        
        Args:
            content: Block content
            block_type: Block type
            
        Returns:
            str: Standardized content
        """
        if not content:
            return ""
        
        # Remove extra spaces and line breaks
        content = content.strip()
        content = re.sub(r'\n\s*\n', '\n\n', content)  # Maximum 2 line breaks in a row
        content = re.sub(r'^\s+', '', content, flags=re.MULTILINE)  # Remove spaces at line start
        
        # Specific processing for different block types
        if block_type == 'skills':
            # Skills: remove extra separators
            content = re.sub(r'[•·▪▫]\s*', '• ', content)
            content = re.sub(r'[,;]\s*', ', ', content)
        
        elif block_type == 'projects':
            # Projects: standardize separators between projects
            content = re.sub(r'[-=]{3,}', '---', content)
            content = re.sub(r'_{3,}', '---', content)
        
        elif block_type == 'education':
            # Education: standardize date format
            content = re.sub(r'(\d{4})\s*[-–]\s*(\d{4})', r'\1–\2', content)
        
        elif block_type == 'languages':
            # Languages: standardize separators
            content = re.sub(r'[|]\s*', ' | ', content)
            content = re.sub(r'[,;]\s*', ', ', content)
        
        return content
    
    async def _parse_html_chunk_with_llm(self, html_content: str) -> Dict[str, str]:
        """
        Parse HTML chunk with LLM
        
        Args:
            html_content: HTML content of the chunk
            
        Returns:
            Dictionary of parsed blocks from this chunk
        """
        try:
            from core.prompts.parsing_prompts import ParsingPrompts
            
            # Create HTML-specific prompt
            parsing_prompts = ParsingPrompts()
            prompt = parsing_prompts.generate_html_parsing_prompt(html_content)
            
            # Query LLM
            response = await query_llm(prompt, temperature=0.0, seed=42)
            
            # Parse response
            blocks = self._parse_llm_response(response)
            
            return blocks
            
        except LLMConnectionError as e:
            logger.error(f"LLM unavailable for HTML chunk parsing: {e}")
            raise LLMConnectionError(f"HTML chunk parsing requires LLM: {e}")
        except Exception as e:
            logger.error(f"Error parsing HTML chunk with LLM: {e}")
            return {}
    
    def _combine_html_chunk_blocks(self, all_blocks: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Combine blocks from multiple HTML chunks
        
        Args:
            all_blocks: List of block dictionaries from each chunk
            
        Returns:
            Combined blocks dictionary
        """
        combined = {
            "projects": [],
            "skills": "",
            "education": "",
            "languages": "",
            "summary": ""
        }
        
        for chunk_blocks in all_blocks:
            for block_name, block_content in chunk_blocks.items():
                if block_content:
                    if block_name == "projects":
                        # Handle projects as list
                        if isinstance(block_content, list):
                            combined[block_name].extend(block_content)
                        else:
                            # Split string into projects
                            projects = [p.strip() for p in str(block_content).split('\n') if p.strip()]
                            combined[block_name].extend(projects)
                    else:
                        # Handle other blocks as strings
                        if isinstance(block_content, list):
                            # Convert list to string
                            block_content = ", ".join(str(item) for item in block_content)
                        
                        if isinstance(block_content, str) and block_content.strip():
                            if combined[block_name]:
                                combined[block_name] += "\n\n" + block_content
                            else:
                                combined[block_name] = block_content
        
        return combined


# Function for backward compatibility
def parse_resume(text: str) -> Dict[str, str]:
    """Convenient function for resume parsing"""
    parser = ResumeParser()
    return parser.parse_resume(text)
