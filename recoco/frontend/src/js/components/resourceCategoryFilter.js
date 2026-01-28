import Alpine from 'alpinejs';

Alpine.data('ResourceFilter', (categoryOptions) => ({

    selected: [],
    selectedIds: [],
    options: categoryOptions || [],
    categoryMap: categoryOptions.map(cat => 'cat'+cat.value),

    init() {
        const params = new URLSearchParams(document.location.search);
        for (const [key, value] of params) {
            if (this.categoryMap.includes(key) && value === 'on') {
                this.selected.push(this.categoryMap.indexOf(key).toString());
                this.selectedIds.push(this.categoryMap.indexOf(key).toString());
                console.log('preselected category:', key);
            }
        }

    },
}));
