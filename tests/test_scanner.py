import os
import io
import fitz
import qrcode
import pytest
from PIL import Image
from src.core.scanner import scan_page, scan_pixmap

@pytest.fixture
def sample_pdf_with_qr(tmp_path):
    pdf_path = tmp_path / "test_qr.pdf"
    doc = fitz.open()
    page = doc.new_page(width=595, height=842) # A4 size
    
    # Generate QR Code image in memory
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data("DOCSEP")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    img_byte_arr = io.BytesIO()
    qr_img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    
    # Insert QR into page rect
    rect = fitz.Rect(100, 100, 300, 300)
    page.insert_image(rect, stream=img_bytes)
    
    # Add a blank page
    doc.new_page(width=595, height=842)
    
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)

def test_scan_page_detects_qr(sample_pdf_with_qr):
    # Page 0 has DOCSEP QR
    barcodes = scan_page(sample_pdf_with_qr, page_num=0)
    assert "DOCSEP" in barcodes

import barcode
from barcode.writer import ImageWriter

@pytest.fixture
def sample_pdf_with_code128(tmp_path):
    pdf_path = tmp_path / "test_code128.pdf"
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    
    # Generate Code 128 barcode image
    code128_class = barcode.get_barcode_class('code128')
    c128 = code128_class('DOCSEP', writer=ImageWriter())
    img_byte_arr = io.BytesIO()
    c128.write(img_byte_arr)
    img_bytes = img_byte_arr.getvalue()
    
    rect = fitz.Rect(100, 100, 450, 250)
    page.insert_image(rect, stream=img_bytes)
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)

def test_scan_page_detects_code128(sample_pdf_with_code128):
    barcodes = scan_page(sample_pdf_with_code128, page_num=0)
    assert "DOCSEP" in barcodes

