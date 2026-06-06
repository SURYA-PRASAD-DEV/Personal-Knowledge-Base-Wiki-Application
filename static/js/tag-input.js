/**
 * Tag Input Component
 * Provides multi-select tag input with autocomplete suggestions
 */

class TagInput {
  constructor(inputSelector, suggestionsSelector, selectedSelector, hiddenInputSelector) {
    this.input = document.querySelector(inputSelector);
    this.suggestionsBox = document.querySelector(suggestionsSelector);
    this.selectedTagsContainer = document.querySelector(selectedSelector);
    this.hiddenInput = document.querySelector(hiddenInputSelector);
    this.selectedTags = new Set();
    
    if (!this.input) return;
    
    this.initializeSelectedTags();
    this.attachListeners();
  }

  initializeSelectedTags() {
    // Parse already selected tags from the container
    const tagElements = this.selectedTagsContainer.querySelectorAll('.tag-selected');
    tagElements.forEach(el => {
      const tagName = el.dataset.tag;
      if (tagName) {
        this.selectedTags.add(tagName);
      }
    });
  }

  attachListeners() {
    this.input.addEventListener('input', (e) => this.handleInput(e));
    this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
    this.input.addEventListener('blur', () => this.hideSuggestions());

    // Delegate click on remove buttons
    this.selectedTagsContainer.addEventListener('click', (e) => {
      if (e.target.classList.contains('btn-remove-tag')) {
        e.preventDefault();
        const tagEl = e.target.parentElement;
        const tagName = tagEl.dataset.tag;
        this.removeTag(tagName);
      }
    });
  }

  async handleInput(e) {
    const query = e.target.value.trim();
    
    if (!query || query.length < 1) {
      this.hideSuggestions();
      return;
    }

    // Check if user just typed a comma (tag delimiter)
    if (query.endsWith(',')) {
      const newTag = query.slice(0, -1).trim();
      if (newTag && !this.selectedTags.has(newTag)) {
        this.addTag(newTag);
        this.input.value = '';
      }
      return;
    }

    await this.fetchSuggestions(query);
  }

  handleKeydown(e) {
    const suggestions = this.suggestionsBox.querySelectorAll('.suggestion-item');
    
    if (e.key === 'Enter') {
      e.preventDefault();
      const activeSuggestion = this.suggestionsBox.querySelector('.suggestion-item.active');
      if (activeSuggestion) {
        this.selectSuggestion(activeSuggestion.dataset.tag);
      } else {
        const inputValue = this.input.value.trim();
        if (inputValue && !this.selectedTags.has(inputValue)) {
          this.addTag(inputValue);
          this.input.value = '';
        }
      }
      return;
    }

    if (e.key === 'Escape') {
      this.hideSuggestions();
      return;
    }

    if (e.key === 'Backspace' && !this.input.value && this.selectedTags.size > 0) {
      // Remove last tag when pressing backspace with empty input
      const lastTag = Array.from(this.selectedTags).pop();
      if (lastTag) {
        this.removeTag(lastTag);
      }
      return;
    }

    // Arrow key navigation
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      const active = this.suggestionsBox.querySelector('.suggestion-item.active');
      if (!active && suggestions.length > 0) {
        suggestions[0].classList.add('active');
      } else if (active) {
        const next = active.nextElementSibling;
        if (next && next.classList.contains('suggestion-item')) {
          active.classList.remove('active');
          next.classList.add('active');
        }
      }
      return;
    }

    if (e.key === 'ArrowUp') {
      e.preventDefault();
      const active = this.suggestionsBox.querySelector('.suggestion-item.active');
      if (active) {
        const prev = active.previousElementSibling;
        if (prev && prev.classList.contains('suggestion-item')) {
          active.classList.remove('active');
          prev.classList.add('active');
        }
      }
      return;
    }
  }

  async fetchSuggestions(query) {
    try {
      const response = await fetch(`/api/tags/suggestions?q=${encodeURIComponent(query)}&limit=8`);
      const data = await response.json();
      this.showSuggestions(data.suggestions || [], query);
    } catch (error) {
      console.error('Tag suggestion fetch failed:', error);
    }
  }

  showSuggestions(suggestions, query) {
    this.suggestionsBox.innerHTML = '';

    // Filter out already selected tags
    const filtered = suggestions.filter(item => !this.selectedTags.has(item.tag));

    if (filtered.length === 0) {
      this.suggestionsBox.style.display = 'none';
      return;
    }

    filtered.forEach(item => {
      const div = document.createElement('div');
      div.className = 'suggestion-item';
      div.dataset.tag = item.tag;
      div.style.borderLeft = `4px solid ${item.color}`;
      
      // Highlight matching text
      const highlighted = this.highlightMatch(item.tag, query);
      div.innerHTML = `${highlighted} <span class="tag-count-small">${item.count}</span>`;
      
      div.addEventListener('click', () => this.selectSuggestion(item.tag));
      div.addEventListener('mouseenter', () => {
        this.suggestionsBox.querySelectorAll('.suggestion-item').forEach(el => el.classList.remove('active'));
        div.classList.add('active');
      });
      
      this.suggestionsBox.appendChild(div);
    });

    this.suggestionsBox.style.display = 'block';
  }

  highlightMatch(text, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<strong>$1</strong>');
  }

  selectSuggestion(tagName) {
    this.addTag(tagName);
    this.input.value = '';
    this.hideSuggestions();
    this.input.focus();
  }

  addTag(tagName) {
    tagName = tagName.trim();
    if (!tagName || this.selectedTags.has(tagName)) return;

    this.selectedTags.add(tagName);
    
    // Create tag element
    const span = document.createElement('span');
    span.className = 'tag-selected';
    span.dataset.tag = tagName;
    span.innerHTML = `${tagName} <button type="button" class="btn-remove-tag">×</button>`;
    
    this.selectedTagsContainer.appendChild(span);
    this.updateHiddenInput();
  }

  removeTag(tagName) {
    this.selectedTags.delete(tagName);
    
    const tagEl = this.selectedTagsContainer.querySelector(`[data-tag="${tagName}"]`);
    if (tagEl) {
      tagEl.remove();
    }
    
    this.updateHiddenInput();
  }

  updateHiddenInput() {
    const tagsArray = Array.from(this.selectedTags);
    this.hiddenInput.value = tagsArray.join(', ');
  }

  hideSuggestions() {
    this.suggestionsBox.style.display = 'none';
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new TagInput('#tagInput', '#tagSuggestions', '#selectedTags', '#tagsHidden');
});
