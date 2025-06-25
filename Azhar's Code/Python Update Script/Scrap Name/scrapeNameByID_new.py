import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright
from datetime import datetime

# Create required folders if they don't exist
required_folders = ['logs', 'screenshots', 'scraped_data']
for folder in required_folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created {folder} directory")

def clean_path(path: str) -> str:
    return path.strip().strip("'\"")

async def take_error_screenshot(page, id_value, error_type):
    """Take a screenshot of the current page state"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join("screenshots", f"{timestamp}_{id_value}_{error_type}.png")
    try:
        await page.screenshot(path=screenshot_path)
        return screenshot_path
    except Exception as e:
        print(f"Failed to take screenshot: {e}")
        return None

def get_excel_info(excel_path):
    """Get sheet names and column names from Excel file"""
    xl = pd.ExcelFile(excel_path)
    sheet_names = xl.sheet_names
    
    print("\nAvailable sheets:")
    for idx, sheet in enumerate(sheet_names, 1):
        print(f"{idx}. {sheet}")
    
    while True:
        try:
            choice = int(input("\nSelect sheet number: ")) - 1
            if 0 <= choice < len(sheet_names):
                selected_sheet = sheet_names[choice]
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Read the selected sheet
    df = pd.read_excel(excel_path, sheet_name=selected_sheet)
    columns = df.columns.tolist()
    
    print("\nAvailable columns:")
    for idx, col in enumerate(columns, 1):
        print(f"{idx}. {col}")
    
    # Always ask user to select the ID column
    id_col = None
    while True:
        try:
            choice = int(input("\nSelect the column containing school IDs (enter number): ")) - 1
            if 0 <= choice < len(columns):
                id_col = columns[choice]
                print(f"\nSelected column: {id_col}")
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    return selected_sheet, id_col, df

async def get_school_info(page, school_id):
    """Get school name and code from expiration page"""
    await page.goto("https://crm.studentqr.com/expiration")
    await asyncio.sleep(1)
    
    # Fill in school ID
    selector = "body > div.page-container > div.page-content > div > div > div:nth-child(2) > div > div > form > div > div:nth-child(1) > div > input"
    await page.fill(selector, str(school_id))
    print(f"✓ Pasted school ID: {school_id}")
    
    # Click submit button (using Enter key since it's a form)
    await page.keyboard.press("Enter")
    await asyncio.sleep(2)
    
    try:
        # Wait for table to appear
        table = await page.wait_for_selector("body > div.page-container > div.page-content > div > div > div:nth-child(3) > div > div > div.table-responsive > table > tbody", timeout=5000)
        
        # Get school name and code
        school_name = await page.evaluate('document.querySelector("body > div.page-container > div.page-content > div > div > div:nth-child(3) > div > div > div.table-responsive > table > tbody > tr:nth-child(2) > td:nth-child(2)").firstChild.textContent.trim()')
        school_code = await page.evaluate('document.querySelector("body > div.page-container > div.page-content > div > div > div:nth-child(3) > div > div > div.table-responsive > table > tbody > tr:nth-child(2) > td:nth-child(4)").lastChild.textContent.trim()')
        
        return school_name.strip(), school_code.strip()
    except Exception as e:
        print(f"Error getting school info: {e}")
        return None, None

async def scrape_student_data(page, school_id, id_value, save_dir):
    """
    Scrape columns 2-5 from the student table for a specific school ID
    and save it to an Excel file named after the school name and code.
    Also separates the name and ID from column 3 into separate columns.
    """
    print(f"\n===== SCRAPING STUDENT DATA FOR ID: {school_id} =====")
    
    # Get school name and code first
    school_name, school_code = await get_school_info(page, school_id)
    if not school_name or not school_code:
        print("Failed to get school information")
        return None
        
    student_url = f"https://crm.studentqr.com/school/{school_id}/student"
    
    # Rest of the existing scrape_student_data function remains the same
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
        
        if len(header_cells) >= 5:
            for i in range(1, 5):
                header_text = await header_cells[i].inner_text()
                if i == 2:
                    name_column_index = len(headers)
                    headers.append("Name")
                    headers.append("ID")
                else:
                    headers.append(header_text.strip())
            
            print(f"Table headers (modified): {headers}")
        else:
            print(f"Not enough columns in table, found {len(header_cells)} columns")
            headers = ["Column 2", "Name", "ID", "Column 4", "Column 5"]
            name_column_index = 1
    except Exception as e:
        print(f"Error getting table headers: {e}")
        headers = ["Column 2", "Name", "ID", "Column 4", "Column 5"]
        name_column_index = 1
    
    for scan_page in range(1, total_pages + 1):
        scan_page_url = f"{student_url}?page={scan_page}" if scan_page > 1 else student_url
        print(f"Scanning student page {scan_page} of {total_pages}")
        await page.goto(scan_page_url)
        await asyncio.sleep(1)
        
        try:
            scan_table = await page.wait_for_selector("#studentTable", timeout=10000)
            scan_rows = await scan_table.query_selector_all("tr")
            
            for idx in range(1, len(scan_rows)):
                try:
                    scan_cells = await scan_rows[idx].query_selector_all("td")
                    
                    if len(scan_cells) >= 5:
                        student_record = {}
                        cell_texts = []
                        for i in range(1, 5):
                            cell_text = await scan_cells[i].inner_text()
                            cell_texts.append(cell_text.strip())
                        
                        header_idx = 0
                        for i, text in enumerate(cell_texts):
                            if i == 1:
                                if "\nID:" in text:
                                    parts = text.split("\nID:")
                                    name = parts[0].strip()
                                    id_value = parts[1].strip() if len(parts) > 1 else ""
                                    student_record["Name"] = name
                                    student_record["ID"] = id_value
                                else:
                                    student_record["Name"] = text
                                    student_record["ID"] = ""
                                header_idx += 2
                            else:
                                if header_idx < len(headers):
                                    student_record[headers[header_idx]] = text
                                header_idx += 1
                        
                        student_record["Source ID"] = id_value
                        all_students.append(student_record)
                        
                except Exception as e:
                    print(f"Error processing student row {idx} on page {scan_page}: {e}")
        except Exception as e:
            print(f"Error scanning page {scan_page}: {e}")
    
    if all_students:
        try:
            # Create filename using school name and code
            safe_filename = f"{school_name} {school_code}".replace("/", "-").replace("\\", "-")
            
            # Ensure the save directory exists
            os.makedirs(save_dir, exist_ok=True)
            
            # Create full output path
            output_file = os.path.join(save_dir, f"{safe_filename}.xlsx")
            
            # Create DataFrame and save
            df = pd.DataFrame(all_students)
            df.to_excel(output_file, index=False)
            
            print(f"\nFile saved successfully:")
            print(f"- Filename: {safe_filename}.xlsx")
            print(f"- Directory: {save_dir}")
            print(f"- Full path: {output_file}")
            print(f"- Total students: {len(all_students)}")
            
            # Verify file was created
            if os.path.exists(output_file):
                print(f"✓ File verified at {output_file}")
            else:
                print(f"❌ Warning: File was not found after saving!")
            
            return df
        except Exception as e:
            print(f"❌ Error saving file: {str(e)}")
            screenshot_path = await take_error_screenshot(page, str(school_id), "save_error")
            if screenshot_path:
                print(f"Screenshot saved to {screenshot_path}")
            return None
    else:
        print(f"No students found for ID {id_value}")
        return None

async def process_ids(page, df, id_column, save_dir):
    """Process each ID from the Excel file"""
    print(f"\n=========================================")
    print(f"PROCESSING IDs FROM EXCEL")
    print(f"=========================================")
    
    try:
        # Extract unique IDs
        school_ids = df[id_column].dropna().unique()
        print(f"Found {len(school_ids)} unique IDs")
        
        # Process each ID
        for idx, school_id in enumerate(school_ids, 1):
            if not school_id or pd.isna(school_id):
                print(f"Skipping invalid ID: {school_id}")
                continue
                
            print(f"\nProcessing ID {idx}/{len(school_ids)}: {school_id}")
            
            try:
                # Directly use the ID to scrape student data
                await scrape_student_data(page, school_id, str(school_id), save_dir)
                
            except Exception as e:
                screenshot_path = await take_error_screenshot(page, str(school_id), "scraping_error")
                print(f"❌ Failed to scrape data for ID {school_id}: {str(e)}")
                if screenshot_path:
                    print(f"Screenshot saved to {screenshot_path}")
        
        print("\n✓ All IDs have been processed!")
        
    except Exception as e:
        print(f"❌ Error processing Excel data: {str(e)}")
        return

async def main():
    """Main function that scrapes student data based on school IDs"""
    print("===== STUDENT DATA SCRAPER =====")
    print("Please provide the following information:")
    
    # Get Excel file path
    excel_path = clean_path(input("Enter the path to the Excel file: "))
    while not excel_path or not os.path.exists(excel_path):
        if not excel_path:
            print("Excel file path is required!")
        else:
            print("Excel file not found!")
        excel_path = clean_path(input("Enter the path to the Excel file: "))
    
    # Get sheet and column information
    selected_sheet, id_column, df = get_excel_info(excel_path)
    
    # Get save directory path
    save_dir = clean_path(input("Enter the directory path where you want to save the Excel files: "))
    while not save_dir:
        print("Save directory path is required!")
        save_dir = clean_path(input("Enter the save directory path: "))
    
    # Create save directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    print(f"Files will be saved to: {save_dir}")
    
    # Get email (password is fixed as 'password')
    user_email = input("Enter your email: ").strip()
    while not user_email:
        print("Email is required!")
        user_email = input("Enter your email: ").strip()
    
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
            
            # Login with fixed password
            await page.goto("https://crm.studentqr.com/login")
            await asyncio.sleep(0.5)
            await page.fill("input[type='email']", user_email)
            await page.fill("input[type='password']", "password")
            try:
                await page.wait_for_selector("div.loader", state="detached", timeout=3000)
            except Exception:
                pass
            await page.click("xpath=//button[@type='submit']")
            await asyncio.sleep(2)

            # Process the Excel file
            await process_ids(page, df, id_column, save_dir)
                
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
