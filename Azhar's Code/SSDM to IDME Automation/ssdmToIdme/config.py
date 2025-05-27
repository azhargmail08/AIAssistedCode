# Configuration settings for the SSDM to IDME automation

# Default mapping values to use when no match is found
DEFAULT_MAPPING = {
    "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
    "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
    "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
}

# Whether to prompt user for manual input when no mapping is found
# If False, will use the default values above
# If True, will ask the user to enter values manually
PROMPT_ON_MISSING_MAPPING = True
