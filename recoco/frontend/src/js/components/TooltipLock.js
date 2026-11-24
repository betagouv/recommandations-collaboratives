import Alpine from 'alpinejs';

Alpine.data('TooltipLock', () => {
  return {
    tooltipProps() {
      return {
        content: () => this.$refs.template.innerHTML,
        allowHTML: true,
        interactive: true,
        placement: 'bottom',
        theme: 'light-border',
        appendTo: document.body
      }
    },
  };
});
