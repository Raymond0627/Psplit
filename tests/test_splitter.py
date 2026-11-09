import io
import os
import fitz
import qrcode
import pytest
from src.core.splitter import PdfSplitter

def create_multi_page_pdf(path, pages_data):
    """Create a test PDF with given pages. 
    pages_data is a list of tuples: (is_separator, separator_text)
    """
    doc = fitz.open()
    for is_sep, text in pages_data:
        page = doc.new_page(width=595, height=842)
        if is_sep:
            qr = qrcode.QRCode(box_size=10, border=2)
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            b = io.BytesIO()
            img.save(b, format='PNG')
            page.insert_image(fitz.Rect(100, 100, 300, 300), stream=b.getvalue())
        else:
            page.insert_text(fitz.Point(100, 100), "Normal Document Page")
    doc.save(path)
    doc.close()

@pytest.fixture
def multi_doc_pdf(tmp_path):
    # Document structure:
    # Page 0: Normal page
    # Page 1: Normal page
    # Page 2: Separator "DOCSEP"
    # Page 3: Normal page
    # Page 4: Separator "DOCSEP"
    # Page 5: Normal page
    pdf_path = str(tmp_path / "multi_doc.pdf")
    pages = [
        (False, ""),
        (False, ""),
        (True, "DOCSEP"),
        (False, ""),
        (True, "DOCSEP"),
        (False, "")
    ]
    create_multi_page_pdf(pdf_path, pages)
    return pdf_path

def test_split_discard_mode(multi_doc_pdf, tmp_path):
    out_dir = str(tmp_path / "out_discard")
    splitter = PdfSplitter()
    result = splitter.split(
        pdf_path=multi_doc_pdf,
        output_dir=out_dir,
        separator_text="DOCSEP",
        mode="discard"
    )
    # Should generate 3 documents:
    # Doc 1: Pages 0, 1 (2 pages)
    # Doc 2: Page 3 (1 page)
    # Doc 3: Page 5 (1 page)
    assert len(result.output_files) == 3
    doc1 = fitz.open(result.output_files[0])
    assert len(doc1) == 2
    doc1.close()
    
    doc2 = fitz.open(result.output_files[1])
    assert len(doc2) == 1
    doc2.close()
    
    doc3 = fitz.open(result.output_files[2])
    assert len(doc3) == 1
    doc3.close()

def test_split_keep_prev_mode(multi_doc_pdf, tmp_path):
    out_dir = str(tmp_path / "out_prev")
    splitter = PdfSplitter()
    result = splitter.split(
        pdf_path=multi_doc_pdf,
        output_dir=out_dir,
        separator_text="DOCSEP",
        mode="keep_prev"
    )
    # Doc 1: Pages 0, 1, 2 (3 pages, separator kept at end of doc 1)
    # Doc 2: Pages 3, 4 (2 pages, separator kept at end of doc 2)
    # Doc 3: Page 5 (1 page)
    assert len(result.output_files) == 3
    doc1 = fitz.open(result.output_files[0])
    assert len(doc1) == 3
    doc1.close()
    
    doc2 = fitz.open(result.output_files[1])
    assert len(doc2) == 2
    doc2.close()

def test_split_keep_next_mode(multi_doc_pdf, tmp_path):
    out_dir = str(tmp_path / "out_next")
    splitter = PdfSplitter()
    result = splitter.split(
        pdf_path=multi_doc_pdf,
        output_dir=out_dir,
        separator_text="DOCSEP",
        mode="keep_next"
    )
    # Doc 1: Pages 0, 1 (2 pages)
    # Doc 2: Pages 2, 3 (2 pages, separator kept at start of doc 2)
    # Doc 3: Pages 4, 5 (2 pages, separator kept at start of doc 3)
    assert len(result.output_files) == 3
    doc1 = fitz.open(result.output_files[0])
    assert len(doc1) == 2
    doc1.close()
    
    doc2 = fitz.open(result.output_files[1])
    assert len(doc2) == 2
    doc2.close()

def test_split_consecutive_and_first_page_separators(tmp_path):
    # Page 0: Separator "DOCSEP"
    # Page 1: Normal page
    # Page 2: Separator "DOCSEP"
    # Page 3: Separator "DOCSEP"
    # Page 4: Normal page
    pdf_path = str(tmp_path / "edge_case.pdf")
    pages = [
        (True, "DOCSEP"),
        (False, ""),
        (True, "DOCSEP"),
        (True, "DOCSEP"),
        (False, "")
    ]
    create_multi_page_pdf(pdf_path, pages)
    out_dir = str(tmp_path / "out_edge")
    splitter = PdfSplitter()
    result = splitter.split(
        pdf_path=pdf_path,
        output_dir=out_dir,
        separator_text="DOCSEP",
        mode="discard"
    )
    # Page 0 discarded
    # Doc 1: Page 1 (1 page)
    # Page 2, 3 discarded
    # Doc 2: Page 4 (1 page)
    assert len(result.output_files) == 2
    doc1 = fitz.open(result.output_files[0])
    assert len(doc1) == 1
    doc1.close()
    
    doc2 = fitz.open(result.output_files[1])
    assert len(doc2) == 1
    doc2.close()

def test_split_regex_matching(tmp_path):
    pdf_path = str(tmp_path / "regex_test.pdf")
    pages = [
        (False, ""),
        (True, "SEP-2026-X"),
        (False, "")
    ]
    create_multi_page_pdf(pdf_path, pages)
    out_dir = str(tmp_path / "out_regex")
    splitter = PdfSplitter()
    result = splitter.split(
        pdf_path=pdf_path,
        output_dir=out_dir,
        separator_text=r"SEP-\d{4}-[A-Z]",
        match_type="regex",
        mode="discard"
    )
    assert len(result.output_files) == 2

