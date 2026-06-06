# 🔗 Wiki Linking Enhancement - Quick Start

## What's New

Your Personal Knowledge Base now has **intelligent wiki linking** with:
- ✅ Real-time autocomplete suggestions
- ✅ Article title suggestions as you type
- ✅ Missing-link warnings
- ✅ Link validation before saving
- ✅ Keyboard shortcuts for fast linking

## How to Use

### 1. Create a Link with Autocomplete

**In the editor, type:** `[[`

When you start typing `[[`, autocomplete suggestions appear below showing matching articles.

```
Editor: See the [[Getting
Suggestions: [Getting Started] [Getting Help] [Getting Better]
```

### 2. Select from Suggestions

Use **arrow keys** to navigate:
- **↓** - Next suggestion
- **↑** - Previous suggestion
- **Enter** - Insert selected article
- **Esc** - Close suggestions

Or click a suggestion directly.

### 3. Result

After selection, the link is inserted:
```
See the [[Getting Started]]
```

## Real-Time Validation

As you write, the system validates your links:

### ✅ Valid Link
```
[[Welcome]]  ← Green checkmark (article exists)
```

### ⚠️ Missing Link
```
[[Nonexistent Article]]  ← Warning box appears
```

The warning shows:
```
⚠️ Missing Links Detected
[[Nonexistent Article]] - Create article
```

## Features in Detail

### Autocomplete
- **Triggered by:** Typing `[[`
- **Shows:** Up to 8 matching article titles
- **Highlights:** Matching text in bold
- **Navigation:** Arrow keys or mouse
- **Selection:** Enter or click

### Validation
- **When:** Real-time as you type
- **Shows:** Yellow warning for missing links
- **Links:** Quick "Create article" buttons
- **Blocking:** Non-blocking (can save anyway)

### Link Format
```
[[Article Title]]
```
- **Title:** Exact article title (case-sensitive)
- **Spacing:** Spaces allowed in titles
- **Nesting:** Not supported (no `[[nested [[links]]]]`)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `[[` | Start link, show suggestions |
| `↓` | Next suggestion |
| `↑` | Previous suggestion |
| `Enter` | Select suggestion |
| `Esc` | Close suggestions |

## Common Workflows

### Workflow 1: Quick Link
1. Type `[[` 
2. Type article name (partial match works)
3. Press ↓ to select
4. Press Enter to insert

### Workflow 2: Reference Article Not Yet Created
1. Type `[[New Topic]]`
2. See warning: "Missing Links Detected"
3. Click "Create article"
4. Create the article
5. Return to original article
6. Link now works

### Workflow 3: Modify Existing Link
1. Delete the link text
2. Start new link with `[[`
3. Select from suggestions
4. Link updated

## Tips & Tricks

💡 **Type Partial Titles**
- Type `[[Getting` to see all articles starting with "Getting"
- Matching is case-insensitive

💡 **Use Suggestions Early**
- Press arrow keys immediately after `[[`
- Faster than typing full title

💡 **Create Missing Articles Later**
- Missing links don't block saving
- Create referenced articles anytime
- Links work once articles exist

💡 **Check Before Submitting**
- Review yellow warnings
- Click "Create article" links for missing topics
- Ensures all links work

## Examples

### Example 1: Creating a Getting Started Guide
```
New User Guide

See [[Welcome]] for introduction.
Follow [[Installation]] steps.
Check [[Configuration]] options.
```

If `Installation` doesn't exist yet:
⚠️ Warning shows: `[[Installation]]` with "Create article" link

Click link → create Installation article → link now works

### Example 2: Writing Technical Documentation
```
API Documentation

For details, see [[API Reference]].
Examples in [[Code Samples]].
Troubleshooting in [[FAQ]].
```

Autocomplete helps you find and link existing articles without typos.

## API Endpoints (For Developers)

### Get Autocomplete Suggestions
```
GET /api/articles/autocomplete?q=getting&limit=8
```

### Validate Links
```
POST /api/links/validate
{ "content": "See [[Welcome]] and [[Missing]]" }
```

### Check if Article Exists
```
GET /api/articles/exists?title=Welcome
```

## Troubleshooting

### Autocomplete not showing
- Ensure editor is focused
- Check browser console for errors
- Type `[[` (two square brackets)

### Suggestions seem slow
- Network latency
- Large number of articles
- Try more specific search

### Warning not appearing
- Refresh page
- Check form is submitting correctly

### Link not working after creation
- Verify article title matches exactly
- Links are case-sensitive in display
- Check article was saved

## See Also

- [WIKI_LINKING_GUIDE.md](WIKI_LINKING_GUIDE.md) - Technical guide
- [README.md](README.md) - Project overview
- [INDEX.md](INDEX.md) - Documentation index

---

**Server URL:** http://127.0.0.1:5000  
**Status:** ✅ Running with Wiki Linking enabled
