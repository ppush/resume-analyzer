import fitz
import io
from fastapi import UploadFile
from typing import List, Dict, Any

async def read_resume_as_html_chunks(file: UploadFile) -> List[Dict[str, Any]]:
    """
    Read resume file and return as HTML chunks for better structure preservation
    
    Args:
        file: Uploaded file
        
    Returns:
        List of HTML chunks with metadata
    """
    content = await file.read()
    filename = file.filename.lower()
    
    if filename.endswith(".docx"):
        # Convert DOCX to HTML using mammoth
        try:
            import mammoth
            result = mammoth.convert_to_html(io.BytesIO(content))
            html_content = result.value
            
            # Process HTML with chunker
            from services.html_chunker import HTMLChunker
            chunker = HTMLChunker(chunk_size=50)
            chunks = chunker.process_html(html_content)
            
            return chunks
            
        except ImportError:
            raise ValueError("mammoth library is required for HTML chunking")
    
    elif filename.endswith(".pdf"):
        # For PDF, convert directly to HTML using PyMuPDF
        html_content = ""
        with fitz.open(stream=content, filetype="pdf") as doc:
            for page_num, page in enumerate(doc):
                # Get HTML from page
                page_html = page.get_text("html")
                
                # Add page separator for multi-page documents
                if page_num > 0:
                    html_content += "\n\n<!-- PAGE BREAK -->\n\n"
                
                html_content += page_html
        
        # Process with chunker
        from services.html_chunker import HTMLChunker
        chunker = HTMLChunker(chunk_size=50)
        chunks = chunker.process_html(html_content)
        
        return chunks
    
    else:
        raise ValueError("Unsupported file format for HTML chunking")
