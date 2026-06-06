/**
 * Wiki Link Autocomplete and Validator
 * Provides real-time suggestions for internal links and validates links before saving
 */

class WikiLinkAutocomplete {
  constructor(editorSelector) {
    this.editor = document.querySelector(editorSelector);
    this.suggestionBox = null;
    this.currentQuery = '';
    this.linkPattern = /\[\[([^\[\]]*?)$/;
    this.setupEvents();
    this.setupUI();
  }

  setupUI() {
    // Create suggestion box
    this.suggestionBox = document.createElement('div');
    this.suggestionBox.id = 'wiki-suggestions';
    this.suggestionBox.className = 'wiki-suggestions hidden';
    this.editor.parentElement.appendChild(this.suggestionBox);

    // Create validation warning box
    this.warningBox = document.createElement('div');
    this.warningBox.id = 'wiki-warnings';
    this.warningBox.className = 'wiki-warnings hidden';
    this.editor.parentElement.appendChild(this.warningBox);
  }

  setupEvents() {
    this.editor.addEventListener('keyup', (e) => this.handleKeyUp(e));
    this.editor.addEventListener('keydown', (e) => this.handleKeyDown(e));
    this.editor.addEventListener('blur', () => this.hideSuggestions());
  }

  async handleKeyUp(e) {
    // Get text from cursor back to [[ 
    const text = this.editor.value;
    const cursorPos = this.editor.selectionStart;
    const textBeforeCursor = text.substring(0, cursorPos);

    const match = textBeforeCursor.match(this.linkPattern);

    if (match) {
      this.currentQuery = match[1];
      if (this.currentQuery.length > 0) {
        await this.fetchSuggestions(this.currentQuery);
      } else {
        this.hideSuggestions();
      }
    } else {
      this.hideSuggestions();
    }
  }

  handleKeyDown(e) {
    if (this.suggestionBox.classList.contains('hidden')) return;

    const suggestions = this.suggestionBox.querySelectorAll('.suggestion-item');
    const active = this.suggestionBox.querySelector('.suggestion-item.active');

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (!active) {
          suggestions[0]?.classList.add('active');
        } else {
          const next = active.nextElementSibling;
          if (next) {
            active.classList.remove('active');
            next.classList.add('active');
          }
        }
        break;

      case 'ArrowUp':
        e.preventDefault();
        if (active) {
          const prev = active.previousElementSibling;
          if (prev) {
            active.classList.remove('active');
            prev.classList.add('active');
          } else {
            active.classList.remove('active');
          }
        }
        break;

      case 'Enter':
        if (active) {
          e.preventDefault();
          this.selectSuggestion(active.textContent);
        }
        break;

      case 'Escape':
        e.preventDefault();
        this.hideSuggestions();
        break;
    }
  }

  async fetchSuggestions(query) {
    try {
      const response = await fetch(`/api/articles/autocomplete?q=${encodeURIComponent(query)}&limit=8`);
      const data = await response.json();

      if (data.suggestions && data.suggestions.length > 0) {
        this.showSuggestions(data.suggestions);
      } else {
        this.hideSuggestions();
      }
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      this.hideSuggestions();
    }
  }

  showSuggestions(suggestions) {
    this.suggestionBox.innerHTML = suggestions
      .map((s) => `<div class="suggestion-item" data-title="${s}">${this.highlightMatch(s)}</div>`)
      .join('');

    this.suggestionBox.classList.remove('hidden');

    // Add click handlers
    this.suggestionBox.querySelectorAll('.suggestion-item').forEach((item) => {
      item.addEventListener('click', () => {
        this.selectSuggestion(item.textContent.replace(/<[^>]*>/g, ''));
      });
      item.addEventListener('mouseenter', () => {
        this.suggestionBox.querySelectorAll('.suggestion-item').forEach((i) => i.classList.remove('active'));
        item.classList.add('active');
      });
    });
  }

  hideSuggestions() {
    this.suggestionBox.classList.add('hidden');
    this.suggestionBox.innerHTML = '';
  }

  selectSuggestion(title) {
    const text = this.editor.value;
    const cursorPos = this.editor.selectionStart;
    const textBeforeCursor = text.substring(0, cursorPos);

    // Find the [[ position
    const linkStart = textBeforeCursor.lastIndexOf('[[');
    if (linkStart === -1) return;

    // Replace from [[ to cursor with [[Title]]
    const newText = text.substring(0, linkStart) + '[[' + title + ']]' + text.substring(cursorPos);

    this.editor.value = newText;
    this.editor.selectionStart = linkStart + title.length + 4;
    this.editor.selectionEnd = this.editor.selectionStart;

    this.hideSuggestions();
    this.editor.focus();

    // Trigger input event for form change detection
    this.editor.dispatchEvent(new Event('input', { bubbles: true }));
  }

  highlightMatch(title) {
    const query = this.currentQuery;
    const regex = new RegExp(`(${query})`, 'gi');
    return title.replace(regex, '<strong>$1</strong>');
  }
}

// Link Validator
class WikiLinkValidator {
  constructor(editorSelector, formSelector) {
    this.editor = document.querySelector(editorSelector);
    this.form = document.querySelector(formSelector);
    this.warningBox = null;
    this.setupUI();
    this.setupForm();
  }

  setupUI() {
    this.warningBox = document.createElement('div');
    this.warningBox.id = 'wiki-validation-warnings';
    this.warningBox.className = 'wiki-validation-warnings hidden';
    this.form.insertBefore(this.warningBox, this.form.firstChild);
  }

  setupForm() {
    this.form.addEventListener('submit', async (e) => {
      // Validate before submit
      const isValid = await this.validate();
      if (!isValid) {
        e.preventDefault();
        this.showWarnings();
      }
    });

    // Real-time validation as user types
    this.editor.addEventListener('input', () => {
      this.validateAsync();
    });
  }

  async validate() {
    const content = this.editor.value;

    try {
      const response = await fetch('/api/links/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      });

      const data = await response.json();
      this.validationData = data;

      return !data.has_missing;
    } catch (error) {
      console.error('Validation error:', error);
      return true; // Allow submit on error
    }
  }

  async validateAsync() {
    const content = this.editor.value;

    try {
      const response = await fetch('/api/links/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      });

      const data = await response.json();
      this.validationData = data;

      if (data.has_missing) {
        this.displayWarnings(data.missing);
      } else {
        this.clearWarnings();
      }
    } catch (error) {
      console.error('Validation error:', error);
    }
  }

  displayWarnings(missingLinks) {
    this.warningBox.innerHTML = `
      <div class="alert alert-warning" role="alert">
        <strong>⚠️ Missing Links Detected</strong>
        <p>The following internal links reference articles that don't exist yet:</p>
        <ul>
          ${missingLinks.map((link) => `<li><code>[[${link}]]</code> - <a href="/articles/new" target="_blank">Create article</a></li>`).join('')}
        </ul>
        <small>You can still save, but these links will not work until the articles are created.</small>
      </div>
    `;
    this.warningBox.classList.remove('hidden');
  }

  clearWarnings() {
    this.warningBox.classList.add('hidden');
    this.warningBox.innerHTML = '';
  }

  showWarnings() {
    if (this.validationData && this.validationData.has_missing) {
      this.displayWarnings(this.validationData.missing);
    }
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const editor = document.getElementById('editor');
  
  if (editor) {
    // Initialize autocomplete
    new WikiLinkAutocomplete('#editor');

    // Initialize validator
    const form = document.querySelector('form');
    if (form) {
      new WikiLinkValidator('#editor', 'form');
    }
  }
});
