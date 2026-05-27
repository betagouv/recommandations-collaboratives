import Alpine from 'alpinejs';

Alpine.data('DepartmentsFilterWrapper', (initialCodes = []) => ({
  selectedCodes: initialCodes,

  normalize(payload) {
    if (!payload) return [];
    if (Array.isArray(payload) && typeof payload[0] === 'string') return payload;
    if (Array.isArray(payload) && typeof payload[0] === 'object') {
      return payload.filter((d) => d.active).map((d) => d.code);
    }
    return [];
  },
}));
