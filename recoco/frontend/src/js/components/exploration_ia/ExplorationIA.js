import Alpine from 'alpinejs';

/**
 * Orchestrateur léger de la page d'exploration IA.
 *
 * Initialise le store global avec la configuration injectée par Django et
 * gère les comportements transverses (scroll vers le haut sur changement
 * de phase). Tout l'état métier vit dans `$store.explorationIA`.
 */
Alpine.data('ExplorationIA', (config = {}) => ({
  init() {
    // contexte projet sérialisé en JSON pour éviter les injections JS via le nom du projet ou de la commune.
    const contextEl = document.getElementById('exploration-ia-context');
    const projectContext = contextEl ? JSON.parse(contextEl.textContent) : '';
    this.$store.explorationIA.setup({ ...config, projectContext });
    this.$watch('$store.explorationIA.currentPhase', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  },
}));
