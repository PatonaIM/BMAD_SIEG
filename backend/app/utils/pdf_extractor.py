"""PDF text extraction utility using pdfplumber."""
from io import BytesIO

import pdfplumber
import structlog

logger = structlog.get_logger(__name__)


class PDFTextExtractor:
    """Utility for extracting text from PDF files."""

    @staticmethod
    def extract_text(pdf_bytes: bytes) -> str:
        """
        Extract text content from PDF bytes.

        Args:
            pdf_bytes: Raw PDF file bytes

        Returns:
            Extracted text as string

        Raises:
            ValueError: If no text content could be extracted from PDF
            Exception: If PDF is corrupted or cannot be read
        """
        try:
            text_parts = []

            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                        logger.debug(
                            "pdf_page_extracted",
                            page_num=page_num,
                            text_length=len(page_text),
                        )

            full_text = "\n\n".join(text_parts)

            if not full_text.strip():
                logger.error("pdf_extraction_empty", pdf_size_bytes=len(pdf_bytes))
                raise ValueError("No text content extracted from PDF")

            logger.info(
                "pdf_text_extracted_successfully",
                pdf_size_bytes=len(pdf_bytes),
                total_text_length=len(full_text),
                pages_extracted=len(text_parts),
            )

            return full_text

        except ValueError:
            # Re-raise ValueError for empty PDFs
            raise
        except Exception as e:
            logger.error(
                "pdf_extraction_failed",
                pdf_size_bytes=len(pdf_bytes),
                error=str(e),
                error_type=type(e).__name__,
            )
            raise Exception(f"Failed to extract text from PDF: {str(e)}") from e
