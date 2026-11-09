"""Super-optimized in-memory barcode and QR scanner using PyMuPDF and zxing-cpp."""

from typing import List
import fitz
from PIL import Image
import zxingcpp

def scan_pixmap(pixmap: fitz.Pixmap) -> List[str]:
    """Scan a PyMuPDF Pixmap in-memory for barcodes/QR codes without disk I/O.
    
    Args:
        pixmap: PyMuPDF pixmap object.
        
    Returns:
        List of decoded barcode string contents.
    """
    # If the pixmap is CMYK or has an alpha channel, convert to RGB
    if pixmap.colorspace.n != 3 or pixmap.alpha:
        rgb_pixmap = fitz.Pixmap(fitz.csRGB, pixmap)
    else:
        rgb_pixmap = pixmap

    # Convert directly to PIL Image using raw memory buffer
    img = Image.frombytes("RGB", [rgb_pixmap.width, rgb_pixmap.height], rgb_pixmap.samples)
    
    # Fast native C++ barcode decode
    results = zxingcpp.read_barcodes(img)
    
    decoded_texts = [r.text for r in results if r.text]
    return decoded_texts

def scan_page(doc_path: str, page_num: int, dpi: int = 150) -> List[str]:
    """Scan a specific page of a PDF file for barcodes and QR codes.
    
    Args:
        doc_path: Path to the PDF file.
        page_num: 0-based page index.
        dpi: Rendering DPI (150 is the optimal speed/accuracy trade-off).
        
    Returns:
        List of decoded barcode text strings found on the page.
    """
    doc = fitz.open(doc_path)
    try:
        if page_num < 0 or page_num >= len(doc):
            return []
        page = doc[page_num]
        
        # 1. Fast path: Direct embedded image check if page has a single full-page scan
        img_list = page.get_images(full=True)
        if len(img_list) == 1:
            xref = img_list[0][0]
            try:
                base_img = doc.extract_image(xref)
                if base_img and "image" in base_img:
                    raw_pix = fitz.Pixmap(doc, xref)
                    found = scan_pixmap(raw_pix)
                    if found:
                        return found
            except Exception:
                pass
                
        # 2. Rendered path: Render page directly to memory pixmap
        pix = page.get_pixmap(dpi=dpi)
        return scan_pixmap(pix)
    finally:
        doc.close()
