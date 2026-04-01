import pytesseract
from PIL import Image
import pdfplumber
import os
from typing import Dict, Any


class OCRTool:
    """OCR tool for extracting text from documents."""

    name = "ocr_tool"
    description = "Extract text from images (JPEG/PNG) using pytesseract and PDFs using pdfplumber"

    input_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to process"
            },
            "file_type": {
                "type": "string",
                "enum": ["jpg", "jpeg", "png", "pdf"],
                "description": "Type of the file"
            }
        },
        "required": ["file_path", "file_type"]
    }

    @staticmethod
    def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a file with OCR and extract text.

        Args:
            input_data: Dictionary with file_path and file_type

        Returns:
            Dictionary with extracted text, page count, and confidence
        """
        file_path = input_data.get("file_path")
        file_type = input_data.get("file_type").lower()

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        result = {
            "text": "",
            "pages": 0,
            "confidence": 0.0
        }

        try:
            if file_type in ["jpg", "jpeg", "png"]:
                # Process image with pytesseract
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image)

                # Get confidence data if available
                try:
                    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                    confidences = [int(conf) for conf in data['conf'] if conf != '-1']
                    result["confidence"] = sum(confidences) / len(confidences) if confidences else 0.0
                except:
                    result["confidence"] = 0.0

                result["text"] = text.strip()
                result["pages"] = 1

            elif file_type == "pdf":
                # Process PDF with pdfplumber
                all_text = []
                confidences = []

                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages, 1):
                        text = page.extract_text()
                        if text:
                            all_text.append(text.strip())

                            # Extract words with confidence if available
                            try:
                                words = page.extract_words()
                                page_confidences = [float(word.get('confidence', 0)) for word in words if word.get('confidence')]
                                confidences.extend(page_confidences)
                            except:
                                pass

                    result["pages"] = len(pdf.pages)

                result["text"] = "\n\n".join(all_text)
                result["confidence"] = sum(confidences) / len(confidences) if confidences else 0.0

            else:
                raise ValueError(f"Unsupported file type: {file_type}")

        except Exception as e:
            raise RuntimeError(f"Error processing file: {str(e)}")

        return result
