# Variable Reference Fix - Script Generation

## Issue Resolved
Fixed `NameError: name 'script_id' is not defined` error that was occurring in all generated scripts.

## Problem
In the `update_scripts_with_logic.py`, the Chrome browser options were incorrectly referencing an undefined variable `script_id` instead of the properly defined constant `SCRIPT_ID`.

### Original Problematic Code:
```python
chrome_options.add_argument(f'--user-data-dir=C:/temp/chrome_profile_script_{script_id}')
chrome_options.add_argument(f'--remote-debugging-port={9222 + script_id}')
```

### Error in Generated Scripts:
```
NameError: name 'script_id' is not defined
```

## Solution
Updated the template in `update_scripts_with_logic.py` to use the correct variable `SCRIPT_ID` with proper string concatenation:

### Fixed Code:
```python
chrome_options.add_argument(f'--user-data-dir=C:/temp/chrome_profile_script_' + str(SCRIPT_ID))
chrome_options.add_argument(f'--remote-debugging-port=' + str(9222 + SCRIPT_ID))
```

## Verification
- ✅ All 66 scripts regenerated successfully
- ✅ Syntax validation passed for generated scripts
- ✅ Variable `SCRIPT_ID` is properly defined in each script (e.g., `SCRIPT_ID = 1` for script1)
- ✅ Chrome options now correctly reference the script ID for unique profiles and ports

## Result
Each script now properly creates:
- Unique Chrome profile directory: `C:/temp/chrome_profile_script_1`, `C:/temp/chrome_profile_script_2`, etc.
- Unique debugging port: `9223`, `9224`, `9225`, etc. (9222 + script_id)

This enables true concurrent execution of multiple browser instances without interference.