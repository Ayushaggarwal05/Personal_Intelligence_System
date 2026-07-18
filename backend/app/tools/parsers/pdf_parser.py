from typing import Dict, Any, List
from app.core.logging import logger

def parse_pdf_file(file_path: str) -> Dict[str, Any]:
    """Parses a PDF file page-by-page using pypdf and returns structured text lists."""
    pages = []
    
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        
        for idx, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if text:
                pages.append({
                    "page_num": idx,
                    "text": text.strip()
                })
        
        logger.info(f"Parsed {len(pages)} pages from PDF: {file_path}")
    except ImportError:
        logger.warning(
            "pypdf package is not installed. PDF parsing skipped. "
            "Please run 'pip install pypdf' to enable local PDF support."
        )
    except Exception as e:
        logger.error(f"Error parsing PDF file {file_path}: {e}")
        
    return {
        "pages": pages
    }
