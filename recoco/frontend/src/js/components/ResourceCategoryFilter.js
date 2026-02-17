import Alpine from 'alpinejs';

Alpine.data('ResourceFilter', (categoryOptions) => ({

    selected: [],
    selectedIds: [],
    options: categoryOptions || [],
    categoryMap: Object.fromEntries(categoryOptions.map(cat => [cat.value, 'cat' + cat.value])),

    init() {
        const params = new URLSearchParams(document.location.search);
        const reverseMap = Object.fromEntries(
            Object.entries(this.categoryMap).map(([k, v]) => [v, k])
        );
        for (const [key, value] of params) {
            if (reverseMap[key] && value === 'on') {
                this.selected.push(reverseMap[key]);
                this.selectedIds.push(reverseMap[key]);
            }
        }
    },
}));
