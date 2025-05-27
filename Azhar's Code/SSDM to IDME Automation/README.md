# SSDM to IDME Automation

This project automates interactions with the StudentQR admin portal using Playwright, specifically for SSDM-related tasks.

## Setup Instructions

### 1. Set up the Virtual Environment

```bash
# Navigate to the project directory
cd "SSDM to IDME Automation"

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install playwright

# Install browser drivers
playwright install
```

### 2. Running the Scripts

```bash
# Make sure the virtual environment is activated
source venv/bin/activate

# To run the original login script
python ssdmToIdme/mapping.py

# To run the search and update script
python ssdmToIdme/search_and_update.py

# To run the refactored script (recommended)
python ssdmToIdme/search_and_update_refactored.py
```

### 3. Using the Scripts

#### Original Mapping Script (`mapping.py`)
- Logs into the admin portal and demonstrates basic interactions
- Searches for SSDM entries but doesn't make changes

#### Search and Update Script (`search_and_update.py`)
- When prompted, enter your email address
- Enter your password (or press Enter to use the default password: "password")
- Choose a specific SSDM item or 'all' to process all items
- The script will automatically:
  - Open a browser window and log in
  - Navigate to the positives page
  - Search for SSDM entries
  - Find and edit the selected item(s)
  - Update category mappings according to the data
  - Ask for confirmation before saving changes
  - Handle the page refresh after save
  - Continue with remaining items if processing all

#### Refactored Script (`search_and_update_refactored.py`) - Recommended
Enhanced version with better organization and improved post-save handling:
- Properly handles the web page behavior after saving changes
- Re-searches for "SSDM" after the page refresh
- Tracks which items have been processed to avoid duplicates
- Correctly interacts with dropdowns after page refresh
- Provides clearer feedback about the process at each step
- Implements a more robust class-based structure for maintainability

## Technical Details

- **Programming Language**: Python 3
- **Automation Framework**: Playwright
- **Browser**: Chromium (default)

## Notes

- For production use, you may want to set `headless=True` in the script to run the browser without UI
- The script detects login success based on URL changes and error messages

## Features

### Modal Form Data Extraction

The script extracts detailed information from modal forms, including:
- Form field labels and values
- Dropdown options with selected values
- Button availability

### Hierarchical Dropdown Handling

The script implements special handling for hierarchical dropdowns:
1. **Automatic Detection**: Identifies key dropdown elements (`#category`, `#idmeCatEdit`, `#idmeSubCatEdit`)
2. **Initial State Capture**: Records the initial state of all dropdowns
3. **Dependency Triggering**: Selects a value in the IDME Category dropdown to populate the Sub-Category options
4. **Change Detection**: Shows before/after comparison of dropdown options
5. **New Option Marking**: Marks new options that appear after selection with a 🆕 indicator

This feature is particularly useful for mapping relationships between categories in the SSDM to IDME workflow.

### Post-Save Behavior Handling

The refactored script includes improved handling of web page behavior after saving changes:

1. **Direct Selector Interaction**: Uses a direct CSS selector to reliably interact with the save button
2. **Page Refresh Handling**: Properly waits for the page to refresh after saving changes
3. **Re-search Automation**: Automatically re-searches for "SSDM" after the page refreshes
4. **Change Tracking**: Keeps track of which items have been processed to avoid duplicates
5. **Error Recovery**: Better error handling if a page doesn't refresh as expected
6. **Interaction Retry**: Can continue processing remaining items even if some fail

### Code Organization

The refactored script uses an object-oriented approach with:

- `SSDMToIDMEMapper` class that encapsulates all functionality
- Clear separation of concerns with specialized methods
- Better error handling and user interaction
- Proper documentation throughout the code
- Consistent logging and user feedback
