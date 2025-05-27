#!/usr/bin/env python3
# disableDuplicate.py - A tool to read QR codes from PDF files

import fitz  # PyMuPDF
import io
import cv2
import numpy as np
import os
import pandas as pd
from PIL import Image
from pyzbar.pyzbar import decode

def extract_images_from_pdf(pdf_path):
    """
    Extract all images from a PDF file
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of PIL Image objects
    """
    pdf_document = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        image_list = page.get_images(full=True)
        
        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]  # get the XREF of the image
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Convert bytes to PIL Image object
            image = Image.open(io.BytesIO(image_bytes))
            images.append(image)
            
    pdf_document.close()
    return images

def preprocess_image_for_qr(image):
    """
    Apply image preprocessing to improve QR code detection
    
    Args:
        image: PIL Image object
        
    Returns:
        Processed OpenCV image
    """
    # Convert PIL to OpenCV
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh

def decode_qr_from_image(image, pdf_page=None, page_num=None):
    """
    Detect and decode QR codes from an image
    
    Args:
        image: PIL Image object
        pdf_page: PyMuPDF page object (optional, for text extraction)
        page_num: Page number (optional, for reference)
        
    Returns:
        List of dicts containing QR data and associated information
    """
    # Convert PIL image to opencv format
    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Try normal detection first
    decoded_objects = decode(opencv_image)
    
    # If no QR codes found, try with preprocessing
    if not decoded_objects:
        processed_image = preprocess_image_for_qr(image)
        decoded_objects = decode(processed_image)
    
    results = []
    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            qr_data = obj.data.decode('utf-8')
            
            # Create result dict with QR code data and bounding box
            qr_result = {
                'qr_value': qr_data,
                'page': page_num,
                'rect': obj.rect,
                'nearby_text': None
            }
            
            # Extract text near QR code if the PDF page is provided
            if pdf_page is not None:
                # Convert coordinates from pyzbar (OpenCV) to PyMuPDF format
                # Note: This is an approximation as coordinate systems differ
                img_height, img_width = opencv_image.shape[:2]
                pdf_width, pdf_height = pdf_page.rect.width, pdf_page.rect.height
                
                # QR code bounding box
                qr_x, qr_y, qr_w, qr_h = obj.rect
                
                # Scale to PDF coordinates
                pdf_x0 = qr_x * pdf_width / img_width
                pdf_y0 = qr_y * pdf_height / img_height
                pdf_x1 = (qr_x + qr_w) * pdf_width / img_width
                pdf_y1 = (qr_y + qr_h) * pdf_height / img_height
                
                # Extend the search area slightly
                margin = 50  # PDF points
                search_rect = fitz.Rect(
                    max(0, pdf_x0 - margin),
                    max(0, pdf_y0 - margin),
                    min(pdf_width, pdf_x1 + margin),
                    min(pdf_height, pdf_y1 + margin)
                )
                
                # Extract text within the search area
                text_in_area = pdf_page.get_text("text", clip=search_rect)
                qr_result['nearby_text'] = text_in_area.strip()
            
            results.append(qr_result)
            
    return results

def extract_qr_from_pdf_pages(pdf_path, dpi=300):
    """
    Render each page of a PDF and scan for QR codes
    
    Args:
        pdf_path: Path to the PDF file
        dpi: Resolution for page rendering (higher is better for QR detection)
        
    Returns:
        List of dicts containing QR code values and associated information
    """
    pdf_document = fitz.open(pdf_path)
    all_qr_codes = []
    
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        
        # Render page to an image (higher dpi for better quality)
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
        img_data = pix.tobytes("png")
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(img_data))
        
        # Decode QR codes and pass the page object for text extraction
        qr_codes = decode_qr_from_image(image, pdf_page=page, page_num=page_num + 1)
        all_qr_codes.extend(qr_codes)
    
    pdf_document.close()
    return all_qr_codes

def read_qr_codes_from_pdf(pdf_path, use_extracted_images=True, use_rendered_pages=True, dpi=300):
    """
    Extract and decode QR codes from a PDF file using multiple methods
    
    Args:
        pdf_path: Path to the PDF file
        use_extracted_images: Whether to try extracting images from PDF
        use_rendered_pages: Whether to try rendering whole pages
        dpi: Resolution for page rendering
        
    Returns:
        List of dicts containing QR code values and associated information
    """
    all_qr_codes = []
    
    # Method 1: Extract embedded images and scan them for QR codes
    if use_extracted_images:
        images = extract_images_from_pdf(pdf_path)
        for image in images:
            qr_codes = decode_qr_from_image(image)
            all_qr_codes.extend(qr_codes)
    
    # Method 2: Render each page and scan for QR codes
    if use_rendered_pages and (not all_qr_codes or not use_extracted_images):
        page_qr_codes = extract_qr_from_pdf_pages(pdf_path, dpi)
        
        # Only add unique QR codes not already found
        for qr_code in page_qr_codes:
            if qr_code not in all_qr_codes:
                all_qr_codes.append(qr_code)
    
    return all_qr_codes


def save_results_to_excel(qr_results, output_path, source_file=None):
    """
    Save QR code results to Excel file
    
    Args:
        qr_results: List of dictionaries containing QR code information
        output_path: Path to save Excel file
        source_file: Source PDF filename (optional, for unified Excel files)
    """
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(qr_results)
    
    # If no QR codes found, return an empty DataFrame with correct columns
    if df.empty and source_file:
        return pd.DataFrame(columns=['Source PDF', 'QR Code Value', 'Page', 'Nearby Text'])
    
    # Reorder columns for better readability
    columns = ['qr_value', 'page', 'nearby_text']
    for col in columns:
        if col not in df.columns:
            df[col] = None
            
    # Only include the columns we want in the Excel file
    df = df[columns]
    
    # Add source file column if provided
    if source_file:
        df.insert(0, 'source_file', source_file)
    
    # Rename columns for better readability
    column_mapping = {
        'qr_value': 'QR Code Value', 
        'page': 'Page', 
        'nearby_text': 'Nearby Text'
    }
    if source_file:
        column_mapping['source_file'] = 'Source PDF'
        
    df = df.rename(columns=column_mapping)
    
    # Save to Excel
    df.to_excel(output_path, index=False)
    
    return df

def main():
    """
    Main function to demonstrate QR code extraction from PDF
    """
    import argparse
    import os
    import sys
    
    parser = argparse.ArgumentParser(description='Extract QR codes from PDF files')
    parser.add_argument('path', nargs='?', help='Path to a PDF file or directory containing PDFs')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for page rendering (default: 300)')
    parser.add_argument('--images-only', action='store_true', help='Only use extracted images (no page rendering)')
    parser.add_argument('--pages-only', action='store_true', help='Only use page rendering (no image extraction)')
    parser.add_argument('--skip-excel', action='store_true', help='Skip saving results to Excel files')
    parser.add_argument('--output-dir', help='Directory to save Excel results')
    parser.add_argument('--excel-name', help='Name for the unified Excel file (default: QRCodeResults.xlsx)')
    parser.add_argument('--individual-excels', action='store_true', help='Create individual Excel files for each PDF instead of a unified file')
    
    args = parser.parse_args()
    
    # If path wasn't provided as an argument, prompt the user for it
    path = args.path
    if path is None:
        print("Enter the path to a PDF file or directory containing PDFs:")
        print("(do not add quotes even if the path contains spaces)")
        path = input("> ").strip()
        
        # Remove any surrounding quotes that users might add
        path = path.strip("'\"")
        
        # Check if the path exists
        if not os.path.exists(path):
            print(f"Error: Path '{path}' not found.")
            sys.exit(1)
    
    # Set method flags based on arguments
    use_extracted_images = not args.pages_only
    use_rendered_pages = not args.images_only
    
    # Determine output directory for Excel files
    output_dir = args.output_dir if args.output_dir else None
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Determine Excel filename for unified results
    unified_excel = None
    if not args.skip_excel and not args.individual_excels:
        excel_name = args.excel_name
        if not excel_name:
            print("\nEnter a name for the unified Excel file (default: QRCodeResults.xlsx):")
            excel_name = input("> ").strip() or "QRCodeResults.xlsx"
            
            # Add .xlsx extension if not provided
            if not excel_name.lower().endswith(".xlsx"):
                excel_name += ".xlsx"
        
        # Determine the full path for the Excel file
        if output_dir:
            unified_excel = os.path.join(output_dir, excel_name)
        else:
            if os.path.isdir(path):
                unified_excel = os.path.join(path, excel_name)
            else:
                unified_excel = os.path.join(os.path.dirname(path), excel_name)
    
    # Process single PDF file or directory of PDFs
    all_results = []  # For storing all QR codes for unified Excel file
    
    if os.path.isfile(path) and path.lower().endswith('.pdf'):
        # Process single PDF file
        qr_results = process_pdf(path, use_extracted_images, use_rendered_pages, args.dpi, 
                               args.individual_excels and not args.skip_excel, output_dir)
        if qr_results:
            # Add source file info to each result
            source_file = os.path.basename(path)
            for result in qr_results:
                result['source_file'] = source_file
            all_results.extend(qr_results)
            
    elif os.path.isdir(path):
        # Process directory of PDF files
        pdf_files = [f for f in os.listdir(path) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print(f"No PDF files found in directory: {path}")
            sys.exit(1)
        
        print(f"Found {len(pdf_files)} PDF files to process...")
        
        for i, pdf_file in enumerate(pdf_files, 1):
            pdf_path = os.path.join(path, pdf_file)
            print(f"\nProcessing file {i}/{len(pdf_files)}: {pdf_file}")
            qr_results = process_pdf(pdf_path, use_extracted_images, use_rendered_pages, args.dpi, 
                                   args.individual_excels and not args.skip_excel, output_dir)
            if qr_results:
                # Add source file info to each result
                for result in qr_results:
                    result['source_file'] = pdf_file
                all_results.extend(qr_results)
    else:
        print(f"Error: '{path}' is not a PDF file or directory.")
        sys.exit(1)
        
    # Save unified Excel file if needed
    if all_results and unified_excel and not args.skip_excel:
        save_results_to_excel(all_results, unified_excel, source_file=True)
        print(f"\nAll results saved to unified Excel file: {unified_excel}")


def process_pdf(pdf_path, use_extracted_images, use_rendered_pages, dpi, save_excel=True, output_dir=None):
    """
    Process a single PDF file
    
    Returns:
        List of QR code information dictionaries, or None if no QR codes found
    """
    # Extract QR codes
    qr_codes = read_qr_codes_from_pdf(
        pdf_path, 
        use_extracted_images=use_extracted_images,
        use_rendered_pages=use_rendered_pages,
        dpi=dpi
    )
    
    # Print results
    if qr_codes:
        print(f"Found {len(qr_codes)} QR code(s) in {os.path.basename(pdf_path)}:")
        for i, code in enumerate(qr_codes, 1):
            qr_value = code['qr_value']
            page_num = code['page'] if code['page'] is not None else 'Unknown'
            nearby_text = code['nearby_text'] if code['nearby_text'] else 'None'
            
            print(f"QR Code {i}: {qr_value}")
            print(f"  Page: {page_num}")
            print(f"  Nearby Text: {nearby_text[:100]}{'...' if len(nearby_text) > 100 else ''}")
        
        # Save results to Excel if requested
        if save_excel:
            # Generate Excel filename from PDF filename
            pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]
            if output_dir:
                excel_path = os.path.join(output_dir, f"{pdf_basename}.xlsx")
            else:
                excel_path = os.path.join(os.path.dirname(pdf_path), f"{pdf_basename}.xlsx")
            
            # Save to Excel
            save_results_to_excel(qr_codes, excel_path)
            print(f"Results saved to {excel_path}")
        
        return qr_codes
    else:
        print(f"No QR codes found in {os.path.basename(pdf_path)}.")
        return None

if __name__ == "__main__":
    main()