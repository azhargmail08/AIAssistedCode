import asyncio
import os
import time
import json
import csv
import pandas as pd
from fuzzywuzzy import fuzz
import getpass
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime

# Create required folders if they don't exist
required_folders = ['logs', 'screenshots', 'processed', 'formatted']
for folder in required_folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created {folder} directory")

def log_error(school_code, error_msg, screenshot_path=None):
    """Log error to file with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_entry = {
        "timestamp": timestamp,
        "school_code": school_code,
        "error": str(error_msg),
        "screenshot": screenshot_path
    }
    
    log_file = os.path.join("logs", "error_log.json")
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        logs.append(log_entry)
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Failed to write to log file: {e}")

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

# Utility functions (as in Selenium code)

def clean_path(path: str) -> str:
    return path.strip().strip("'\"")

async def create_new_class(page, level, name):
    """
    Create new class using the provided level and name.
    """
    try:
        # Click the "Create New Class" button
        await page.wait_for_selector("body > div > div.page-content > div > div > div.col-md-12 > div > div > div.d-flex.gap-3.justify-content-end > button", timeout=5000)
        await page.click("body > div > div.page-content > div > div > div.col-md-12 > div > div > div.d-flex.gap-3.justify-content-end > button")
        # Wait for the modal to appear
        # Just verify it exists in DOM
        exists = await page.evaluate("""() => {
            return !!document.querySelector(".modal-dialog");
        }""")
        await asyncio.sleep(1)  # Ensure the modal is fully rendered

        # Fill in the "level" and "name" fields
        level_input = await page.query_selector("input[name='level']")
        name_input = await page.query_selector("input[name='name']")
        await level_input.fill("")
        await level_input.fill(level)
        await name_input.fill("")
        await name_input.fill(name)

        # Click the specified radio button option
        await page.click("#createClass > div > div > div.modal-body > form > div:nth-child(6) > div > div:nth-child(1) > label")
        # Click the "Add New Class" button to submit the form
        await page.wait_for_selector("#createClass > div > div > div.modal-body > form > div:nth-child(7) > button", timeout=5000)
        await page.click("#createClass > div > div > div.modal-body > form > div:nth-child(7) > button")
        # Just verify it exists in DOM
        exists = await page.evaluate("""() => {
            return !!document.querySelector(".modal-dialog");
        }""")
        await asyncio.sleep(1)
        print(f"Created new class: Level '{level}', Name '{name}'")
    except Exception as e:
        print(f"Error creating new class for Level '{level}', Name '{name}':", e)

async def get_web_classes(page, school_id):
    """
    Get existing (level, name) pairs from the website.
    """
    classes = set()
    class_url_page1 = f"https://crm.studentqr.com/school/{school_id}/class"
    await page.goto(class_url_page1)
    await asyncio.sleep(2)
    try:
        table_body = await page.wait_for_selector("body > div > div.page-content > div > div > div.col-md-12 > div > div > div.table-responsive > table > tbody", timeout=5000)
        rows = await table_body.query_selector_all("tr")
        for row in rows:
            cells = await row.query_selector_all("td")
            if len(cells) >= 3:
                lvl = (await cells[1].inner_text()).strip()
                nm = (await cells[2].inner_text()).strip()
                classes.add((lvl, nm))
                # If special class name
                if lvl == "" and nm and ' ' not in nm:
                    classes.add((nm, ""))
                    print(f"Added special class alternative: ({nm}, '')")
                if ' ' in nm and lvl == "":
                    parts = nm.split(' ', 1)
                    classes.add((parts[0], parts[1]))
                    print(f"Added complex class alternative: ({parts[0]}, {parts[1]})")
    except Exception as e:
        print("Error reading Page 1:", e)
    
    max_page = 1
    try:
        nav_element = await page.query_selector("body > div > div.page-content > div > div > div.col-md-12 > div > div > div.row > div > nav")
        nav_links = await nav_element.query_selector_all("a")
        pages = []
        for link in nav_links:
            text = (await link.inner_text()).strip()
            if text.isdigit():
                pages.append(int(text))
        if pages:
            max_page = max(pages)
    except Exception as e:
        print("Error extracting max page number:", e)
    
    for page_num in range(2, max_page + 1):
        try:
            page_url = f"https://crm.studentqr.com/school/{school_id}/class?page={page_num}"
            await page.goto(page_url)
            await asyncio.sleep(1)
            table_body = await page.wait_for_selector("body > div > div.page-content > div > div > div.col-md-12 > div > div > div.table-responsive > table > tbody", timeout=5000)
            rows = await table_body.query_selector_all("tr")
            for row in rows:
                cells = await row.query_selector_all("td")
                if len(cells) >= 3:
                    lvl = (await cells[1].inner_text()).strip()
                    nm = (await cells[2].inner_text()).strip()
                    classes.add((lvl, nm))
                    if lvl == "" and nm and ' ' not in nm:
                        classes.add((nm, ""))
                        print(f"Added special class alternative: ({nm}, '')")
                    if ' ' in nm and lvl == "":
                        parts = nm.split(' ', 1)
                        classes.add((parts[0], parts[1]))
                        print(f"Added complex class alternative: ({parts[0]}, {parts[1]})")
        except Exception as e:
            print(f"Error reading Page {page_num}:", e)
    
    return classes

def find_best_match(student_name, teacher_dict):
    best_match = None
    best_score = 0
    for excel_name in teacher_dict.keys():
        score = fuzz.ratio(student_name.lower(), excel_name.lower())
        if score > best_score:
            best_score = score
            best_match = excel_name
    return best_match, best_score

def parse_class_name(class_string):
    prefixes = ['TAHUN', 'TINGKATAN', 'DARJAH', 'FORM', 'YEAR', 'SEMESTER']
    if not class_string or ' ' not in class_string:
        return ("", class_string)
    parts = class_string.split(' ')
    if len(parts) >= 3 and parts[0] in prefixes and parts[1].isdigit():
        level = f"{parts[0]} {parts[1]}"
        name = ' '.join(parts[2:])
        return (level, name)
    parts = class_string.split(' ', 1)
    return (parts[0], parts[1] if len(parts) > 1 else "")

async def find_missing_students_in_excel(teacher_df, original_student_data, school_id, base_filename, column_mapping):
    print("\n===== FINDING MISSING STUDENTS =====")
    missing_xlsx_filename = ""
    website_names = set()
    for student in original_student_data:
        student_info = student.get("Name", "")
        if "\nID:" in student_info:
            student_name = student_info.split("\nID:")[0].strip()
        else:
            student_name = student_info.strip()
        website_names.add(student_name.lower())
    
    missing_students = []
    match_threshold = 99
    processed_excel_names = set()
    name_col = column_mapping.get('name_col')
    if not name_col and 'NAMA' not in teacher_df.columns:
        print("Name column not found in Excel data")
        print("Available columns:", list(teacher_df.columns))
        return [], missing_xlsx_filename
    actual_name_col = name_col if name_col else "NAMA"
    for _, row in teacher_df.iterrows():
        if pd.isna(row.get(actual_name_col)):
            continue
        excel_name = str(row.get(actual_name_col)).strip()
        if not excel_name or excel_name.lower() in processed_excel_names:
            continue
        processed_excel_names.add(excel_name.lower())
        best_score = 0
        for web_name in website_names:
            score = fuzz.ratio(excel_name.lower(), web_name)
            if score > best_score:
                best_score = score
        if best_score < match_threshold:
            student_record = {
                'name': excel_name,
                'nick_name': str(row.get('NICKNAME', '')).strip(),
                'matrix_number': str(row.get('NO MATRIK', '')).strip(),
                'father': str(row.get('NAMA BAPA', '')).strip(),
                'father_id': str(row.get('ID BAPA', '')).strip(),
                'father_email': str(row.get('EMAIL BAPA', '')).strip(),
                'father_contact_no': str(row.get('NO TEL BAPA', '')).strip(),
                'mother': str(row.get('NAMA IBU', '')).strip(),
                'mother_id': str(row.get('ID IBU', '')).strip(),
                'mother_email': str(row.get('EMAIL IBU', '')).strip(),
                'mother_contact_no': str(row.get('NO TEL IBU', '')).strip(),
            }
            if 'KELAS' in row:
                kelas = str(row.get('KELAS')).strip()
                parts = kelas.split(' ', 1)
                if len(parts) == 2:
                    student_record['class_level'] = parts[0]
                    student_record['class_name'] = parts[1]
                else:
                    student_record['class_level'] = kelas
                    student_record['class_name'] = ''
            else:
                student_record['class_level'] = str(row.get('TINGKATAN_TAHUN', '')).strip()
                student_record['class_name'] = str(row.get('NAMA_KELAS', '')).strip()
            missing_students.append(student_record)
    if missing_students:
        missing_xlsx_filename = f"{base_filename}_{school_id}_upload.xlsx"
        missing_df = pd.DataFrame(missing_students)
        required_columns = ['name', 'nick_name', 'matrix_number', 'father_id', 'father_email', 'father_contact_no', 'mother_id', 'mother_email', 'mother_contact_no', 'class_level', 'class_name']
        for col in required_columns:
            if col not in missing_df.columns:
                missing_df[col] = ''
        missing_df = missing_df[required_columns]
        missing_df.to_excel(missing_xlsx_filename, index=False)
        print(f"Missing student data saved as {missing_xlsx_filename}")
    return missing_students, missing_xlsx_filename

dropdown_options_cache = {}

async def find_alumni_class(page):
    # For Playwright, we directly query the options from the dropdown element.
    try:
        dropdown_element = await page.wait_for_selector("#moveStudentForm > div.modal-body > div.form-group.mb-2 > select", timeout=10000)
        options = await dropdown_element.query_selector_all("option")
        exact_match_index = None
        contains_match_index = None
        exact_match_text = None
        contains_match_text = None
        for index, option in enumerate(options):
            option_text = (await option.inner_text()).strip()
            option_class = option_text.split(" - ")[0].strip() if " - " in option_text else option_text
            if option_class == "ALUMNI":
                exact_match_index = index
                exact_match_text = option_text
                break
            if "ALUMNI" in option_class and contains_match_index is None:
                contains_match_index = index
                contains_match_text = option_text
        if exact_match_index is not None:
            print(f"Found exact ALUMNI class match: {exact_match_text}")
            return exact_match_index, exact_match_text
        if contains_match_index is not None:
            print(f"Found partial ALUMNI class match: {contains_match_text}")
            return contains_match_index, contains_match_text
        print("No ALUMNI class found in dropdown")
        return None, None
    except Exception as e:
        print("Error in finding ALUMNI class:", e)
        return None, None

async def handle_dropdown_selection(page, target_class):
    try:
        # Check cache first for performance
        if target_class in dropdown_options_cache:
            cached_option = dropdown_options_cache[target_class]
            print(f"🔍 Using cached value for class '{target_class}'")
            
            # Use cached selection directly
            result = await page.evaluate(f"""() => {{
                try {{
                    const dropdown = document.querySelector("#moveStudentForm > div.modal-body > div.form-group.mb-2 > select");
                    dropdown.value = "{cached_option['value']}";
                    dropdown.selectedIndex = {cached_option['index']};
                    dropdown.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    
                    const form = document.querySelector("#moveStudentForm");
                    const button = form.querySelector("button[type='submit']");
                    
                    if (button) {{
                        button.click();
                        return {{ success: true, method: "button (cached)" }};
                    }} else {{
                        form.submit(); 
                        return {{ success: true, method: "form (cached)" }};
                    }}
                }} catch (e) {{
                    return {{ success: false, error: e.toString() }};
                }}
            }}""")
            
            print(f"Form submission using cache: {result}")
            return True
        
        # Wait for modal form using JavaScript (no visibility requirement)
        await page.wait_for_function("""() => {
            const form = document.querySelector("#moveStudentForm");
            return !!form; 
        }""", timeout=5000)
        
        print("Modal form detected in DOM")
        
        # Wait for dropdown to have options (faster than sleep)
        await page.wait_for_function("""() => {
            const dropdown = document.querySelector("#moveStudentForm > div.modal-body > div.form-group.mb-2 > select");
            return dropdown && dropdown.options && dropdown.options.length > 0;
        }""", timeout=5000)

        # Get all options and their info in a single JavaScript call
        dropdown_data = await page.evaluate("""() => {
            const dropdown = document.querySelector("#moveStudentForm > div.modal-body > div.form-group.mb-2 > select");
            const options = Array.from(dropdown.options).map((opt, index) => ({
                text: opt.text.trim(),
                value: opt.value,
                index: index,
                disabled: opt.disabled,
                class: opt.text.trim().split(" - ")[0].trim()
            }));
            
            return {
                optionCount: options.length,
                options: options,
                availableClasses: options.filter(o => !o.disabled).map(o => o.class)
            };
        }""")
        
        print(f"🔍 Found {dropdown_data['optionCount']} options ({len(dropdown_data['availableClasses'])} enabled)")
        
        # Cache all options for future lookups - major performance improvement
        for opt in dropdown_data['options']:
            if not opt['disabled']:  # Only cache enabled options
                dropdown_options_cache[opt['class']] = {
                    'value': opt['value'],
                    'index': opt['index'],
                    'text': opt['text']
                }
        
        # Find matching option
        selected_option = None
        for opt in dropdown_data['options']:
            if opt['class'] == target_class:
                selected_option = opt
                print(f"✅ Found exact matching class: {opt['text']}")
                break
                
        # If no match found, try fuzzy matching
        if not selected_option and dropdown_data['availableClasses']:
            from fuzzywuzzy import process
            best_match_class, score = process.extractOne(target_class, dropdown_data['availableClasses'])
            
            if score >= 98:
                for opt in dropdown_data['options']:
                    if opt['class'] == best_match_class:
                        selected_option = opt
                        print(f"⚠️ Using fuzzy match: {best_match_class} ({score}% match)")
                        break
        
        if not selected_option:
            print(f"❌ No suitable match found for '{target_class}'")
            return False
            
        # Select and submit in one JavaScript operation
        result = await page.evaluate(f"""() => {{
            try {{
                const dropdown = document.querySelector("#moveStudentForm > div.modal-body > div.form-group.mb-2 > select");
                dropdown.value = "{selected_option['value']}";
                dropdown.selectedIndex = {selected_option['index']};
                dropdown.dispatchEvent(new Event('change', {{ bubbles: true }}));
                
                const form = document.querySelector("#moveStudentForm");
                const button = form.querySelector("button[type='submit']");
                
                if (button) {{
                    button.click();
                    return {{ success: true, method: "button" }};
                }} else {{
                    form.submit(); 
                    return {{ success: true, method: "form" }};
                }}
            }} catch (e) {{
                return {{ success: false, error: e.toString() }};
            }}
        }}""")
        
        print(f"Form submission: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error in dropdown selection: {e}")
        try:
            await page.keyboard.press("Escape")  # Try to close any stuck modal
        except:
            pass
        return False

async def upload_unmatched_students(page, excel_filename):
    try:
        print("\n===== UPLOADING UNMATCHED STUDENT EXCEL FILE =====")
        await page.wait_for_selector("#app > div.col-12 > div.row > div.col-md-9.col-sm-12 > div > div > div:nth-child(4) > button", timeout=10000)
        await page.click("#app > div.col-12 > div.row > div.col-md-9.col-sm-12 > div > div > div:nth-child(4) > button")
        print("✓ Clicked 'Upload Student Data' button")
        await page.wait_for_selector("#importStudentModal", state="visible", timeout=10000)
        await asyncio.sleep(1)
        file_input = await page.wait_for_selector("#importStudentModal > div > div > div > div > form > div.form-group.col-12.mb-3 > input", timeout=10000)
        await page.eval_on_selector("#importStudentModal > div > div > div > div > form > div.form-group.col-12.mb-3 > input", "el => el.style.display = 'block'")
        abs_path = os.path.abspath(excel_filename)
        await file_input.set_input_files(abs_path)
        print(f"✓ Uploaded file: {excel_filename}")
        try:
            upload_submit_button = await page.wait_for_selector("#importStudentModal > div > div > div > div > form > div.form-group.col-6.text-end.my-2 > button.btn.btn-info.mx-2", timeout=5000)
            await upload_submit_button.click()
            print("✓ Clicked 'Upload' button")
        except Exception as e:
            print("⚠️ Could not find upload button, trying JS form submission", e)
            await page.eval_on_selector("#importStudentModal form", "form => form.submit()")
        await asyncio.sleep(3)
        await page.wait_for_selector("//*[contains(text(), 'successfully uploaded')]", timeout=10000)
        print("✓ Upload successful!")
    except Exception as e:
        print(f"❌ Error uploading unmatched student data: {e}")

def get_column_mapping(df):
    # Define possible column names for each field (lowercase for case-insensitive matching)
    name_columns = ['nama', 'name', 'student name', 'student_name', 'nama murid', 'full name', 'nama_kelas']
    class_columns = ['nama_kelas', 'class name', 'class_name']
    level_columns = ['tingkatan_nama', 'tingkatan_tahun', 'level', 'tingkatan', 'darjah', 'tahun', 'year', 'grade']
    
    # Initialize mapping dictionary with None values
    mapping = {
        'name_col': None,
        'class_col': None, 
        'level_col': None,
        'class_name_col': None,
        'nickname_col': None,
        'matrix_col': None,
        'father_col': None,
        'father_id_col': None,
        'father_email_col': None,
        'father_contact_col': None,
        'mother_col': None,
        'mother_id_col': None,
        'mother_email_col': None,
        'mother_contact_col': None
    }
    
    # Get actual Excel column names (convert to lowercase for case-insensitive matching)
    excel_columns = [col.lower() for col in df.columns]
    
    # Find NAME column
    for col in name_columns:
        if col in excel_columns:
            actual_col = df.columns[excel_columns.index(col)]
            mapping['name_col'] = actual_col
            print(f"Found name column: '{actual_col}'")
            break
    
    # Find NAMA_KELAS column
    if 'nama_kelas' in excel_columns:
        actual_col = df.columns[excel_columns.index('nama_kelas')]
        mapping['class_name_col'] = actual_col
        print(f"Found class name column: '{actual_col}'")
    else:
        for col in class_columns:
            if col in excel_columns:
                actual_col = df.columns[excel_columns.index(col)]
                mapping['class_name_col'] = actual_col
                print(f"Found class name column: '{actual_col}'")
                break
    
    # Find TINGKATAN_NAMA/TINGKATAN_TAHUN column
    if 'tingkatan_nama' in excel_columns:
        actual_col = df.columns[excel_columns.index('tingkatan_nama')]
        mapping['level_col'] = actual_col
        print(f"Found level column: '{actual_col}'")
    elif 'tingkatan_tahun' in excel_columns:
        actual_col = df.columns[excel_columns.index('tingkatan_tahun')]
        mapping['level_col'] = actual_col
        print(f"Found level column: '{actual_col}'")
    else:
        for col in level_columns:
            if col in excel_columns:
                actual_col = df.columns[excel_columns.index(col)]
                mapping['level_col'] = actual_col
                print(f"Found level column: '{actual_col}'")
                break

    # Find additional columns using simple pattern matching
    for col in df.columns:
        col_lower = col.lower()
        
        # Nickname
        if any(x in col_lower for x in ['nick', 'nickname', 'alias']):
            mapping['nickname_col'] = col
            
        # Matrix number
        if any(x in col_lower for x in ['matri', 'matric', 'id', 'no matrik']):
            mapping['matrix_col'] = col
            
        # Father info
        if any(x in col_lower for x in ['father', 'bapa', 'dad']) and 'id' not in col_lower and 'email' not in col_lower and 'contact' not in col_lower and 'tel' not in col_lower:
            mapping['father_col'] = col
        if any(x in col_lower for x in ['father', 'bapa', 'dad']) and any(x in col_lower for x in ['id', 'ic', 'number']):
            mapping['father_id_col'] = col
        if any(x in col_lower for x in ['father', 'bapa', 'dad']) and 'email' in col_lower:
            mapping['father_email_col'] = col
        if any(x in col_lower for x in ['father', 'bapa', 'dad']) and any(x in col_lower for x in ['contact', 'tel', 'phone', 'hp']):
            mapping['father_contact_col'] = col
            
        # Mother info
        if any(x in col_lower for x in ['mother', 'ibu', 'mom']) and 'id' not in col_lower and 'email' not in col_lower and 'contact' not in col_lower and 'tel' not in col_lower:
            mapping['mother_col'] = col
        if any(x in col_lower for x in ['mother', 'ibu', 'mom']) and any(x in col_lower for x in ['id', 'ic', 'number']):
            mapping['mother_id_col'] = col
        if any(x in col_lower for x in ['mother', 'ibu', 'mom']) and 'email' in col_lower:
            mapping['mother_email_col'] = col
        if any(x in col_lower for x in ['mother', 'ibu', 'mom']) and any(x in col_lower for x in ['contact', 'tel', 'phone', 'hp']):
            mapping['mother_contact_col'] = col
    
    print("\nDetected column mappings:")
    for key, val in mapping.items():
        if val:
            print(f"  {key}: {val}")
    
    return mapping

async def validate_class_names(teacher_df, school_id):
    """Check NAMA_KELAS column for names exceeding 20 characters and log them"""
    try:
        if 'NAMA_KELAS' not in teacher_df.columns:
            print("Error: NAMA_KELAS column not found in Excel")
            return False
            
        # Get school info
        school_name = teacher_df['NAMA_SEKOLAH'].iloc[0] if 'NAMA_SEKOLAH' in teacher_df.columns else "Unknown"
        kod_sekolah = teacher_df['KODSEKOLAH'].iloc[0] if 'KODSEKOLAH' in teacher_df.columns else school_id
        
        # Find long class names
        long_class_names = teacher_df[teacher_df['NAMA_KELAS'].str.len() > 20]
        
        if not long_class_names.empty:
            # Create log file
            log_filename = f"{school_name} {kod_sekolah}.txt"
            with open(log_filename, "w", encoding="utf-8") as f:
                f.write(f"NAMA_SEKOLAH: {school_name}\n")
                f.write(f"KODSEKOLAH: {kod_sekolah}\n\n")
                f.write("Class names exceeding 20 characters:\n")
                f.write("-" * 50 + "\n")
                
                for _, row in long_class_names.iterrows():
                    class_name = row['NAMA_KELAS']
                    f.write(f"Class: {class_name}\n")
                    f.write(f"Length: {len(class_name)} characters\n")
                    f.write("-" * 50 + "\n")
                    
            print(f"\n⚠️ Found {len(long_class_names)} class names exceeding 20 characters")
            print(f"Details logged to: {log_filename}")
            return False
            
        return True
    except Exception as e:
        print(f"Error validating class names: {e}")
        return False

async def validate_nama_kelas(teacher_df, school_id, excel_file):
    """
    Validate NAMA_KELAS values and create a report for any issues found.
    Returns True if all values are valid (<=20 chars), False otherwise.
    """
    print("\n===== VALIDATING NAMA_KELAS VALUES =====")
    
    if 'NAMA_KELAS' not in teacher_df.columns:
        print("Error: NAMA_KELAS column not found in Excel")
        return False
        
    # Create reports directory if it doesn't exist
    if not os.path.exists('reports'):
        os.makedirs('reports')
        
    # Get timestamp for the report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize report data
    school_name = teacher_df['NAMA_SEKOLAH'].iloc[0] if 'NAMA_SEKOLAH' in teacher_df.columns else "Unknown"
    kod_sekolah = teacher_df['KODSEKOLAH'].iloc[0] if 'KODSEKOLAH' in teacher_df.columns else school_id
    
    # Find long class names
    long_class_names = teacher_df[teacher_df['NAMA_KELAS'].str.len() > 20]
    
    # Create report file
    report_filename = os.path.join('reports', f"{timestamp}_{excel_file}_validation.txt")
    
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write("NAMA_KELAS Validation Report\n")
        f.write("=========================\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Excel File: {excel_file}\n")
        f.write(f"School Name: {school_name}\n")
        f.write(f"School Code: {kod_sekolah}\n\n")
        
        if long_class_names.empty:
            f.write("✓ All NAMA_KELAS values are valid (<=20 characters)\n")
            print("✓ All NAMA_KELAS values are valid")
            return True
        else:
            f.write("⚠️ Found NAMA_KELAS values exceeding 20 characters:\n")
            f.write("-" * 50 + "\n")
            
            for _, row in long_class_names.iterrows():
                class_name = row['NAMA_KELAS']
                f.write(f"Class Name: {class_name}\n")
                f.write(f"Length: {len(class_name)} characters\n")
                f.write("-" * 50 + "\n")
            
            print(f"⚠️ Found {len(long_class_names)} class names exceeding 20 characters")
            print(f"Report saved as: {report_filename}")
            return False

async def main():
    """Main function that processes Excel files and updates CRM data"""
    print("===== CRM AUTOMATION SETUP =====")
    print("Please provide the following information:")
    
    # Get folder path containing Excel files
    excel_folder = clean_path(input("Enter the folder path containing Excel files: "))
    while not excel_folder or not os.path.exists(excel_folder):
        if not excel_folder:
            print("Folder path is required!")
        else:
            print("Folder not found!")
        excel_folder = clean_path(input("Enter the folder path containing Excel files: "))

    # Get Excel files from folder (excluding _upload and _formatted)
    excel_files = [f for f in os.listdir(excel_folder) if f.endswith('.xlsx') 
                  and not '_upload' in f and not '_formatted' in f]
    
    # Validate file naming pattern (ABC1234.xlsx)
    valid_files = []
    for f in excel_files:
        name = os.path.splitext(f)[0]
        if len(name) == 7 and name[:3].isalpha() and name[3:].isdigit():
            valid_files.append(f)
        else:
            print(f"Skipping invalid filename pattern: {f}")
            
    if not valid_files:
        print("No valid Excel files found in the specified folder!")
        return
        
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

            # Process each Excel file
            for excel_file in valid_files:
                print(f"\nProcessing {excel_file}")
                excel_path = os.path.join(excel_folder, excel_file)
                
                try:
                    # Load Excel with string type preservation for all columns
                    teacher_df = pd.read_excel(excel_path, dtype=str)
                    
                    # Get school code from filename (remove .xlsx)
                    school_code = os.path.splitext(excel_file)[0]
                    
                    # Validate NAMA_KELAS values before processing
                    if not await validate_nama_kelas(teacher_df, school_code, excel_file):
                        print(f"⚠️ Skipping {excel_file} due to NAMA_KELAS validation failures")
                        # Move file to processed folder
                        os.rename(excel_path, os.path.join("processed", excel_file))
                        continue
                    
                    # Navigate to expiration page
                    await page.goto("https://crm.studentqr.com/expiration")
                    await asyncio.sleep(1)
                    
                    # Get school code from filename (remove .xlsx)
                    school_code = os.path.splitext(excel_file)[0]
                    
                    # Fill in school code
                    selector = "body > div.page-container > div.page-content > div > div > div:nth-child(2) > div > div > form > div > div:nth-child(3) > div > input"
                    await page.fill(selector, school_code)
                    print(f"✓ Pasted school code: {school_code}")
                    
                    # Click submit button
                    submit_selector = "body > div.page-container > div.page-content > div > div > div:nth-child(2) > div > div > form > div > div.col-12.col-md-12.text-end > div > button.btn.btn-block.btn-primary"
                    await page.click(submit_selector)
                    print("✓ Clicked submit button")
                    await asyncio.sleep(1)
                    
                    # Extract school ID from table
                    print("Scanning for school ID...")
                    try:
                        id_selector = "body > div.page-container > div.page-content > div > div > div:nth-child(3) > div > div > div.table-responsive > table > tbody > tr:nth-child(2) > td:nth-child(2) > small"
                        id_element = await page.wait_for_selector(id_selector)
                        raw_id = await id_element.inner_text()
                        school_id = raw_id.replace("ID: ", "")  # Remove "ID: " prefix including space
                        print(f"✓ Found school ID: {school_id}")
                    except Exception as e:
                        screenshot_path = await take_error_screenshot(page, school_code, "id_extraction_error")
                        log_error(school_code, f"Failed to extract school ID: {str(e)}", screenshot_path)
                        print(f"❌ Failed to extract school ID for {school_code}. Skipping to next file.")
                        # Move failed file to processed folder
                        os.rename(excel_path, os.path.join("processed", excel_file))
                        continue

                    # Navigate to student page with extracted ID
                    student_url = f"https://crm.studentqr.com/school/{school_id}/student"
                    print(f"✓ Navigating to student page: {student_url}")
                    await page.goto(student_url)
                    await asyncio.sleep(1)

                    # Process the current Excel file with existing logic
                    try:
                        # ... (rest of the existing processing logic) ...
                        print(f"\nProcessing school ID: {school_id}")
                        web_classes = await get_web_classes(page, school_id)
                        print("Unique (Level, Name) pairs found on the web:", web_classes)
                        old_class_json_filename = f"original_classes_{school_id}.json"
                        old_class_csv_filename = f"original_classes_{school_id}.csv"
                        old_class_data = [{"Level": level, "Name": name} for level, name in web_classes]
                        with open(old_class_json_filename, "w", encoding="utf-8") as f:
                            json.dump(old_class_data, f, ensure_ascii=False, indent=4)
                        with open(old_class_csv_filename, "w", newline="", encoding="utf-8") as fcsv:
                            writer = csv.DictWriter(fcsv, fieldnames=["Level", "Name"])
                            writer.writeheader()
                            writer.writerows(old_class_data)
                        
                        # Load Excel with string type preservation for all columns
                        teacher_df = pd.read_excel(excel_path, dtype=str)

                        column_mapping = get_column_mapping(teacher_df)
                        name_col = column_mapping.get('name_col') or 'NAMA'
                        level_col = column_mapping.get('level_col') or 'TINGKATAN_TAHUN'
                        class_name_col = column_mapping.get('class_name_col') or 'NAMA_KELAS'

                        # Create set of teacher classes using TINGKATAN_TAHUN and NAMA_KELAS
                        teacher_classes = set()
                        if level_col in teacher_df.columns and class_name_col in teacher_df.columns:
                            teacher_df.dropna(subset=[level_col, class_name_col], inplace=True)
                            for _, row in teacher_df.iterrows():
                                level = str(row[level_col]).strip()
                                name = str(row[class_name_col]).strip() 
                                # Remove .0 from any numeric values that got converted
                                if level.endswith('.0'):
                                    level = level[:-2]
                                if name.endswith('.0'):
                                    name = name[:-2]
                                teacher_classes.add((level, name))
                        else:
                            print(f"Error: Required columns not found. Looking for {level_col} and {class_name_col}")
                            print("Available columns:", list(teacher_df.columns))
                            continue
                        print("Teacher's (Level, Name) pairs from Excel:", teacher_classes)
                        missing_in_web = teacher_classes - web_classes
                        print("Missing (Level, Name) pairs:", missing_in_web)
                        while missing_in_web:
                            for level, name in list(missing_in_web):
                                print(f"\nCreating new class for missing pair: Level '{level}', Name '{name}'")
                                await create_new_class(page, level, name)
                                web_classes = await get_web_classes(page, school_id)
                                missing_in_web = teacher_classes - web_classes
                                print("Updated missing (Level, Name) pairs:", missing_in_web)
                                if not missing_in_web:
                                    break
                        print(f"Finished processing class creation for school ID: {school_id}")
                        
                        # Use the same teacher_df that was read with dtype=str earlier
                        teacher_dict = {}
                        if level_col in teacher_df.columns and class_name_col in teacher_df.columns:
                            teacher_df.dropna(subset=[name_col, level_col, class_name_col], inplace=True)
                            for _, row in teacher_df.iterrows():
                                nama = str(row[name_col]).strip()
                                concatenated_class = str(row[level_col]).strip() + " " + str(row[class_name_col]).strip()
                                teacher_dict[nama] = concatenated_class
                        print(f"Created teacher dictionary with {len(teacher_dict)} entries")
                        student_url = f"https://crm.studentqr.com/school/{school_id}/student"
                        excel_basename = os.path.basename(excel_path)
                        base_filename = os.path.splitext(excel_basename)[0]
                        json_filename = f"{base_filename}_{school_id}.json"
                        csv_filename = f"{base_filename}_{school_id}.csv"
                        fuzzy_csv_filename = f"{base_filename}_{school_id}_fuzzy_matches.csv"
                        fuzzy_matches = []
                        student_data = []
                        processed_student_ids = set()
                        await page.goto(student_url)
                        await asyncio.sleep(2)
                        total_pages = 1
                        try:
                            pagination = await page.query_selector(".pagination")
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
                        original_student_data = []
                        for scan_page in range(1, total_pages + 1):
                            scan_page_url = f"{student_url}?page={scan_page}" if scan_page > 1 else student_url
                            print(f"\nScanning student page {scan_page} of {total_pages}")
                            await page.goto(scan_page_url)
                            await asyncio.sleep(1)
                            scan_table = await page.wait_for_selector("#studentTable", timeout=10000)
                            scan_rows = await scan_table.query_selector_all("tr")
                            for idx in range(1, len(scan_rows)):
                                try:
                                    scan_cells = await scan_rows[idx].query_selector_all("td")
                                    if len(scan_cells) >= 4:
                                        student_num = (await scan_cells[1].inner_text()).strip()
                                        student_info = (await scan_cells[2].inner_text()).strip()
                                        student_class = (await scan_cells[3].inner_text()).strip()
                                        student_status = (await scan_cells[4].inner_text()).strip()
                                        original_student_data.append({
                                            "#": student_num,
                                            "Name": student_info,
                                            "Kelas": student_class,
                                            "Status": student_status
                                        })
                                except Exception as e:
                                    print("Error scanning student row:", e)
                        original_student_json = f"original_students_{school_id}.json"
                        original_student_csv = f"original_students_{school_id}.csv"
                        with open(original_student_json, "w", encoding="utf-8") as f:
                            json.dump(original_student_data, f, ensure_ascii=False, indent=4)
                        with open(original_student_csv, "w", newline="", encoding="utf-8") as fcsv:
                            writer = csv.DictWriter(fcsv, fieldnames=["#", "Name", "Kelas", "Status"])
                            writer.writeheader()
                            writer.writerows(original_student_data)
                        missing_students, missing_xlsx_filename = await find_missing_students_in_excel(teacher_df, original_student_data, school_id, base_filename, column_mapping)
                        def calculate_match_rate(original_students, teacher_df, name_col):
                            website_names = set()
                            match_count = 0
                            for student in original_students:
                                student_info = student.get("Name", "")
                                if "\nID:" in student_info:
                                    student_name = student_info.split("\nID:")[0].strip().lower()
                                else:
                                    student_name = student_info.strip().lower()
                                website_names.add(student_name)
                            excel_names = {str(row.get(name_col)).strip().lower() for _, row in teacher_df.iterrows() if not pd.isna(row.get(name_col))}
                            exact_matches = website_names.intersection(excel_names)
                            match_count = len(exact_matches)
                            unmatched_website = website_names - exact_matches
                            unmatched_excel = excel_names - exact_matches
                            for web_name in unmatched_website:
                                for excel_name in unmatched_excel:
                                    score = fuzz.ratio(web_name, excel_name)
                                    if score >= 90:
                                        match_count += 1
                                        break
                            return (match_count / len(website_names) * 100) if website_names else 0
                        match_rate = calculate_match_rate(original_student_data, teacher_df, name_col)
                        print(f"Match rate: {match_rate:.1f}%")
                        if match_rate < 39:
                            print("Match rate is below 39%, skipping processing for this Excel file")
                            log_error(school_code, f"Low match rate: {match_rate:.1f}%", None)
                            continue
                        current_page = 1
                        while current_page <= total_pages:
                            page_url = f"{student_url}?page={current_page}" if current_page > 1 else student_url
                            print(f"\nProcessing student page {current_page} of {total_pages}")
                            await page.goto(page_url)
                            await asyncio.sleep(2)
                            table = await page.wait_for_selector("#studentTable", timeout=10000)
                            rows = await table.query_selector_all("tr")
                            if len(rows) <= 1:
                                print("No students on this page, moving to next")
                                current_page += 1
                                continue
                            row_index = 1
                            while row_index < len(rows):
                                try:
                                    # Get fresh references to table and rows each time
                                    table = await page.wait_for_selector("#studentTable", timeout=5000)
                                    if not table:
                                        print("Could not find student table, retrying page...")
                                        await page.goto(page_url)
                                        await asyncio.sleep(1)
                                        continue
                                        
                                    rows = await table.query_selector_all("tr")
                                    if row_index >= len(rows):
                                        break
                                        
                                    row = rows[row_index]
                                    cells = await row.query_selector_all("td")
                                    
                                    # Immediately get all the text content we need
                                    if len(cells) < 5:
                                        row_index += 1
                                        continue
                                        
                                    cell_texts = await asyncio.gather(
                                        cells[1].inner_text(),
                                        cells[2].inner_text(),
                                        cells[3].inner_text(),
                                        cells[4].inner_text()
                                    )
                                    
                                    student_number = cell_texts[0].strip()
                                    student_info = cell_texts[1].strip()
                                    student_class = cell_texts[2].strip()
                                    student_status = cell_texts[3].strip()

                                    if "\nID:" in student_info:
                                        student_name = student_info.split("\nID:")[0].strip()
                                        student_id = student_info.split("\nID:")[1].strip()
                                    else:
                                        student_name = student_info
                                        student_id = ""
                                        
                                    if student_status.lower() == "disabled":
                                        print(f"Skipping disabled student: {student_name}")
                                        row_index += 1
                                        continue
                                    
                                    if student_id and student_id in processed_student_ids:
                                        print(f"Skipping already processed student: {student_name}")
                                        row_index += 1
                                        continue
                                    student_data.append({
                                        "#": student_number,
                                        "Name": student_info,
                                        "Kelas": student_class,
                                        "Status" : student_status
                                    })
                                    current_class = student_class
                                    if "Kelas:" in current_class:
                                        current_class = current_class.split("Kelas:")[-1].strip()
                                    needs_transfer = False
                                    target_class = None
                                    is_fuzzy_match = False
                                    if student_name in teacher_dict:
                                        excel_class = teacher_dict[student_name]
                                        # Remove any '.0' that might have been added during earlier processing
                                        if excel_class.endswith('.0'):
                                            excel_class = excel_class[:-2]
                                        if excel_class != current_class:
                                            needs_transfer = True
                                            target_class = excel_class
                                            print(f"Student {student_name} needs to be moved from '{current_class}' to '{excel_class}'")
                                    else:
                                        is_fuzzy_match = True
                                        best_match, match_score = find_best_match(student_name, teacher_dict)
                                        if match_score >= 99:
                                            excel_class = teacher_dict[best_match]
                                            print(f"Fuzzy match found: '{student_name}' matches '{best_match}' with {match_score}% confidence")
                                            fuzzy_matches.append({
                                                "Website Name": student_name,
                                                "Excel Name": best_match,
                                                "Match Score": match_score,
                                                "Excel Class": excel_class,
                                                "Current Class": current_class
                                            })
                                            if excel_class != current_class:
                                                needs_transfer = True
                                                target_class = excel_class
                                                print(f"Student {student_name} (fuzzy match) needs to be moved from '{current_class}' to '{excel_class}'")
                                        else:
                                            print(f"No good match found for '{student_name}', will move to ALUMNI class")
                                            fuzzy_matches.append({
                                                "Website Name": student_name,
                                                "Excel Name": best_match if best_match else "No Match",
                                                "Match Score": match_score,
                                                "Excel Class": "ALUMNI",
                                                "Current Class": current_class
                                            })
                                            if "ALUMNI" not in current_class:
                                                needs_transfer = True
                                                target_class = "1 ALUMNI"
                                    if needs_transfer and target_class:
                                        try:
                                            move_button = await row.query_selector("button.btn.btn-sm.btn-warning")
                                            await move_button.scroll_into_view_if_needed()
                                            await page.wait_for_selector("button.btn.btn-sm.btn-warning", timeout=5000)
                                            await move_button.click()
                                            await asyncio.sleep(0.5)
                                            if target_class == "ALUMNI":
                                                dropdown_element = await page.wait_for_selector("#moveStudentForm > div.modal-body > div.form-group.mb-2 > select", timeout=10000)
                                                await dropdown_element.scroll_into_view_if_needed()
                                                await asyncio.sleep(1)
                                                alumni_index, alumni_class = await find_alumni_class(page)
                                                if alumni_index is not None:
                                                    await page.eval_on_selector("#moveStudentForm > div.modal-body > div.form-group.mb-2 > select", f"el => {{ el.selectedIndex = {alumni_index}; el.dispatchEvent(new Event('change', {{ bubbles: true }})); }}")
                                                    print(f"Selected ALUMNI class: {alumni_class}")
                                                    transfer_button = await page.query_selector("button[type='submit']")
                                                    await transfer_button.click()
                                                    print(f"Successfully transferred {student_name} to {alumni_class}")
                                                    if student_id:
                                                        processed_student_ids.add(student_id)
                                                    await asyncio.sleep(2)
                                                    table = await page.wait_for_selector("#studentTable", timeout=10000)
                                                    rows = await table.query_selector_all("tr")
                                                    continue
                                                else:
                                                    print("No ALUMNI class found in dropdown")
                                                    try:
                                                        cancel_button = await page.query_selector("button[type='button'][class='btn btn-secondary']")
                                                        await cancel_button.click()
                                                    except Exception as e:
                                                        print("Couldn't find cancel button", e)
                                            else:
                                                success = await handle_dropdown_selection(page, target_class)
                                                if success:
                                                    print(f"Successfully transferred {student_name} to {target_class}")
                                                    if student_id:
                                                        processed_student_ids.add(student_id)
                                                    await asyncio.sleep(0.5)
                                                    table = await page.wait_for_selector("#studentTable", timeout=10000)
                                                    rows = await table.query_selector_all("tr")
                                                    continue
                                                else:
                                                    print(f"Warning: Couldn't find matching class {target_class} in dropdown!")
                                                    try:
                                                        cancel_button = await page.query_selector("button[type='button'][class='btn btn-secondary']")
                                                        await cancel_button.click()
                                                    except Exception as e:
                                                        print("Could not find cancel button", e)
                                        except Exception as e:
                                            print(f"Error during transfer for {student_name}: {e}")
                                            try:
                                                await page.goto(page_url)
                                                await asyncio.sleep(2)
                                                table = await page.wait_for_selector("#studentTable", timeout=10000)
                                                rows = await table.query_selector_all("tr")
                                                continue
                                            except Exception as e:
                                                print("Error recovering page:", e)
                                    row_index += 1
                                except Exception as e:
                                    print(f"Error processing student: {e}")
                                    row_index += 1
                            current_page += 1
                        with open(json_filename, "w", encoding="utf-8") as f:
                            json.dump(student_data, f, ensure_ascii=False, indent=4)
                        print(f"Student data saved as {json_filename}")
                        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
                            writer = csv.DictWriter(csvfile, fieldnames=["#", "Name", "Kelas", "Status"])
                            writer.writeheader()
                            writer.writerows(student_data)
                        print(f"Student data saved as {csv_filename}")
                        if fuzzy_matches:
                            with open(fuzzy_csv_filename, "w", newline="", encoding="utf-8") as csvfile:
                                writer = csv.DictWriter(csvfile, fieldnames=["Website Name", "Excel Name", "Match Score", "Excel Class", "Current Class"])
                                writer.writeheader()
                                writer.writerows(fuzzy_matches)
                            print(f"Fuzzy match data saved as {fuzzy_csv_filename}")
                        if missing_students:
                            print("\n===== FINAL STEP =====")
                            print("\nUploading unmatched student data...")
                            await upload_unmatched_students(page, missing_xlsx_filename)
                        # After successful processing, move the file to processed folder
                        os.rename(excel_path, os.path.join("processed", excel_file))
                        print(f"✓ Moved {excel_file} to processed folder")

                    except Exception as e:
                        screenshot_path = await take_error_screenshot(page, school_code, "processing_error")
                        log_error(school_code, f"Error processing school: {str(e)}", screenshot_path)
                        print(f"❌ Error processing {school_code}: {str(e)}")
                        # Move failed file to processed folder
                        os.rename(excel_path, os.path.join("processed", excel_file))
                        continue

                except Exception as e:
                    screenshot_path = await take_error_screenshot(page, school_code, "general_error")
                    log_error(school_code, f"General error: {str(e)}", screenshot_path)
                    print(f"❌ General error processing {school_code}: {str(e)}")
                    # Move failed file to processed folder
                    os.rename(excel_path, os.path.join("processed", excel_file))
                    continue

            print("\n✓ All Excel files have been processed!")
            
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
