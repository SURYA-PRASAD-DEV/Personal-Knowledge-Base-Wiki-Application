# Enhanced Wiki Linking - Implementation Guide

## Overview
The wiki linking system now includes intelligent autocomplete, real-time validation, and missing-link warnings to improve the authoring experience.

## Features Implemented

### 1. **Autocomplete Suggestions** ✓
- As you type `[[`, suggestions appear automatically
- Shows matching article titles in real-time
- Navigate with arrow keys, select with Enter
- Keyboard shortcuts: ↑/↓ for navigation, Enter to select, Esc to dismiss

### 2. **Article Title Autocomplete** ✓
- Fuzzy matching of article titles (case-insensitive)
- Displays up to 8 matches
- Matched text highlighted in bold
- Mouse and keyboard support

### 3. **Link Validation** ✓
- Real-time validation as you type
- Check which links reference existing articles
- Identifies broken/missing links

### 4. **Missing-Link Warning** ✓
- Yellow warning box shows missing links
- Lists all references that don't have articles yet
- Quick links to create missing articles
- Non-blocking: can still save with missing links

## Backend API Endpoints

### `GET /api/articles/autocomplete`
Returns article titles matching a query.

**Parameters:**
- `q` (string) - Search query (case-insensitive)
- `limit` (int, default=10) - Max results to return

**Response:**
```json
{
  "suggestions": ["Getting Started", "Welcome", "Git Guide"]
}
```

### `POST /api/links/validate`
Validates internal links in content.

**Request Body:**
```json
{
  "content": "See [[Welcome]] and [[Missing Article]]"
}
```

**Response:**
```json
{
  "valid": ["Welcome"],
  "missing": ["Missing Article"],
  "total": 2,
  "has_missing": true
}
```

### `GET /api/articles/exists`
Checks if an article with a given title exists.

**Parameters:**
- `title` (string) - Article title

**Response:**
```json
{
  "exists": true,
  "title": "Welcome"
}
```

## Frontend Components

### WikiLinkAutocomplete Class
Handles real-time suggestions while typing.

**Features:**
- Monitors keystrokes for `[[` pattern
- Fetches suggestions from API
- Displays suggestion dropdown
- Handles keyboard navigation
- Replaces `[[Query` with `[[Title]]` on selection

**Usage:**
```javascript
new WikiLinkAutocomplete('#editor');
```

### WikiLinkValidator Class
Validates links and shows warnings.

**Features:**
- Real-time validation as user types
- Pre-submit validation check
- Displays missing links with context
- Non-blocking warnings

**Usage:**
```javascript
new WikiLinkValidator('#editor', 'form');
```

## UI Elements

### Suggestion Box
- Position: Absolute, below editor
- Style: White box with border and shadow
- Items: Clickable, keyboard-navigable
- Highlight: Active item has blue background

### Validation Warning
- Position: Top of form
- Style: Bootstrap alert (yellow)
- Content: List of missing links
- Links: Quick "Create article" buttons

## CSS Classes

### Autocomplete
- `.wiki-suggestions` - Suggestion container
- `.suggestion-item` - Individual suggestion
- `.suggestion-item.active` - Active suggestion
- `.hidden` - Hidden state

### Validation
- `.wiki-validation-warnings` - Warning container
- `.alert` - Bootstrap alert styling
- `.hidden` - Hidden state

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↓` | Next suggestion |
| `↑` | Previous suggestion |
| `Enter` | Select active suggestion |
| `Esc` | Close suggestions |

## Integration with TinyMCE

The autocomplete works with TinyMCE editor through:
1. Textarea fallback for link detection
2. Content sync from editor to validation
3. Link pattern matching in both textarea and editor content

**TinyMCE Setup:**
```javascript
setup: function(editor) {
  editor.on('change', function() {
    // Sync to textarea for validation
    document.getElementById('editor').value = editor.getContent();
    document.getElementById('editor').dispatchEvent(new Event('input'));
  });
}
```

## Link Pattern

The system recognizes wiki links using this pattern:
```regex
\[\[([^\[\]]+)\]\]
```

Examples:
- `[[Welcome]]` ✓ Valid
- `[[Getting Started]]` ✓ Valid
- `[[Article with [[nested]]]]` ✗ Not supported (no nesting)

## File Structure

```
static/
├── js/
│   └── wiki-autocomplete.js      ← Main autocomplete/validator logic
├── css/
│   └── style.css                 ← Updated with autocomplete styles
└── ... (existing files)

templates/
└── article_form.html             ← Updated with script inclusion

app.py                            ← 3 new API endpoints
```

## Usage Examples

### Example 1: Creating a Link with Autocomplete
1. Type `See the [[` in editor
2. Autocomplete shows suggestions: `[Welcome] [Getting Started] [Git Guide]`
3. Press ↓ to select `Getting Started`
4. Press Enter to insert `[[Getting Started]]`
5. Result: `See the [[Getting Started]]`

### Example 2: Missing Link Warning
1. Type `Check [[Nonexistent Article]]`
2. As you type, validation runs
3. Yellow warning appears: "⚠️ Missing Links Detected"
4. Shows: `[[Nonexistent Article]]` with "Create article" link
5. Can still save; link shows broken until article created

### Example 3: Submit with Validation
1. Edit article with broken links
2. Click Save
3. If missing links exist, warning is shown
4. Still allows save (non-blocking)
5. Missing links become functional once articles are created

## Error Handling

- **API errors**: Silently fail, continue without suggestions
- **Validation errors**: Show generic warning, allow save
- **Network issues**: Graceful degradation to manual linking
- **Missing editor**: Script checks for element existence

## Performance Considerations

- Debounced API calls to reduce server load
- Regex-based pattern matching (client-side)
- Limit: 8 suggestions per query
- Article list cached in local searches

## Security Notes

- User input sanitized via regex (no arbitrary code)
- API responses validated before display
- HTML entities escaped in suggestions
- No direct database queries from frontend

## Future Enhancements

1. **Recent Links** - Show recently created articles
2. **Link Popularity** - Suggest frequently linked articles
3. **Fuzzy Search** - Improved matching algorithm
4. **Link Preview** - Hover to see article preview
5. **Backlinks** - Show what links to current article
6. **Link Validation** - Automatic link checking on save
7. **Redirect Links** - Handle article renames

## Testing Checklist

- [x] Autocomplete appears on `[[`
- [x] Arrow keys navigate suggestions
- [x] Enter selects suggestion
- [x] Esc closes suggestions
- [x] Missing links detected
- [x] Warning displays correctly
- [x] Can save with missing links
- [x] Links work after article created
- [x] Responsive on mobile
- [x] Works with TinyMCE
- [x] API endpoints return correct data

## Troubleshooting

### Autocomplete not showing
- Check browser console for errors
- Verify `/api/articles/autocomplete` endpoint is working
- Ensure textarea has `id="editor"`
- Check JavaScript file is loaded

### Validation not working
- Verify form selector matches `<form>` tag
- Check `/api/links/validate` endpoint
- Ensure TinyMCE content syncs to textarea

### Styling issues
- Verify CSS file loaded (check browser dev tools)
- Check z-index: 1000 for suggestions
- Test in different browsers

## API Documentation

See [app.py](../app.py) lines ~130-160 for endpoint implementations.
