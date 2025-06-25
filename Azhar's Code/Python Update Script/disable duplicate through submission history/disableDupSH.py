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

async def take_error_screenshot(page, jpn_code, error_type):
    """Take a screenshot of the current page state"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join("screenshots", f"{timestamp}_{jpn_code}_{error_type}.png")
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
    
    # Look for KOD JPN column
    jpn_col = None
    while True:
        try:
            choice = int(input("\nSelect the column containing JPN codes (enter number): ")) - 1
            if 0 <= choice < len(columns):
                jpn_col = columns[choice]
                print(f"\nSelected column: {jpn_col}")
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    return selected_sheet, jpn_col, df

async def handle_admin_login(context, email):
    """Handle admin portal login and interaction"""
    try:
        # Create new page for admin portal
        admin_page = await context.new_page()
        
        # Go to admin login page
        await admin_page.goto("https://admin.studentqr.com/login")
        await asyncio.sleep(1)
        
        # Fill in credentials
        await admin_page.fill("body > div.authincation.p-4 > div > div > div > div > div.row.no-gutters > div > div.p-4.p-md-5 > form > div:nth-child(2) > input", email)
        await admin_page.fill("body > div.authincation.p-4 > div > div > div > div > div.row.no-gutters > div > div.p-4.p-md-5 > form > div:nth-child(3) > div > input", "password")
        
        # Submit login form
        await admin_page.keyboard.press("Enter")
        await admin_page.wait_for_url("https://admin.studentqr.com/")
        print(f"✓ Logged in to admin portal as {email}")
        
        # Navigate to reporting
        await admin_page.goto("https://admin.studentqr.com/reporting")
        await asyncio.sleep(5)

        # Click the date range selector
        date_selector = "#submissionDateRange"
        await admin_page.wait_for_selector(date_selector)
        await admin_page.evaluate("document.querySelector('#submissionDateRange').click()")
        await asyncio.sleep(2)

        # Inspect calendar elements
        calendar_structure = await admin_page.evaluate("""() => {
            const leftCalendar = document.querySelector('.daterangepicker .drp-calendar.left');
            const rightCalendar = document.querySelector('.daterangepicker .drp-calendar.right');
            
            function getCalendarInfo(calendar) {
                if (!calendar) return null;
                return {
                    monthYear: calendar.querySelector('.month').textContent,
                    availableDates: Array.from(calendar.querySelectorAll('td.available')).map(td => ({
                        text: td.textContent.trim(),
                        classes: td.className,
                        inMonth: !td.classList.contains('off'),
                    })),
                    tableHTML: calendar.querySelector('table').outerHTML
                };
            }
            
            return {
                left: getCalendarInfo(leftCalendar),
                right: getCalendarInfo(rightCalendar),
                ranges: Array.from(document.querySelectorAll('.ranges li')).map(li => li.textContent),
                currentSelection: document.querySelector('.drp-selected') ? document.querySelector('.drp-selected').textContent : null
            };
        }""")

        if calendar_structure:
            print("\nCalendar Structure:")
            print("-" * 60)
            print("Left Calendar Month:", calendar_structure['left']['monthYear'])
            print("\nAvailable Dates in Left Calendar:")
            for date in calendar_structure['left']['availableDates']:
                if date['inMonth']:
                    print(f"Date: {date['text']}, Classes: {date['classes']}")
            
            print("\nRight Calendar Month:", calendar_structure['right']['monthYear'])
            print("\nAvailable Dates in Right Calendar:")
            for date in calendar_structure['right']['availableDates']:
                if date['inMonth']:
                    print(f"Date: {date['text']}, Classes: {date['classes']}")
            
            print("\nPreset Ranges:", calendar_structure['ranges'])
            print("Current Selection:", calendar_structure['currentSelection'])
            print("-" * 60)

        # Navigate to Nov 2024 in left calendar
        prev_month_selector = "body > div.daterangepicker.ltr.auto-apply.show-calendar.opensright > div.drp-calendar.left > div.calendar-table > table > thead > tr:nth-child(1) > th.prev.available"
        print("\nNavigating to November 2024...")
        
        while True:
            current_month = await admin_page.evaluate("""() => {
                const monthYearElement = document.querySelector('.daterangepicker .drp-calendar.left .month');
                return monthYearElement ? monthYearElement.textContent : null;
            }""")
            
            if current_month and "Nov 2024" in current_month:
                print("✓ Found November 2024")
                break
                
            await admin_page.evaluate(f"""() => {{
                const prevButton = document.querySelector('{prev_month_selector}');
                if (prevButton) {{
                    prevButton.click();
                }}
            }}""")
            await asyncio.sleep(1)
            print(f"Current month: {current_month}")

        # Select November 1st with exact selector
        print("\nSelecting start date (Nov 1, 2024)...")
        start_date_selected = await admin_page.evaluate("""() => {
            const nov1Selector = "body > div.daterangepicker.ltr.auto-apply.show-calendar.opensright > div.drp-calendar.right > div.calendar-table > table > tbody > tr:nth-child(1) > td.active.start-date.available";
            const nov1 = document.querySelector(nov1Selector);
            if (nov1) {
                nov1.click();
                console.log('Clicked November 1st');
                return true;
            }
            return false;
        }""")
        await asyncio.sleep(1)
        print("Start date selected:", start_date_selected)

        # Navigate to Jun 2025 in right calendar
        next_month_selector = "body > div.daterangepicker.ltr.auto-apply.show-calendar.opensright > div.drp-calendar.right > div.calendar-table > table > thead > tr:nth-child(1) > th.next.available"
        print("\nNavigating to June 2025...")
        
        while True:
            current_month = await admin_page.evaluate("""() => {
                const monthYearElement = document.querySelector('.daterangepicker .drp-calendar.right .month');
                return monthYearElement ? monthYearElement.textContent : null;
            }""")
            
            if current_month and "Jun 2025" in current_month:
                print("✓ Found June 2025")
                break
                
            await admin_page.evaluate(f"""() => {{
                const nextButton = document.querySelector('{next_month_selector}');
                if (nextButton) {{
                    nextButton.click();
                }}
            }}""")
            await asyncio.sleep(1)
            print(f"Current month: {current_month}")

        # Select June 30th with exact selector
        print("\nSelecting end date (Jun 30, 2025)...")
        end_date_selected = await admin_page.evaluate("""() => {
            const jun30Selector = "body > div.daterangepicker.ltr.auto-apply.show-calendar.opensright > div.drp-calendar.right > div.calendar-table > table > tbody > tr:nth-child(6) > td.active.start-date.available";
            const jun30 = document.querySelector(jun30Selector);
            if (jun30) {
                jun30.click();
                console.log('Clicked June 30th');
                return true;
            }
            return false;
        }""")
        await asyncio.sleep(1)
        print("End date selected:", end_date_selected)

        # Verify the selection
        final_selection = await admin_page.evaluate("""() => {
            const selection = document.querySelector('.drp-selected');
            return selection ? selection.textContent : null;
        }""")
        if final_selection:
            print(f"\nFinal date range selection: {final_selection}")
        
        # If selection is not correct, try applying it again
        if not "20241101 - 20250630" in (final_selection or ""):
            print("First attempt didn't work, trying again...")
            await admin_page.evaluate("""() => {
                const leftCalendar = document.querySelector('.daterangepicker .drp-calendar.left');
                const rightCalendar = document.querySelector('.daterangepicker .drp-calendar.right');
                
                // Click November 1st
                const dates1 = Array.from(leftCalendar.querySelectorAll('td.available:not(.off)'));
                const nov1 = dates1.find(date => date.textContent.trim() === '1');
                if (nov1) nov1.click();
                
                // Click June 30th
                const dates2 = Array.from(rightCalendar.querySelectorAll('td.available:not(.off)'));
                const june30 = dates2.find(date => date.textContent.trim() === '30');
                if (june30) june30.click();
            }""")
            await asyncio.sleep(1)
            
            final_selection = await admin_page.evaluate("""() => {
                const selection = document.querySelector('.drp-selected');
                return selection ? selection.textContent : null;
            }""")
            print(f"Final attempt selection: {final_selection}")
        
        # Close admin page
        await admin_page.close()
        
    except Exception as e:
        print(f"Error in admin portal: {e}")
        screenshot_path = await take_error_screenshot(admin_page, "admin_portal", "date_range_error")
        if screenshot_path:
            print(f"Error screenshot saved to: {screenshot_path}")

async def scrape_submission_history(page, context, school_id):
    """Scrape submission history data from the table"""
    print(f"\nViewing submission history for school ID: {school_id}")
    
    try:
        # Wait for table to appear
        table = await page.wait_for_selector("#app > div > div.mb-1 > div.card.shadow-lg > div > div > table", timeout=10000)
        print("✓ Found submission history table")

        # Get all rows
        rows = await table.query_selector_all("tr")
        
        # Extract header row
        header_row = await rows[0].query_selector_all("th")
        headers = []
        for header in header_row:
            header_text = await header.inner_text()
            headers.append(header_text.strip())
        
        # Print headers
        print("\nSubmission History:")
        print("-" * 80)
        print(" | ".join(headers))
        print("-" * 80)
        
        # Extract and print data rows
        for row in rows[1:]:  # Skip header row
            cells = await row.query_selector_all("td")
            row_data = []
            for idx, cell in enumerate(cells):
                cell_text = await cell.inner_text()
                row_data.append(cell_text.strip())
            print(" | ".join(row_data))

            # Check if this row has Super Admin = Yes
            row_dict = dict(zip(headers, row_data))
            if row_dict.get('By Super Admin') == 'Yes':
                email = row_dict.get('Email')
                if email:
                    print(f"\nFound Super Admin email: {email}")
                    await handle_admin_login(context, email)
                    
        print("-" * 80 + "\n")
        
    except Exception as e:
        print(f"Error viewing submission history: {e}")
        return None

async def process_jpn_codes(page, context, df, jpn_column):
    """Process each JPN code from the Excel file"""
    print(f"\n=========================================")
    print(f"PROCESSING JPN CODES FROM EXCEL")
    print(f"=========================================")
    
    try:
        # Extract JPN codes
        jpn_codes = df[jpn_column].dropna().unique()
        print(f"Found {len(jpn_codes)} unique JPN codes")
        
        # Process each Jpn code
        for idx, jpn_code in enumerate(jpn_codes, 1):
            if not jpn_code or pd.isna(jpn_code):
                continue
                
            print(f"\nProcessing JPN code {idx}/{len(jpn_codes)}: {jpn_code}")
            
            try:
                # Go to expiration page
                await page.goto("https://crm.studentqr.com/expiration")
                await asyncio.sleep(1)
                
                # Fill in JPN code
                selector = "body > div.page-container > div.page-content > div > div > div:nth-child(2) > div > div > form > div > div:nth-child(3) > div > input"
                await page.fill(selector, str(jpn_code))
                print(f"✓ Pasted JPN code: {jpn_code}")
                
                # Press Enter
                await page.keyboard.press("Enter")
                await asyncio.sleep(2)
                
                try:
                    # Click the submission history link
                    link_selector = "body > div.page-container > div.page-content > div > div > div:nth-child(3) > div > div > div.table-responsive > table > tbody > tr:nth-child(2) > td.text-center > div > a:nth-child(2) > svg"
                    await page.click(link_selector)
                    await asyncio.sleep(2)
                    
                    # Get current URL to extract school ID
                    current_url = page.url
                    school_id = current_url.split("/")[-1]
                    
                    # View submission history and handle admin login if needed
                    await scrape_submission_history(page, context, school_id)
                    
                except Exception as e:
                    print(f"Error processing JPN code: {e}")
                
            except Exception as e:
                print(f"❌ Failed to process JPN code {jpn_code}: {str(e)}")
        
        print("\n✓ All JPN codes have been processed!")
        
    except Exception as e:
        print(f"❌ Error processing Excel data: {str(e)}")
        return

async def main():
    """Main function that scrapes submission history data"""
    print("===== SUBMISSION HISTORY SCRAPER =====")
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
    selected_sheet, jpn_column, df = get_excel_info(excel_path)
    
    async with async_playwright() as p:
        browser = await p.firefox.launch(
            headless=False,
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
            
            # Fill in email and password
            await page.fill("#floatingInput", "nur.azhar.adnan@gmail.com")
            await page.fill("#floatingPassword", "password")
            
            # Click login button
            await page.keyboard.press("Enter")
            await asyncio.sleep(2)
            
            # Wait for navigation to complete
            await page.wait_for_url("https://crm.studentqr.com/")
            print("✓ Successfully logged in")

            # Process the Excel file
            await process_jpn_codes(page, context, df, jpn_column)
                
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(main())