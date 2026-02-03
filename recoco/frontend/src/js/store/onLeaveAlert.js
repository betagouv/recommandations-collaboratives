import Alpine from 'alpinejs';

/**
 * Store global pour gérer les alertes de sortie avec saisie en cours.
 *
 * Usage depuis n'importe quel composant :
 *
 *   // Signaler une saisie en cours
 *   this.$store.onLeaveAlert.setDirty(true);
 *
 *   // Signaler la fin de la saisie (après submit)
 *   this.$store.onLeaveAlert.setDirty(false);
 *
 * Le store intercepte automatiquement :
 * - La fermeture de l'onglet/navigateur (beforeunload)
 * - Les clics sur les liens de navigation
 */
Alpine.store('onLeaveAlert', {
  isDirty: false,
  isOpen: false,
  pendingNavigation: null,

  init() {
    this.setupBeforeUnload();
    this.setupNavigationInterception();
  },

  /**
   * Définit l'état de saisie en cours
   */
  setDirty(value) {
    this.isDirty = value;
  },

  /**
   * Configure l'événement beforeunload
   */
  setupBeforeUnload() {
    window.addEventListener('beforeunload', (event) => {
      if (this.isDirty) {
        event.preventDefault();
      }
    });
  },

  /**
   * Intercepte les clics sur les liens
   */
  setupNavigationInterception() {
    document.addEventListener(
      'click',
      (event) => {
        if (!this.isDirty) return;

        const link = event.target.closest('a[href]');
        if (!link) return;

        // Ignorer certains liens
        if (link.matches('[data-no-leave-alert]')) return;
        if (link.target === '_blank') return;
        if (link.hasAttribute('aria-controls')) return;

        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('javascript:'))
          return;

        event.preventDefault();
        event.stopPropagation();
        this.pendingNavigation = href;
        this.isOpen = true;
      },
      true
    );
  },

  /**
   * Confirme la sortie
   */
  confirmLeave() {
    const href = this.pendingNavigation;
    this.isDirty = false;
    this.isOpen = false;
    this.pendingNavigation = null;

    if (href) {
      window.location.href = href;
    }
  },

  /**
   * Annule la sortie
   */
  cancelLeave() {
    this.isOpen = false;
    this.pendingNavigation = null;
  },
});

export default Alpine.store('onLeaveAlert');
