import Alpine from 'alpinejs';

Alpine.data('ExpandableMenuHandler', () => {
  return {
    toggle() {
      if (this.$refs.expandMenuButton.ariaExpanded == 'true') {
        this.$refs.expandMenuButton.ariaExpanded = 'false';
      }
    },
  };
});
