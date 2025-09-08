#!/usr/bin/env python3
"""
HTML chunker for resume processing
Cleans HTML and splits into chunks for LLM processing
"""

import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class HTMLChunker:
    """HTML chunker for resume processing"""
    
    def __init__(self, chunk_size: int = 50):
        """
        Initialize HTML chunker
        
        Args:
            chunk_size: Number of tags per chunk for regular content
        """
        self.chunk_size = chunk_size
    
    def clean_html(self, html_content: str) -> str:
        """
        Clean HTML content by removing images and empty tags
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Cleaned HTML content
        """
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove all img tags
            for img in soup.find_all('img'):
                img.decompose()
            
            # Remove all style attributes to reduce size
            for tag in soup.find_all(attrs={'style': True}):
                del tag['style']
            
            # Remove empty tags (tags with no content or only whitespace)
            for tag in soup.find_all():
                if tag.string is None and not tag.contents:
                    # Tag has no content
                    tag.decompose()
                elif tag.string and not tag.string.strip():
                    # Tag has only whitespace
                    tag.decompose()
            
            # Get cleaned HTML
            cleaned_html = str(soup)
            
            logger.info(f"HTML cleaned: removed images, styles, and empty tags")
            return cleaned_html
            
        except Exception as e:
            logger.error(f"Error cleaning HTML: {e}")
            return html_content
    
    def split_html_into_chunks(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Split HTML into chunks according to specified rules
        
        Args:
            html_content: Cleaned HTML content
            
        Returns:
            List of chunks with metadata
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            body = soup.find('body')
            
            if not body:
                logger.warning("No body tag found, using entire document")
                body = soup
            
            chunks = []
            current_chunk = []
            current_chunk_type = "regular"
            
            # Process all direct children of body
            for element in body.children:
                if hasattr(element, 'name') and element.name:  # Skip text nodes and None names
                    element_name = element.name.lower()
                    
                    # Check for special elements (table, ul)
                    if element_name in ['table', 'ul']:
                        # Save current chunk if it exists
                        if current_chunk:
                            chunks.append({
                                'type': current_chunk_type,
                                'content': ''.join(current_chunk),
                                'size': len(current_chunk)
                            })
                            current_chunk = []
                        
                        # Create chunk for table/ul and previous element
                        chunk_content = []
                        
                        # Add previous element if it exists
                        if chunks and chunks[-1]['type'] == 'regular':
                            # Get the last element from previous chunk
                            prev_chunk = chunks[-1]
                            if prev_chunk['content']:
                                chunk_content.append(prev_chunk['content'])
                                # Remove it from previous chunk
                                chunks[-1]['content'] = ''
                                chunks[-1]['size'] = 0
                        
                        # Add current element
                        chunk_content.append(str(element))
                        
                        chunks.append({
                            'type': f'{element_name}_special',
                            'content': ''.join(chunk_content),
                            'size': len(chunk_content)
                        })
                        
                        current_chunk_type = "regular"
                    
                    elif element_name == 'div':
                        # Special handling for div elements (common in PDF)
                        # Check if div contains many paragraphs (PDF structure)
                        div_children = [child for child in element.children if hasattr(child, 'name') and child.name]
                        p_count = sum(1 for child in div_children if child.name.lower() == 'p')
                        
                        if p_count > self.chunk_size:
                            # Split div by paragraphs
                            div_chunks = self._split_div_by_paragraphs(element, self.chunk_size)
                            for div_chunk in div_chunks:
                                chunks.append({
                                    'type': 'div_split',
                                    'content': div_chunk,
                                    'size': 1
                                })
                        else:
                            # Regular div processing
                            current_chunk.append(str(element))
                            
                            # Check if chunk is full
                            if len(current_chunk) >= self.chunk_size:
                                chunks.append({
                                    'type': current_chunk_type,
                                    'content': ''.join(current_chunk),
                                    'size': len(current_chunk)
                                })
                                current_chunk = []
                                current_chunk_type = "regular"
                    
                    else:
                        # Regular element
                        current_chunk.append(str(element))
                        
                        # Check if chunk is full
                        if len(current_chunk) >= self.chunk_size:
                            chunks.append({
                                'type': current_chunk_type,
                                'content': ''.join(current_chunk),
                                'size': len(current_chunk)
                            })
                            current_chunk = []
                            current_chunk_type = "regular"
            
            # Add remaining chunk
            if current_chunk:
                chunks.append({
                    'type': current_chunk_type,
                    'content': ''.join(current_chunk),
                    'size': len(current_chunk)
                })
            
            # Filter out empty chunks
            chunks = [chunk for chunk in chunks if chunk['content'].strip()]
            
            logger.info(f"HTML split into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting HTML: {e}")
            return [{'type': 'error', 'content': html_content, 'size': 1}]
    
    def _split_div_by_paragraphs(self, div_element, chunk_size: int) -> List[str]:
        """
        Split div element by paragraphs for better PDF handling
        
        Args:
            div_element: BeautifulSoup div element
            chunk_size: Number of paragraphs per chunk
            
        Returns:
            List of HTML chunks
        """
        try:
            # Get all paragraph elements
            paragraphs = div_element.find_all('p')
            
            if not paragraphs:
                # No paragraphs found, return the whole div
                return [str(div_element)]
            
            chunks = []
            current_chunk_paragraphs = []
            
            for i, p in enumerate(paragraphs):
                current_chunk_paragraphs.append(p)
                
                # Check if we should create a chunk
                if len(current_chunk_paragraphs) >= chunk_size or i == len(paragraphs) - 1:
                    # Create a new div with current paragraphs
                    from bs4 import BeautifulSoup
                    new_div = BeautifulSoup('<div></div>', 'html.parser').div
                    new_div.attrs = div_element.attrs.copy()  # Copy attributes
                    
                    for p_elem in current_chunk_paragraphs:
                        new_div.append(p_elem)
                    
                    chunks.append(str(new_div))
                    current_chunk_paragraphs = []
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting div by paragraphs: {e}")
            return [str(div_element)]
    
    def process_html(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Complete HTML processing: clean and chunk
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            List of processed chunks
        """
        # Clean HTML
        cleaned_html = self.clean_html(html_content)
        
        # Split into chunks
        chunks = self.split_html_into_chunks(cleaned_html)
        
        return chunks
