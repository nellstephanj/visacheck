# EU-VIS Matching Module

## Overview
This module provides a visual matching interface for comparing visa applicants against potential matches in the EU-VIS database. It displays the applicant details on the left side and shows 2-5 potential matching candidates on the right side.

## Features

### 1. Applicant Display (Left Side)
- **Profile Picture**: Generated using robohash.org based on application number
- **Personal Details**:
  - Surname
  - Surname at birth
  - Given Name
  - Nationality
  - Date of Birth
  - Place of Birth
  - Country of Birth
  - Gender

### 2. Candidate List (Right Side)
- **Displays 2-5 matching candidates**
- Each candidate card shows:
  - EU-VIS badge
  - Candidate number (1, 2, 3, etc.)
  - Profile picture (robohash.org)
  - All personal details matching the applicant format
  - EUVIS Applications count (randomly generated)
  - Selection button (✓ Select)
  - Info button (ℹ️)

### 3. Interactive Features
- **Match EU-VIS Button**: Loads new random candidates from the people folder
- **Select Candidate**: Click the "✓ Select" button to highlight a candidate with green border
- **Confirm Selection**: Confirm the selected candidate match
- **Reset**: Clear the current selection
- **Tabs**: Toggle between EU-VIS and BVV matching (BVV not yet implemented)

### 4. Data Source
- Uses mock data from `res/people/` folder
- Loads random JSON files (person_001.json through person_XXX.json)
- Profile pictures generated via robohash.org API
- Each person gets a unique robohash based on their visa application number

## File Structure

```
src/
├── pages/
│   └── matching.py                    # Matching screen UI
└── main.py                            # Updated with matching page navigation

res/
└── people/
    ├── person_001.json
    ├── person_002.json
    ├── person_003.json
    └── ... (multiple person files)
```

## JSON Data Format

Each person JSON file contains:

```json
{
  "visa_application_number": "AUTO000001",
  "case_type": "Work Visa",
  "visa_type_requested": "Long Stay",
  "application_type": "Initial",
  "submission_date": "2025-10-21",
  "intake_location": "Sydney FO",
  "applicant_is_minor": false,
  "urgent": true,
  "given_names": "Morgan",
  "surname": "Smith",
  "variation_in_birth_certificate": false,
  "gender": "Female",
  "country_of_nationality": "Australia",
  "address": {
    "street_number": "754 Eagles Road",
    "unit_number": "",
    "postal_code": "6328",
    "city": "Sydney",
    "state": "TAS",
    "country": "Australia"
  },
  "date_of_birth": {
    "year": 1974,
    "month": 2,
    "day": 21
  },
  "place_of_birth": {
    "city": "Canberra",
    "state": "TAS",
    "country": "Australia"
  },
  "residency_status_in_australia": "Citizen",
  "civil_status": "Married",
  "packaged_member_of_eu": false,
  "occupation": "Developer"
}
```

## Usage

### Accessing the Matching Page
1. Log in to the VisaCheck application
2. Navigate to "EU-VIS Matching" 🔍 from the sidebar
3. The page will automatically load a random applicant and 2-5 candidates

### Workflow
1. **Review Applicant**: Check the applicant details on the left side
2. **Review Candidates**: Examine potential matches on the right side
3. **Select Match**: Click "✓ Select" button on the matching candidate
   - Selected candidate will be highlighted with a green border
4. **Confirm**: Click "Confirm Selection" to finalize the match
5. **Reset** (optional): Clear selection if needed
6. **New Match**: Click "Match EU-VIS" to load new random candidates

### Visual Indicators
- **EU-VIS Badge**: Blue badge on each candidate card
- **Selected Candidate**: Green border (3px solid) around the selected card
- **Profile Pictures**: Unique robot avatars from robohash.org
- **Candidate Numbers**: 1, 2, 3, 4, 5 for easy reference

## Technical Details

### Profile Picture Generation
```python
def get_robohash_url(identifier, size=200):
    """Generate robohash.org URL for profile picture"""
    return f"https://robohash.org/{identifier}?size={size}x{size}"
```

### Loading Random People
```python
def get_random_people(people_dir, count=5):
    """Get random people from the people directory"""
    json_files = list(Path(people_dir).glob("person_*.json"))
    selected_files = random.sample(json_files, min(count, len(json_files)))
    return [load_person_data(file) for file in selected_files]
```

### Date Formatting
The module handles three types of date formats:
- **Complete**: DD/MM/YYYY (day, month, year)
- **Month and Year**: MM/YYYY
- **Year Only**: YYYY

## Session State Management

The matching page uses session state to maintain:
- `matching_applicant`: Current applicant being matched
- `matching_candidates`: List of candidate matches (2-5 people)
- `selected_candidate`: Index of the selected candidate (1-5)

## Navigation

### Top Navigation
- **← Back**: Navigate to previous page (placeholder)
- **Match EU-VIS**: Load new random applicants and candidates

### Bottom Navigation
- **Reset**: Clear current selection
- **Confirm Selection**: Finalize the match (enabled only when a candidate is selected)

### Tabs
- **🌍 EU-VIS**: Current matching interface (shows count of candidates)
- **🔵 BVV**: Placeholder for BVV matching (not yet implemented)

## Styling

### EU-VIS Badge
```html
<div style='background-color: #E3F2FD; padding: 4px 12px; border-radius: 4px; 
            display: inline-block; color: #1976D2; font-weight: bold;'>
    EU-VIS
</div>
```

### Selected Candidate Highlight
- Border: 3px solid #4CAF50 (green)
- Applied to the entire candidate card

## Future Enhancements

1. **BVV Matching**: Implement BVV database matching
2. **Advanced Search**: Filter candidates by specific criteria
3. **Match Score**: Display similarity percentage for each candidate
4. **History**: Track previous matches for an applicant
5. **Export**: Generate match report PDF
6. **Biometric Matching**: Integrate facial recognition
7. **Manual Entry**: Allow manual addition of candidates
8. **Batch Matching**: Process multiple applicants at once
9. **Match Reasons**: Show why candidates were matched
10. **Confidence Levels**: Display match confidence scores

## Troubleshooting

### No Candidates Displayed
- Ensure the `res/people/` folder contains JSON files
- Check that JSON files follow the correct format
- Verify at least 2 person files exist in the folder

### Profile Pictures Not Loading
- Check internet connection (robohash.org requires internet)
- Verify the robohash URL is correctly formatted
- Images are loaded on-demand from robohash.org

### Selection Not Working
- Ensure you click the "✓ Select" button
- Check that session state is properly initialized
- Try clicking "Reset" and selecting again

## API Reference

### Main Functions

#### `matching_page()`
Main entry point for the matching screen. Handles authentication, page layout, and user interactions.

#### `load_person_data(file_path)`
Loads person data from a JSON file.
- **Parameters**: `file_path` (str) - Path to JSON file
- **Returns**: dict - Person data

#### `get_random_people(people_dir, count=5)`
Retrieves random people from the people directory.
- **Parameters**: 
  - `people_dir` (str) - Path to people directory
  - `count` (int) - Number of random people to retrieve (default: 5)
- **Returns**: list - List of person dictionaries

#### `format_date_of_birth(dob)`
Formats date of birth dictionary to string.
- **Parameters**: `dob` (dict) - Date of birth with year, month, day keys
- **Returns**: str - Formatted date string

#### `get_robohash_url(identifier, size=200)`
Generates robohash.org URL for profile picture.
- **Parameters**:
  - `identifier` (str) - Unique identifier for the robot
  - `size` (int) - Image size in pixels (default: 200)
- **Returns**: str - Full robohash URL

#### `display_person_card(person, is_applicant=False, card_id=None)`
Displays a person card with profile picture and details.
- **Parameters**:
  - `person` (dict) - Person data
  - `is_applicant` (bool) - Whether this is the main applicant
  - `card_id` (str) - Optional card identifier

#### `display_candidate_compact(person, candidate_num, is_selected=False)`
Displays a compact candidate card for the list.
- **Parameters**:
  - `person` (dict) - Candidate data
  - `candidate_num` (int) - Candidate number (1-5)
  - `is_selected` (bool) - Whether this candidate is selected

## Testing

To test the matching page:

1. **Navigate to the page**: 
   ```
   http://localhost:8501
   Login → EU-VIS Matching
   ```

2. **Verify display**:
   - Applicant appears on left
   - 2-5 candidates appear on right
   - Profile pictures load from robohash.org

3. **Test selection**:
   - Click "✓ Select" on a candidate
   - Verify green border appears
   - Check "Confirm Selection" button becomes enabled

4. **Test reset**:
   - Click "Reset"
   - Verify selection is cleared

5. **Test new match**:
   - Click "Match EU-VIS"
   - Verify new applicant and candidates load

## Support

For issues or questions:
- Email: support@visacheck.com
- Review main documentation: `VISA_INTAKE_README.md`
- Check architecture: `ARCHITECTURE.md`
