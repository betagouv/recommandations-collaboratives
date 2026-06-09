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
    const projectContext = {
      name: document.getElementById('project-name'),
      description: document.getElementById('project-description'),
      location: document.getElementById('project-commune-name'),
      postal: document.getElementById('project-commune-postal'),
      department: document.getElementById('project-department-code'),
      region: document.getElementById('project-region'),
      tags: document.getElementById('project-tags'),
    };
    for (const key in projectContext) {
      projectContext[key] = projectContext[key]
        ? JSON.parse(projectContext[key].textContent)
        : '';
    }

    config.CSRFToken = [
      ...document.getElementsByName('csrfmiddlewaretoken'),
    ][0].value;
    this.$store.explorationIA.setup({ ...config, projectContext });
    this.$watch('$store.explorationIA.currentPhase', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  },
}));
