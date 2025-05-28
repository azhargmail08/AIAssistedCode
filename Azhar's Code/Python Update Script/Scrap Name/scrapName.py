import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright
from datetime import datetime
import getpass

# Create required folders if they don't exist
required_folders = ['logs', 'screenshots', 'scraped_data']
for folder in required_folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created {folder} directory")

def clean_path(path: str) -> str:
    return path.strip().strip("'\"")

async def take_error_screenshot(page, school_code, error_type):
    """Take a screenshot of the current page state"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join("screenshots", f"{timestamp}_{school_code}_{error_type}.png")
    try:
        await page.screenshot(path=screenshot_path)
        return screenshot_path
    except Exception as e:
        print(f"Failed to take screenshot: {e}")
        return None

async def scrape_student_data(page, school_id, school_code):
    """
    Scrape columns 2-5 from the student table for a specific school ID
    and save it to an Excel file named after the school code.
    Also separates the name and ID from column 3 into separate columns.
    """
    print(f"\n===== SCRAPING STUDENT DATA FOR {school_code} =====")
    student_url = f"https://crm.studentqr.com/school/{school_id}/student"
    
    # Data to store all student information
    all_students = []
    
    # Navigate to the student page
    await page.goto(student_url)
    await asyncio.sleep(1)
    
    # Determine total pages
    total_pages = 1
    try:
        pagination = await page.query_selector(".pagination")
        if pagination:
            page_links = await pagination.query_selector_all("a")
            page_numbers = []
            for link in page_links:
                text = (await link.inner_text()).strip()
                if text.isdigit():
                    page_numbers.append(int(text))
            if page_numbers:
                total_pages = max(page_numbers)
    except Exception:
        total_pages = 1
        
    print(f"Found {total_pages} pages of students")
    
    # Get column headers from the first page
    headers = []
    name_column_index = -1  # To track which column contains the name and ID
    
    try:
        scan_table = await page.wait_for_selector("#studentTable", timeout=10000)
        header_row = await scan_table.query_selector("tr")
        header_cells = await header_row.query_selector_all("th")
        
        # Get headers for columns 2-5 (0-indexed, so indices 1-4)
        if len(header_cells) >= 5:
            for i in range(1, 5):  # Get columns at index 1, 2, 3, 4 (2nd to 5th columns)
                header_text = await header_cells[i].inner_text()
                if i == 2:  # Column 3 (index 2) typically contains the Name and ID
                    name_column_index = len(headers)  # Remember where the name column is in our array
                    # Instead of adding the original header, we'll add two new headers
                    headers.append("Name")
                    headers.append("ID")
                else:
                    headers.append(header_text.strip())
            
            print(f"Table headers (modified): {headers}")
        else:
            print(f"Not enough columns in table, found {len(header_cells)} columns")
            headers = ["Column 2", "Name", "ID", "Column 4", "Column 5"]
            name_column_index = 1  # Name is the second column in our headers list
    except Exception as e:
        print(f"Error getting table headers: {e}")
        headers = ["Column 2", "Name", "ID", "Column 4", "Column 5"]
        name_column_index = 1  # Name is the second column in our headers list
    
    # Scan all pages to get complete student data
    for scan_page in range(1, total_pages + 1):
        scan_page_url = f"{student_url}?page={scan_page}" if scan_page > 1 else student_url
        print(f"Scanning student page {scan_page} of {total_pages}")
        await page.goto(scan_page_url)
        await asyncio.sleep(1)
        
        try:
            scan_table = await page.wait_for_selector("#studentTable", timeout=10000)
            scan_rows = await scan_table.query_selector_all("tr")
            
            # Skip header row (index 0)
            for idx in range(1, len(scan_rows)):
                try:
                    scan_cells = await scan_rows[idx].query_selector_all("td")
                    
                    if len(scan_cells) >= 5:  # Need at least 5 columns
                        student_record = {}
                        
                        # Get columns 2-5 (indices 1-4)
                        cell_texts = []
                        for i in range(1, 5):  # Get columns at index 1, 2, 3, 4 (2nd to 5th columns)
                            cell_text = await scan_cells[i].inner_text()
                            cell_texts.append(cell_text.strip())
                        
                        # Handle all columns except the name+ID column
                        header_idx = 0
                        for i, text in enumerate(cell_texts):
                            if i == 1:  # This is the name+ID column (column 3, index 1 in cell_texts)
                                # Split the name and ID
                                if "\nID:" in text:
                                    parts = text.split("\nID:")
                                    name = parts[0].strip()
                                    id_value = parts[1].strip() if len(parts) > 1 else ""
                                    
                                    # Add the split values to the record
                                    student_record["Name"] = name
                                    student_record["ID"] = id_value
                                else:
                                    # If no ID found, just use the text as the name
                                    student_record["Name"] = text
                                    student_record["ID"] = ""
                                
                                # Skip 2 headers (Name and ID) since we've handled them
                                header_idx += 2
                            else:
                                # Handle other columns normally
                                if header_idx < len(headers):
                                    student_record[headers[header_idx]] = text
                                header_idx += 1
                        
                        # Add school code for reference
                        student_record["School Code"] = school_code
                        
                        # Only include students regardless of status (both active and disabled)
                        all_students.append(student_record)
                        
                except Exception as e:
                    print(f"Error processing student row {idx} on page {scan_page}: {e}")
        except Exception as e:
            print(f"Error scanning page {scan_page}: {e}")
    
    # Save data to Excel file
    if all_students:
        output_file = os.path.join("scraped_data", f"{school_code}.xlsx")
        df = pd.DataFrame(all_students)
        df.to_excel(output_file, index=False)
        print(f"✓ Scraped {len(all_students)} students, saved to {output_file}")
        return df
    else:
        print(f"No students found for {school_code}")
        return None

async def process_reference_excel(page, reference_excel_path):
    """Process a reference Excel file that contains school codes in the KOD column"""
    print(f"\n=========================================")
    print(f"PROCESSING REFERENCE EXCEL: {reference_excel_path}")
    print(f"=========================================")
    
    try:
        # Load reference Excel with string type preservation for all columns
        reference_df = pd.read_excel(reference_excel_path, dtype=str)
        
        # Check if KOD column exists
        if 'KOD' not in reference_df.columns:
            print("Error: KOD column not found in reference Excel")
            return
            
        # Extract unique school codes
        school_codes = reference_df['KOD'].dropna().unique()
        print(f"Found {len(school_codes)} unique school codes")
        
        # Process each school code
        for idx, school_code in enumerate(school_codes, 1):
            if not school_code or not isinstance(school_code, str):
                print(f"Skipping invalid school code: {school_code}")
                continue
                
            # Validate school code format (ABC1234)
            if not (len(school_code) == 7 and school_code[:3].isalpha() and school_code[3:].isdigit()):
                print(f"Skipping invalid school code format: {school_code}")
                continue
                
            print(f"\nProcessing school code {idx}/{len(school_codes)}: {school_code}")
            
            # Navigate to expiration page
            await page.goto("https://crm.studentqr.com/expiration")
            await asyncio.sleep(1)
            
            # Fill in school code
            selector = "body > div.page-container > div.page-content > div > div > div:nth-child(2) > div > div > form > div > div:nth-child(3) > div > input"
            await page.fill(selector, school_code)
            print(f"✓ Pasted school code: {school_code}")
            
            # Click submit button
            submit_selector = "body > div.page-container > div.page-content > div > div > div:nth-child(2) > div > div > form > div > div.col-12.col-md-12.text-end > div > button.btn.btn-block.btn-primary"
            await page.click(submit_selector)
            print("✓ Clicked submit button")
            await asyncio.sleep(3)
            
            # Extract school ID from table
            try:
                id_selector = "body > div.page-container > div.page-content > div > div > div:nth-child(3) > div > div > div.table-responsive > table > tbody > tr:nth-child(2) > td:nth-child(2) > small"
                id_element = await page.wait_for_selector(id_selector)
                raw_id = await id_element.inner_text()
                school_id = raw_id.replace("ID: ", "")  # Remove "ID: " prefix including space
                print(f"✓ Found school ID: {school_id}")
                
                # Scrape and save student data
                await scrape_student_data(page, school_id, school_code)
                
            except Exception as e:
                screenshot_path = await take_error_screenshot(page, school_code, "id_extraction_error")
                print(f"❌ Failed to extract school ID for {school_code}: {str(e)}")
                print(f"Screenshot saved to {screenshot_path}")
        
        print("\n✓ All school codes have been processed!")
        
    except Exception as e:
        print(f"❌ Error processing reference Excel: {str(e)}")
        return

async def main():
    """Main function that scrapes student data based on school codes"""
    print("===== STUDENT DATA SCRAPER =====")
    print("Please provide the following information:")
    
    # Get reference Excel path
    reference_excel_path = clean_path(input("Enter the path to the reference Excel file with KOD column: "))
    while not reference_excel_path or not os.path.exists(reference_excel_path):
        if not reference_excel_path:
            print("Excel file path is required!")
        else:
            print("Excel file not found!")
        reference_excel_path = clean_path(input("Enter the path to the reference Excel file: "))
    
    # Get credentials    
    user_email = input("Enter your email: ").strip()
    while not user_email:
        print("Email is required!")
        user_email = input("Enter your email: ").strip()
    user_password = getpass.getpass("Enter your password: ").strip()
    while not user_password:
        print("Password is required!")
        user_password = getpass.getpass("Enter your password: ").strip()

    async with async_playwright() as p:
        browser = await p.firefox.launch(
            headless=True,
            firefox_user_prefs= {
                "browser.cache.disk.enable": False,
                "browser.cache.memory.enable": False,
                "browser.cache.offline.enable": False,
                "browser.animation.disabled": True,
                "toolkit.cosmeticAnimations.enabled": False,
                "widget.macos.touchbar.enabled": False,
                "browser.sessionstore.interval": 60000000,
                "permission.default.image": 2,
                "dom.ipc.processCount": 1
                }
            )
        try:
            context = await browser.new_context()
            page = await context.new_page()
            
            # Login
            await page.goto("https://crm.studentqr.com/login")
            await asyncio.sleep(0.5)
            await page.fill("input[type='email']", user_email)
            await page.fill("input[type='password']", user_password)
            try:
                await page.wait_for_selector("div.loader", state="detached", timeout=3000)
            except Exception:
                pass
            await page.click("xpath=//button[@type='submit']")
            await asyncio.sleep(2)

            # Process the reference Excel file
            await process_reference_excel(page, reference_excel_path)
                
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
