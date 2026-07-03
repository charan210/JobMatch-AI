import io
from unittest.mock import patch, MagicMock
import pytest

from ai_engine.parsers.pdf_parser import PdfParser
from ai_engine.parsers.docx_parser import DocxParser
from ai_engine.exceptions import ParserError

@patch('ai_engine.parsers.pdf_parser.PdfReader')
def test_pdf_parser(mock_pdf_reader):
    mock_page_1 = MagicMock()
    mock_page_1.extract_text.return_value = "Page 1 text."
    
    mock_page_2 = MagicMock()
    mock_page_2.extract_text.return_value = "Page 2 text."
    
    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [mock_page_1, mock_page_2]
    mock_pdf_reader.return_value = mock_reader_instance

    parser = PdfParser()
    dummy_file = io.BytesIO(b"dummy pdf content")
    text = parser.parse(dummy_file)

    assert text == "Page 1 text.\nPage 2 text."

@patch('ai_engine.parsers.pdf_parser.PdfReader')
def test_pdf_parser_error(mock_pdf_reader):
    mock_pdf_reader.side_effect = Exception("Corrupt PDF")
    
    parser = PdfParser()
    dummy_file = io.BytesIO(b"corrupt")
    
    with pytest.raises(ParserError):
        parser.parse(dummy_file)

@patch('ai_engine.parsers.docx_parser.docx.Document')
def test_docx_parser(mock_docx_document):
    mock_para_1 = MagicMock()
    mock_para_1.text = "Paragraph 1"
    
    mock_para_2 = MagicMock()
    mock_para_2.text = "Paragraph 2"
    
    mock_doc_instance = MagicMock()
    mock_doc_instance.paragraphs = [mock_para_1, mock_para_2]
    mock_docx_document.return_value = mock_doc_instance

    parser = DocxParser()
    dummy_file = io.BytesIO(b"dummy docx content")
    text = parser.parse(dummy_file)

    assert text == "Paragraph 1\nParagraph 2"

@patch('ai_engine.parsers.docx_parser.docx.Document')
def test_docx_parser_error(mock_docx_document):
    mock_docx_document.side_effect = Exception("Corrupt DOCX")
    
    parser = DocxParser()
    dummy_file = io.BytesIO(b"corrupt")
    
    with pytest.raises(ParserError):
        parser.parse(dummy_file)
