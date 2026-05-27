import Alpine from 'alpinejs';

/**
 * Modale d'aperçu d'une ressource ou recommandation.
 *
 * L'état (open/citation/resource/recommendation) est porté par le store
 * `$store.explorationIA.resourceModal` afin que n'importe quel composant
 * (bibliographie phase 1, sources phase 2, cartes synthèse phase 3) puisse
 * déclencher l'ouverture via `$store.explorationIA.openResourceModal(...)`.
 *
 * Ce composant fournit les utilitaires spécifiques à la modale : rendu HTML
 * du contenu avec surlignage du passage cité et auto-scroll vers le
 * surlignage.
 */
Alpine.data('ExplorationIAResourceModal', () => ({
  init() {
    // Quand la modale termine son chargement, scroller vers le passage surligné.
    this.$watch('$store.explorationIA.resourceModal.isLoading', (loading) => {
      if (!loading && this.$store.explorationIA.resourceModal.isOpen) {
        this.$nextTick(() => this.scrollToHighlight());
      }
    });
  },

  scrollToHighlight() {
    const modalBody = document.querySelector('.exploration-ia-modal__body');
    const highlight = modalBody?.querySelector('.exploration-ia-highlight');
    if (highlight && modalBody) {
      setTimeout(() => {
        highlight.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 100);
    }
  },

  /**
   * Surligne une citation dans un HTML déjà rendu.
   * Tolère les balises HTML insérées entre les mots.
   */
  highlightCitationInHtml(html, citationMarkdown) {
    if (!html || !citationMarkdown) return html;
    const cleanCitation = citationMarkdown
      .trim()
      .replace(/^["']|["']$/g, '')
      .trim();
    if (cleanCitation.length < 10) return html;

    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = this.$store.explorationIA.parseMarkdown(cleanCitation);
    const plainText = (tempDiv.textContent || '').trim();
    if (plainText.length < 10) return html;

    const escaped = plainText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const pattern = escaped.replace(/\s+/g, '(?:\\s|<[^>]*>)+');

    try {
      const regex = new RegExp(`(${pattern})`, 'gis');
      return html.replace(regex, '<mark class="exploration-ia-highlight">$1</mark>');
    } catch (e) {
      console.warn('Erreur regex highlight:', e);
      return html;
    }
  },

  getResourceContentWithHighlight() {
    const modal = this.$store.explorationIA.resourceModal;
    if (!modal.resource || !modal.citation) return '';
    const fullContent =
      modal.resource.content || modal.resource.text || modal.resource.summary || '';
    const htmlContent = this.$store.explorationIA.parseMarkdown(fullContent);
    return this.highlightCitationInHtml(htmlContent, modal.citation.content);
  },

  getRecommendationContentWithHighlight() {
    const modal = this.$store.explorationIA.resourceModal;
    if (!modal.recommendation || !modal.citation) return '';
    const fullContent =
      modal.recommendation.content ||
      modal.recommendation.comment ||
      modal.recommendation.intent ||
      '';
    const htmlContent = this.$store.explorationIA.parseMarkdown(fullContent);
    return this.highlightCitationInHtml(htmlContent, modal.citation.content);
  },
}));
