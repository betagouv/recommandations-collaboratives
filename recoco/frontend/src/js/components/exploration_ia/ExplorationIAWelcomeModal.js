import Alpine from 'alpinejs';

/**
 * Modale d'accueil affichée une seule fois par utilisateur (persistance
 * `localStorage`). Le bouton "Revoir l'aide" appelle `open()` pour la
 * rouvrir manuellement.
 */
Alpine.data('ExplorationIAWelcomeModal', () => ({
  storageKey: 'explorationIA_welcomeShown',
  isOpen: false,

  init() {
    try {
      if (!localStorage.getItem(this.storageKey)) {
        this.isOpen = true;
      }
    } catch (e) {
      // localStorage indisponible (mode privé, etc.) : on n'affiche pas la modale.
    }
    // Permet au bouton "Revoir l'aide" (en dehors du scope de la modale)
    // de la rouvrir via un événement global.
    window.addEventListener('exploration-ia:open-welcome-modal', () => this.open());
  },

  open() {
    this.isOpen = true;
  },

  close() {
    this.isOpen = false;
    try {
      localStorage.setItem(this.storageKey, 'true');
    } catch (e) {
      // ignore
    }
  },
}));
