#!/usr/bin/env python3
import asyncio
import getpass
from playwright.async_api import async_playwright

async def main():
    # Prompt for credentials
    email = input("Enter your email: ")
    password = getpass.getpass("Enter your password: ")
    
    async with async_playwright() as p:
        # Launch Firefox browser
        print("Launching Firefox browser...")
        browser = await p.firefox.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        try:
            # Navigate to login page
            print("Navigating to login page...")
            await page.goto("https://adminv2.studentqr.com/login")
            
            # Fill in login form
            print("Entering credentials...")
            email_selector = "body > div.authincation.p-4 > div > div > div > div > div.row.no-gutters > div > div.p-4.p-md-5 > form > div:nth-child(2) > input"
            password_selector = "body > div.authincation.p-4 > div > div > div > div > div.row.no-gutters > div > div.p-4.p-md-5 > form > div:nth-child(3) > div > input"
            login_button_selector = "body > div.authincation.p-4 > div > div > div > div > div.row.no-gutters > div > div.p-4.p-md-5 > form > div.text-center > button"
            
            # Wait for the form fields to be available and fill them
            await page.fill(email_selector, email)
            await page.fill(password_selector, password)
            
            # Click login button
            print("Logging in...")
            await page.click(login_button_selector)
            
            # Wait for login to complete by looking for dashboard elements instead of URL change
            print("Waiting for dashboard to load...")
            try:
                # Wait for dashboard elements to appear
                print("Waiting for dashboard elements to appear...")
                await page.wait_for_selector("#main-wrapper", timeout=10000)
                await page.wait_for_selector(".nk-sidebar", timeout=5000, state="visible")
                
                print("Login successful - dashboard loaded")
            except Exception as e:
                print(f"Login might have failed or dashboard element detection issue: {e}")
                print("Checking if we're still on the login page...")
                login_form_still_visible = await page.is_visible(login_button_selector)
                if login_form_still_visible:
                    print("Still on login page. Login likely failed.")
                    raise Exception("Login failed - still on login page")
                else:
                    print("Login form no longer visible. Proceeding anyway...")
            
            # Navigate to class page
            print("Navigating to class page...")
            await page.goto("https://adminv2.studentqr.com/class")
            
            # Loop until there are no more classes with delete buttons
            classes_deleted = 0
            while True:
                # Wait for page to load completely
                await page.wait_for_load_state("networkidle")
                await page.wait_for_selector("#main-wrapper > div.content-body", timeout=10000)
                
                # Check how many elements with id="classDiv" are present
                print("\n--- Scanning for classes to delete ---")
                
                # Using JavaScript to find all elements with id="classDiv" and check delete buttons
                class_details = await page.evaluate('''() => {
                    const container = document.querySelector("#main-wrapper > div.content-body > div > div.row");
                    if (!container) return { totalClassDivs: 0, deleteButtons: [] };
                    
                    const classDivs = container.querySelectorAll('[id="classDiv"]');
                    const totalClassDivs = classDivs.length;
                    
                    const deleteButtons = [];
                    
                    // For each classDiv, look for delete buttons
                    classDivs.forEach((classDiv, index) => {
                        // Find delete buttons within this classDiv
                        const delButtons = classDiv.querySelectorAll('[id^="del-"]');
                        
                        // Get class name if available
                        let className = "Unknown";
                        const classNameEl = classDiv.querySelector('.card-title');
                        if (classNameEl) {
                            className = classNameEl.textContent.trim();
                        }
                        
                        if (delButtons.length > 0) {
                            deleteButtons.push({
                                classIndex: index,
                                className: className,
                                deleteButtonId: delButtons[0].id
                            });
                        }
                    });
                    
                    return { totalClassDivs, deleteButtons };
                }''')
                
                # Display class information
                print(f"Found {class_details['totalClassDivs']} classes")
                print(f"Found {len(class_details['deleteButtons'])} classes with delete buttons")
                
                # If no more classes with delete buttons, break out of the loop
                if len(class_details['deleteButtons']) == 0:
                    print("No more classes with delete buttons found. Stopping...")
                    break
                
                # Process the first class with a delete button
                class_info = class_details['deleteButtons'][0]
                delete_button_id = class_info['deleteButtonId']
                class_name = class_info['className']
                
                print(f"Deleting class: {class_name} (Button ID: {delete_button_id})")
                
                # Click the delete button using JavaScript
                await page.evaluate(f'''() => {{
                    const deleteButton = document.getElementById("{delete_button_id}");
                    if (deleteButton) {{
                        deleteButton.click();
                    }}
                }}''')
                
                # Wait for the modal to appear
                print("Waiting for confirmation modal...")
                try:
                    # Wait for the modal to be visible
                    await page.wait_for_selector("#deleteClass", timeout=5000, state="visible")
                    
                    # Check for confirmation button in the modal
                    confirm_button_selector = "#deleteClass > div > div > div.modal-body > form > p > button.btn.btn-danger"
                    confirm_button_exists = await page.is_visible(confirm_button_selector)
                    
                    if confirm_button_exists:
                        # Click the confirmation button to delete the class
                        print("Clicking confirmation button...")
                        await page.click(confirm_button_selector)
                        
                        # Wait for deletion to complete and page to refresh
                        print("Waiting for deletion to complete...")
                        await page.wait_for_load_state("networkidle")
                        
                        classes_deleted += 1
                        print(f"Class '{class_name}' deleted successfully!")
                        print(f"Total classes deleted: {classes_deleted}")
                        
                        # Short pause to ensure the page updates fully
                        await asyncio.sleep(1)
                    else:
                        print("❌ Confirmation button not found in the modal")
                        break
                        
                except Exception as e:
                    print(f"Failed to interact with the modal: {e}")
                    break
            
            print(f"\nDeletion process complete. Total classes deleted: {classes_deleted}")
            
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Keep the browser open for manual inspection if needed
            input("Press Enter to close the browser...")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())