# Version History Feature - Quick Start Guide

## 🚀 Getting Started

The app now includes a powerful version history system. Here's how to use it:

## 📋 Basic Workflow

### Step 1: Create or Edit an Article
1. Click "New Article" or "Edit"
2. Make changes using the TinyMCE editor
3. Save the article
4. The current version is automatically saved

### Step 2: View Version History
1. From an article, click the **"View Versions"** button
2. See a timeline of all versions
3. Each version shows:
   - **Version number** (e.g., "Version 2")
   - **When it was edited** (timestamp)
   - **Who edited it** (editor name)
   - **Preview of content** (first 200 characters)

### Step 3: Compare Two Versions
1. In the versions timeline, click **"Compare"** next to a version
2. Or manually select two versions using dropdown menus
3. View the diff with color coding:
   - 🔴 **Red** = lines that were removed
   - 🟢 **Green** = lines that were added
   - ⚪ **Gray** = unchanged lines

### Step 4: Restore an Old Version
1. Click **"Restore"** on any version
2. Confirm the action (dialog will ask: "Are you sure?")
3. The old version becomes the current version
4. Your previous current version is saved as a new version
5. You're taken back to the article view

## 🎨 UI Elements Explained

### Timeline View (`/articles/<id>/versions`)

```
┌─────────────────────────────────────────────┐
│ Version 3                                   │
│ 📅 2025-02-05 14:30  👤 John Doe           │
├─────────────────────────────────────────────┤
│ Content preview: "This is the updated...   │
├─────────────────────────────────────────────┤
│ [Restore]  [Compare]                        │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Version 2                                   │
│ 📅 2025-02-05 14:15  👤 System             │
├─────────────────────────────────────────────┤
│ Content preview: "Initial version of wel...│
├─────────────────────────────────────────────┤
│ [Restore]  [Compare]                        │
└─────────────────────────────────────────────┘
```

### Comparison View (`/articles/<id>/compare?v1=...&v2=...`)

```
FROM Version 1            TO Version 2
[Select Version ▼]       [Select Version ▼]

─────────────────────────────────────
- This is the old line
- Another old line
+ This is the new line
+ A different new line
  Unchanged line stays the same
─────────────────────────────────────

[Restore Version 1]  [Restore Version 2]
```

## 🔑 Key Concepts

### **Automatic Versioning**
- Every time you edit an article, the old version is saved
- No manual version control needed
- All versions are preserved

### **Safe Restoration**
- Restoring an old version doesn't lose work
- Current version is automatically saved as a new version
- You can always restore forward again

### **Editor Tracking**
- Each version shows who made the edit
- Timestamp shows exactly when
- Helps track changes over time

### **Diff View**
- Easy to see what changed between versions
- Color-coded for quick scanning
- Shows exact line-level changes

## 🔗 Routes Reference

| Route | Method | Purpose |
|-------|--------|---------|
| `/articles/<id>/versions` | GET | View version timeline |
| `/articles/<id>/compare?v1=<vid>&v2=<vid>` | GET | Compare two versions |
| `/articles/<id>/restore/<vid>` | POST | Restore a version |

## ⚙️ Technical Details

### Version Storage
Each version record contains:
- `version_no` - Sequential version number
- `content` - The article content (sanitized HTML)
- `edited_at` - Timestamp (UTC datetime)
- `edited_by` - Name of editor (defaults to "System")
- `article_id` - Reference to the article

### Diff Algorithm
- Uses Python's `difflib.Differ` for line-by-line comparison
- Generates HTML with color-coded changes
- Removed lines show with `−` marker
- Added lines show with `+` marker

### Storage
- Primary: Firestore collection `versions`
- Fallback: Local JSON file `data/versions.json`
- Works with or without Firebase credentials

## 💡 Tips & Tricks

1. **Frequent Saves**: Edit and save often - each save creates a new version
2. **Descriptive Edits**: When editing, make focused changes so diffs are clear
3. **Compare Before Restore**: Use comparison to verify changes before restoring
4. **Email to Team**: Use comparison view for code reviews / discussions
5. **Documentation**: Use version history to track article evolution

## 🐛 Troubleshooting

### "No versions found"
- Article was just created
- Make an edit and save to create the first version

### Timestamps are UTC
- All timestamps stored in UTC timezone
- Consider converting to local time in future updates

### Compare button missing
- Only shows between non-final versions
- Last version has no "Compare" (nothing to compare to)

## 📖 See Also
- [VERSION_HISTORY_FEATURES.md](VERSION_HISTORY_FEATURES.md) - Detailed feature documentation
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical implementation details
- [README.md](README.md) - Project overview
