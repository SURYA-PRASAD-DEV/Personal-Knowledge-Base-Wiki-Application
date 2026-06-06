# Version History Feature Enhancement

## Overview
The Personal Knowledge Base app now includes a modern version history system with an enhanced UI for tracking and managing article versions.

## New Features

### 1. **Version Timeline View** (`/articles/<article_id>/versions`)
- Visual timeline display of all versions
- Each version card shows:
  - **Version Number** (e.g., v1, v2, v3)
  - **Editor Name** - who made the edit (defaults to "System")
  - **Timestamp** - when the version was created
  - **Content Preview** - first 200 characters of the version
  - **Action Buttons**:
    - **Restore** - revert to this version (with confirmation)
    - **Compare** - see differences between consecutive versions

### 2. **Version Comparison (Diff View)** (`/articles/<article_id>/compare?v1=<vid>&v2=<vid>`)
- Side-by-side comparison of two versions
- **Version Selection Dropdowns** - dynamically choose any two versions
- **Diff Display** with color-coded changes:
  - **Red (#ffcccc)** - removed lines with `-` marker
  - **Green (#ccffcc)** - added lines with `+` marker
  - **Gray** - unchanged lines
- **Restore Buttons** for each version being compared
- Visual metadata (editor, timestamp) for each version

### 3. **Restoration with Confirmation Dialog**
- Before restoring a version, users see a confirmation dialog showing:
  - `Are you sure you want to restore version X?`
  - Note: Current content is automatically saved as a new version
- Safe operation: prevents accidental reversions

### 4. **Editor and Timestamp Metadata**
- **Timestamp**: Every version records `edited_at` (UTC datetime)
- **Editor Name**: Every version records `edited_by` field
  - Seeded data uses `"System"` 
  - Can be extended to track actual user names

## Implementation Details

### Backend Changes

#### `models.py`
- Updated `add_version(article_id, content, edited_by='System')` to accept editor name
- Version records now include:
  ```python
  {
    'article_id': article_id,
    'version_no': next_no,
    'content': safe_content,
    'edited_at': _now(),
    'edited_by': edited_by,
    'id': version_id
  }
  ```
- Removed duplicate function definitions

#### `utils/diff.py` (NEW)
- `generate_diff()` - compares two text blocks using Python's `difflib`
- `generate_html_diff()` - generates HTML representation with color-coded changes

#### `app.py`
- Added `/articles/<article_id>/compare` route for version comparison
- Passes `edited_by` parameter through version operations
- Cleaned up duplicate route definitions

### Frontend Changes

#### `templates/versions.html` (UPDATED)
- Timeline layout with Bootstrap cards
- Version metadata display (number, timestamp, editor)
- Content preview with truncation
- Hover effects and responsive design
- Inline confirm dialog for restoration

#### `templates/compare_versions.html` (NEW)
- Dual-panel layout showing both versions
- Version selection dropdowns to change compared versions
- Color-coded diff display
- Restore buttons for each version
- Full metadata for both versions

#### `static/css/style.css` (UPDATED)
- Timeline styling with borders and spacing
- Diff view colors and markers
- Hover effects on version cards
- Responsive layout adjustments

#### `seed.py` (UPDATED)
- Updated to pass `edited_by` parameter when creating versions

## Database Schema (Firestore / JSON Fallback)

### Versions Collection
```
{
  'id': '<uuid>',
  'article_id': '<article_uuid>',
  'version_no': <integer>,
  'content': '<sanitized HTML>',
  'edited_at': <datetime>,
  'edited_by': '<editor name>'
}
```

## Usage

### Viewing Version History
1. Navigate to an article
2. Click "View Versions" button
3. See timeline of all versions with metadata

### Comparing Two Versions
1. In the versions page, click "Compare" next to a version
2. Or manually select two versions from the comparison page
3. View color-coded differences
4. Restore either version if needed

### Restoring a Version
1. Click "Restore" button on any version
2. Confirm in the dialog
3. Current version is automatically saved as new version
4. Selected version becomes the new current version

## File Structure
```
templates/
  ├── versions.html              (timeline view)
  └── compare_versions.html      (diff comparison)
utils/
  ├── parser.py                  (existing)
  └── diff.py                    (new - diff generation)
static/css/
  └── style.css                  (updated with version styles)
app.py                           (updated routes)
models.py                        (updated add_version signature)
seed.py                          (updated)
```

## Testing

To test the new features:

1. **Create an article** and make several edits
2. **Click "View Versions"** to see the timeline
3. **Click "Compare"** between versions to see diffs
4. **Test Restore** with confirmation dialogs
5. **Verify metadata** - timestamps and editor names display correctly

## Future Enhancements
- Add user authentication to track real user names
- Add version tagging/annotations
- Add batch version comparison (3+ versions)
- Export version history to CSV/JSON
- Add full-text search within versions
- Implement automatic version retention policies
