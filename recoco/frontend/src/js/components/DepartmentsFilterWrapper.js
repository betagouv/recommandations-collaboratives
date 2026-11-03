import Alpine from 'alpinejs';

Alpine.data('DepartmentsFilterWrapper', (initialCodes = []) => ({
  selectedCodes: initialCodes,
  allSelected: false,
  _justSelectedAll: false,

  normalize(payload) {
    if (!payload) return [];
    if (Array.isArray(payload) && typeof payload[0] === 'string') return payload;
    if (Array.isArray(payload) && typeof payload[0] === 'object') {
      return payload.filter((d) => d.active).map((d) => d.code);
    }
    return [];
  },

  onSelectAll(detail) {
    this.allSelected = Boolean(detail);
    this._justSelectedAll = true;
  },

  onSelected(detail) {
    this.selectedCodes = this.normalize(detail);
    if (!this._justSelectedAll) this.allSelected = false;
    this._justSelectedAll = false;
  },
}));
