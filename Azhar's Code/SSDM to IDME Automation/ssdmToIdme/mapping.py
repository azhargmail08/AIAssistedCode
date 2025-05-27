#!/usr/bin/env python3

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright
from mapping_data import ssdm_to_idme_mapping

def save_comparison_results(scraped_data, mapping_data, comparison_result):
    """
    Save comparison results to a JSON file with detailed metadata.
    
    Args:
        scraped_data (dict): Data scraped from the web interface
        mapping_data (dict): Reference mapping data from mapping_data.py
        comparison_result (bool): Whether the categories match
    
    Returns:
        str: Path to the saved JSON file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join(os.path.dirname(__file__), "mapping_results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Get the current item name from scraped_data
    item_name = next(iter(scraped_data))
    
    # Create a copy of scraped_data without the all_category_options
    filtered_scraped_data = {
        item_name: {
            k: v for k, v in scraped_data[item_name].items() 
            if k != 'all_category_options'
        }
    }
    
    result_data = {
        "metadata": {
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "item_name": item_name,
        },
        "results": {
            "scraped_data": filtered_scraped_data,
            "mapping_data": mapping_data,
            "categories_match": comparison_result,
            "comparison_details": {
                "scraped_category": scraped_data[item_name]["old_category"],
                "expected_category": mapping_data.get("old_category") if mapping_data else None,
                "has_mapping": bool(mapping_data),
                "idme_mapping": {
                    "category": mapping_data.get("idme_category") if mapping_data else None,
                    "subcategory": mapping_data.get("idme_subcategory") if mapping_data else None,
                    "new_category": mapping_data.get("new_category") if mapping_data else None
                }
            }
        }
    }
    
    filename = f"comparison_results_{timestamp}.json"
    filepath = os.path.join(results_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=4, ensure_ascii=False)
    
    print(f"\nResults saved to: {filepath}")
    return filepath

async def perform_login(page, email, password):
    """Login and navigate to positives page."""
    print("\nLogging in...")
    await page.goto("https://admin.studentqr.com/login")
    await page.fill("input[type=email]", email)
    await page.fill("input[type=password]", password)
    await page.click("button[type=submit]")
    
    # Wait for navigation after login - it goes to root URL first
    try:
        await page.wait_for_url("https://admin.studentqr.com", timeout=5000)
        await page.wait_for_timeout(1000)  # Wait for any post-login redirects
    except:
        print("❌ Login failed. Please check your credentials and try again.")
        return False
        
    # Navigate to positives page
    print("Navigating to positives page...")
    await page.goto("https://admin.studentqr.com/positives")
    await page.wait_for_url("https://admin.studentqr.com/positives", timeout=5000)
    await page.wait_for_timeout(2000)
    return True

async def login_to_student_qr():
    """
    Automates login to admin.studentqr.com using Playwright.
    Asks for user credentials and detects successful login.
    """
    print("\n=== StudentQR Admin Portal Login Automation ===\n")
    
    # Ask for login credentials
    email = input("Enter your email: ")
    password = input("Enter your password (default is 'password'): ") or "password"
    
    # Process all items
    items_to_process = list(ssdm_to_idme_mapping.keys())
    print(f"\nWill process all {len(items_to_process)} items")
        
    async with async_playwright() as p:
        try:
            # Launch the browser in headless mode
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Perform initial login
            if not await perform_login(page, email, password):
                return
            
            # Process each item
            results = {
                "success": [],
                "failed": []
            }
            
            for i, item_name in enumerate(items_to_process, 1):
                print(f"\n=== Processing item {i}/{len(items_to_process)}: {item_name} ===")
                if await process_ssdm_item(page, item_name):
                    results["success"].append(item_name)
                else:
                    results["failed"].append(item_name)
                    
            # Print summary
            print("\n=== Processing Summary ===")
            print(f"Total items: {len(items_to_process)}")
            print(f"Successful: {len(results['success'])}")
            print(f"Failed: {len(results['failed'])}")
            
            if results["failed"]:
                print("\nFailed items:")
                for item in results["failed"]:
                    print(f"- {item}")
                    
        except Exception as e:
            print(f"Error: {str(e)}")
            raise e
        finally:
            input("\nPress Enter to close the browser...")
            await browser.close()

async def process_ssdm_item(page, item_name):
    """Process a single SSDM item - update its categories and save changes."""
    while True:  # Keep processing until we find our item or need to switch accounts
        try:
            # 1. Filter for SSDM items
            print("\nFiltering table for SSDM items...")
            search_input = "#positives_filter > label > input[type=search]"
            await page.fill(search_input, "")  # Clear search first
            await page.fill(search_input, "SSDM")
            await page.wait_for_timeout(1000)
                
            # Check if we have any SSDM items
            no_data = await page.evaluate('''() => {
                const tbody = document.querySelector("#positives > tbody > tr > td");
                return tbody && tbody.innerText.includes("No matching records found");
            }''')
                
            if no_data:
                print("❌ No SSDM records found in table. Account may be finished.")
                print("Logging out to try another account...")
                
                # Click profile dropdown and logout
                await page.click("#main-wrapper > div.header > div > nav > div > ul > li.nav-item.dropdown.header-profile > a")
                await page.wait_for_timeout(500)
                await page.click("#main-wrapper > div.header > div > nav > div > ul > li.nav-item.dropdown.header-profile.show > div > a:nth-child(6)")
                await page.wait_for_url("https://admin.studentqr.com/login")
                
                # Ask for new credentials
                print("\nPlease enter credentials for the next account:")
                email = input("Enter your email: ")
                password = input("Enter your password (default is 'password'): ") or "password"
                
                if not await perform_login(page, email, password):
                    return False
                print("Continuing with new account...")
                continue  # Start over with new account
    
            # 2. Get first visible SSDM item data
            item_data = await page.evaluate('''() => {
                const row = document.querySelector("#positives tbody tr");
                if (!row) return null;
                const cells = row.cells;
                return {
                    name: cells[2].innerText.trim(),
                    category: cells[3].innerText.trim()
                };
            }''')
            
            if not item_data:
                print("❌ Failed to get item data from table")
                return False
            
            print(f"\nProcessing item: {item_data['name']}")
            
            # 3. Click the dropdown button
            print("Opening dropdown menu...")
            try:
                await page.click("#dropdownMenuButton")
            except Exception as e:
                print(f"❌ Failed to click dropdown button: {str(e)}")
                return False
            
            await page.wait_for_timeout(500)
            
            # 4. Click edit in the dropdown
            print("Clicking edit option...")
            try:
                await page.click("#positives > tbody > tr:nth-child(1) > td:nth-child(4) > div > div > a:nth-child(2)")
            except Exception as e:
                print(f"❌ Failed to click edit option: {str(e)}")
                return False
            
            await page.wait_for_timeout(1500)

            # Check and clear the input field if it's not empty
            print("Checking input field...")
            input_value = await page.evaluate('''() => {
                const input = document.querySelector("#editPositive > div > div > div > form > div:nth-child(3) > div:nth-child(2) > div:nth-child(1) > input");
                if (input && input.value) {
                    const oldValue = input.value;
                    input.value = '';
                    // Trigger change event
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    return oldValue;
                }
                return null;
            }''')
            
            if input_value:
                print(f"Cleared input field. Previous value: {input_value}")
            else:
                print("Input field is already empty")

            await page.wait_for_timeout(500)
            
            # 5. Scrape modal data and match with mapping_data.py
            modal_data = await page.evaluate('''() => {
                const input = document.querySelector("#editPositive > div > div > div > form > div:nth-child(3) > div:nth-child(1) > div.form-group > input");
                const categoryXPath = "/html/body/div[2]/div[7]/div/div[4]/div/div/div/form/div[1]/div[2]/div[3]/select";
                const dropdown = document.evaluate(categoryXPath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                
                return {
                    input_name: input ? input.value.trim() : null,
                    input_value: input ? input.value.trim() : null,
                    category_text: dropdown && dropdown.selectedIndex >= 0 ? dropdown.options[dropdown.selectedIndex].text.trim() : null
                };
            }''')
            
            # Validate scrapped data
            if not modal_data.get('input_value') or not modal_data.get('category_text'):
                print("❌ Failed to read modal data")
                return False
                
            current_item = modal_data.get('input_value')
            current_category = modal_data.get('category_text')
            
            # Find all possible matches for the item name
            possible_matches = {}
            for mapping_key, mapping_data_list in ssdm_to_idme_mapping.items():
                if mapping_key.lower() in current_item.lower() or current_item.lower() in mapping_key.lower():
                    # If it's a single mapping, convert to list for consistency
                    if isinstance(mapping_data_list, dict):
                        mapping_data_list = [mapping_data_list]
                    possible_matches[mapping_key] = mapping_data_list

            if not possible_matches:
                print(f"⚠️ No mapping found for item: {current_item}")
                return False

            # Try to find an exact category match from possible matches
            found_match = None
            for mapping_key, mapping_data_list in possible_matches.items():
                for mapping_data in mapping_data_list:
                    if mapping_data['old_category'] == current_category:
                        found_match = mapping_data
                        print(f"✅ Found exact match: {mapping_key}")
                        break
                if found_match:
                    break
                    
            # If no exact match found, close modal and continue to next item
            if not found_match:
                print(f"❌ Categories don't match for {current_item}:")
                print(f"Scraped: {current_category}")
                for key, data_list in possible_matches.items():
                    for data in data_list:
                        print(f"Possible match '{key}' with category: {data['old_category']}")
                
                # Close modal by clicking outside
                await page.click("body", position={"x": 0, "y": 0})
                await page.wait_for_timeout(1000)
                continue  # Continue to next item
                
            # Found a match, proceed with updating dropdowns
            print(f"\nUpdating categories for: {current_item}")
            
            update_dropdown_script = '''({ xpath, targetText }) => {
                const dropdown = document.evaluate(
                    xpath,
                    document,
                    null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE,
                    null
                ).singleNodeValue;
                
                if (!dropdown) {
                    console.error("Dropdown not found:", xpath);
                    return false;
                }
                
                const targetOption = Array.from(dropdown.options).find(opt => opt.text === targetText);
                if (targetOption) {
                    dropdown.value = targetOption.value;
                    const event = new Event('change', { bubbles: true });
                    dropdown.dispatchEvent(event);
                    return true;
                }
                return false;
            }'''
            
            # Update new category
            print("Updating new category...")
            new_cat_success = await page.evaluate(update_dropdown_script, {
                'xpath': "/html/body/div[2]/div[7]/div/div[4]/div/div/div/form/div[1]/div[2]/div[3]/select",
                'targetText': found_match['new_category']
            })
            if not new_cat_success:
                print("❌ Failed to update new category")
                return False
            
            await page.wait_for_timeout(500)
            
            # Update IDME category
            print("Updating IDME category...")
            idme_cat_success = await page.evaluate(update_dropdown_script, {
                'xpath': "/html/body/div[2]/div[7]/div/div[4]/div/div/div/form/div[1]/div[2]/div[4]/select",
                'targetText': found_match['idme_category']
            })
            if not idme_cat_success:
                print("❌ Failed to update IDME category")
                return False
            
            await page.wait_for_timeout(1000)  # Wait longer for subcategory to populate
            
            # Update IDME subcategory
            print("Updating IDME subcategory...")
            idme_subcat_success = await page.evaluate(update_dropdown_script, {
                'xpath': "/html/body/div[2]/div[7]/div/div[4]/div/div/div/form/div[1]/div[2]/div[5]/select",
                'targetText': found_match['idme_subcategory']
            })
            if not idme_subcat_success:
                print("❌ Failed to update IDME subcategory")
                return False
            
            # 7. Save the changes
            print("Saving changes...")
            save_success = await page.evaluate('''() => {
                const saveButton = document.querySelector("#editPositive > div > div > div > form > div:nth-child(5) > div:nth-child(2) > button");
                if (saveButton) {
                    saveButton.click();
                    return true;
                }
                return false;
            }''')
            
            if not save_success:
                print("❌ Failed to find save button")
                return False
                
            print(f"✅ Successfully updated {current_item}")
            
            # Wait for page to reload after save
            await page.wait_for_timeout(2000)
            
            # If this was our target item, we're done
            if current_item == item_name:
                return True
            
            # Otherwise continue the loop to process more items
            
        except Exception as e:
            print(f"Error processing items: {str(e)}")
            return False

if __name__ == "__main__":
    asyncio.run(login_to_student_qr())
