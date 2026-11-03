import Alpine from 'alpinejs';

const STORAGE_KEY = 'crm-org-merge-selected';

Alpine.data('OrgMergeSelection', (justMerged = false) => ({
  selected: [],

  init() {
    if (justMerged) {
      this.clearSelection();
    } else {
      this.selected = this.loadSelection();
    }

    this.$watch('selected', (value) => {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
    });
  },

  loadSelection() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  },

  clearSelection() {
    this.selected = [];
    localStorage.removeItem(STORAGE_KEY);
  },
}));
