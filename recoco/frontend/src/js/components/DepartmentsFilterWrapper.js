import Alpine from 'alpinejs';

Alpine.data(
  'DepartmentsFilterWrapper',
  (initialCodes = [], initiallyAllSelected = false) => ({
    selectedCodes: initialCodes,
    allSelected: initiallyAllSelected,
    pendingAllSelect: false,

    normalize(payload) {
      if (!payload) return [];
      if (Array.isArray(payload) && typeof payload[0] === 'string')
        return payload;
      if (Array.isArray(payload) && typeof payload[0] === 'object') {
        return payload.filter((d) => d.active).map((d) => d.code);
      }
      return [];
    },

    onSelectAll(detail) {
      this.allSelected = Boolean(detail);
      this.pendingAllSelect = true;
    },

    onSelected(detail) {
      this.selectedCodes = this.normalize(detail);
      if (!this.pendingAllSelect) {
        this.allSelected = false;
      }
      this.pendingAllSelect = false;
    },
  })
);
