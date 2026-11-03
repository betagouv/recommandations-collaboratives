import Alpine from 'alpinejs';

Alpine.data('ExplorationIAWelcomeModal', () => ({
  isOpen: false,

  init() {
    window.addEventListener('exploration-ia:open-welcome-modal', () => this.open());
  },

  open() {
    this.isOpen = true;
  },

  close() {
    this.isOpen = false;
  },
}));
