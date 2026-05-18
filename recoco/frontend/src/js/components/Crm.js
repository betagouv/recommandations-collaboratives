import Alpine from 'alpinejs';

Alpine.data('Crm', Crm);

function Crm() {
  return {
    init() {
      // Sidebar behaviour
      const sidebar = this.$refs.sidebar;
      if (!sidebar) return;
      const sidebarHeight = sidebar.offsetHeight;
      const windowHeight = window.innerHeight;

      if (sidebarHeight > windowHeight) {
        sidebar.classList.remove('crm-sticky');
        sidebar.classList.add('crm-relative');
      }
    },
    goBack() {
      console.debug('go back');
      window.history.back();
    },
  };
}
