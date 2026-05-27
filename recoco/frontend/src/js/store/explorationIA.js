import Alpine from 'alpinejs';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { askLLM, fetchCoRecommendations } from '../utils/llmClient';
import { ToastType } from '../models/toastType';

/**
 * Store global de la page d'exploration assistée par IA.
 *
 * Porte tout l'état partagé entre les phases (1: recherche, 2: co-recos,
 * 3: synthèse) et les modales, ainsi que la logique métier (appels LLM,
 * synthèse, navigation entre phases).
 *
 * @store explorationIA
 */
Alpine.store('explorationIA', {
  // === CONFIGURATION (injectée par le composant orchestrateur via setup()) ===
  projectId: null,
  siteId: null,
  projectContext: '',
  isEditingContext: false,

  // === PHASES ===
  currentPhase: 1,

  // === RECHERCHE (Phase 1) ===
  searchQuery: '',
  isLoading: false,
  error: null,
  answerChunks: [],
  citations: [],
  selectedChunks: [],
  hoveredSources: [],
  foundAnswer: null,

  // === CO-RECOMMANDATIONS (Phase 2) ===
  coRecommendations: [],
  isLoadingCoRecos: false,
  selectedCitationsForStep2: [],
  selectedCoRecoIds: [],

  // === SYNTHÈSE (Phase 3) ===
  allSelectedItems: [],

  // === MODALE RESSOURCE ===
  resourceModal: {
    isOpen: false,
    isLoading: false,
    citation: null,
    resource: null,
    recommendation: null,
    error: null,
  },

  /**
   * Initialise le store avec la configuration fournie par Django.
   * Appelé par le composant orchestrateur dans son init().
   */
  setup(config = {}) {
    this.projectId = config.projectId ?? null;
    this.siteId = config.siteId ?? null;
    this.projectContext = config.projectContext || '';
  },

  // ============================================================
  // PHASE 1 : RECHERCHE
  // ============================================================

  async performSearch() {
    if (!this.searchQuery.trim()) {
      this.error = 'Veuillez saisir des mots-clés';
      return;
    }
    this.isLoading = true;
    this.error = null;

    try {
      const data = await askLLM(this.searchQuery.trim(), this.projectContext, {
        siteId: this.siteId,
      });
      this.answerChunks = data.answer_chunks || [];
      this.citations = data.citations || [];
      this.foundAnswer = data.found_answer || false;
      this.selectedChunks = [];
    } catch (err) {
      this.error = 'Erreur lors de la recherche. Veuillez réessayer.';
      console.error('ExplorationIA search error:', err);
      Alpine.store('app').displayToastMessage({
        message: 'Erreur lors de la recherche',
        type: ToastType.error,
      });
    } finally {
      this.isLoading = false;
    }
  },

  // === Gestion des chunks ===
  toggleChunkSelection(index) {
    const chunk = this.answerChunks[index];
    if (!chunk || !chunk.sources || chunk.sources.length === 0) return;

    const idx = this.selectedChunks.indexOf(index);
    if (idx > -1) {
      this.selectedChunks.splice(idx, 1);
    } else {
      this.selectedChunks.push(index);
    }
  },

  isChunkSelected(index) {
    return this.selectedChunks.includes(index);
  },

  getSelectableChunksCount() {
    return this.answerChunks.filter((c) => c.sources && c.sources.length > 0)
      .length;
  },

  clearChunkSelection() {
    this.selectedChunks = [];
  },

  // === Survol des sources ===
  highlightSources(sources) {
    this.hoveredSources = sources || [];
  },

  clearHighlight() {
    this.hoveredSources = [];
  },

  isSourceHighlighted(label) {
    return this.hoveredSources.includes(label);
  },

  isSourceSelected(label) {
    return this.selectedChunks.some((index) => {
      const chunk = this.answerChunks[index];
      return chunk && chunk.sources && chunk.sources.includes(label);
    });
  },

  // === Getters de présentation pour la phase 1 ===
  get groupedAnswerChunks() {
    const groups = [];
    this.answerChunks.forEach((chunk, index) => {
      const subQuestion = chunk.sub_question || null;
      const lastGroup = groups[groups.length - 1];
      if (lastGroup && lastGroup.subQuestion === subQuestion) {
        lastGroup.chunks.push({ chunk, index });
      } else {
        groups.push({ subQuestion, chunks: [{ chunk, index }] });
      }
    });
    return groups;
  },

  get orderedCitations() {
    const labelOrder = [];
    this.answerChunks.forEach((chunk) => {
      (chunk.sources || []).forEach((label) => {
        if (!labelOrder.includes(label)) labelOrder.push(label);
      });
    });
    return [...this.citations].sort((a, b) => {
      const indexA = labelOrder.indexOf(a.label);
      const indexB = labelOrder.indexOf(b.label);
      return (
        (indexA === -1 ? Infinity : indexA) -
        (indexB === -1 ? Infinity : indexB)
      );
    });
  },

  getCitationByLabel(label) {
    return this.citations.find((c) => c.label === label);
  },

  getCitationUrl(citation) {
    if (!citation) return null;
    if (citation.resource_id) return `/ressource/${citation.resource_id}/`;
    if (citation.reco_id && citation.project_id) {
      return `/project/${citation.project_id}/actions/#action-${citation.reco_id}`;
    }
    return null;
  },

  hasAnswerResults() {
    return this.answerChunks.length > 0 || this.citations.length > 0;
  },

  hasSelectedResources() {
    const hasDirectResources = this.getSelectedResourceIds().length > 0;
    const hasRecommendations =
      this.getSelectedRecommendationCitations().length > 0;
    return hasDirectResources || hasRecommendations;
  },

  // ============================================================
  // PHASE 2 : CO-RECOMMANDATIONS
  // ============================================================

  getSelectedResourceIds() {
    const resourceIds = new Set();
    this.selectedChunks.forEach((index) => {
      const chunk = this.answerChunks[index];
      if (chunk && chunk.sources) {
        chunk.sources.forEach((label) => {
          const citation = this.getCitationByLabel(label);
          if (citation && citation.resource_id) {
            resourceIds.add(citation.resource_id);
          }
        });
      }
    });
    return Array.from(resourceIds);
  },

  getSelectedRecommendationCitations() {
    const recoCitations = [];
    this.selectedChunks.forEach((index) => {
      const chunk = this.answerChunks[index];
      if (chunk && chunk.sources) {
        chunk.sources.forEach((label) => {
          const citation = this.getCitationByLabel(label);
          if (
            citation &&
            citation.source_type === 'recommendation' &&
            !citation.resource_id &&
            citation.reco_id
          ) {
            if (!recoCitations.find((c) => c.reco_id === citation.reco_id)) {
              recoCitations.push(citation);
            }
          }
        });
      }
    });
    return recoCitations;
  },

  getSelectedCitations() {
    const citations = [];
    this.selectedChunks.forEach((index) => {
      const chunk = this.answerChunks[index];
      if (chunk && chunk.sources) {
        chunk.sources.forEach((label) => {
          const citation = this.getCitationByLabel(label);
          if (citation) {
            const existing = citations.find((c) => c.label === citation.label);
            if (existing) {
              if (chunk.text && !existing.chunkTexts.includes(chunk.text)) {
                existing.chunkTexts.push(chunk.text);
              }
            } else {
              citations.push({
                ...citation,
                chunkTexts: chunk.text ? [chunk.text] : [],
              });
            }
          }
        });
      }
    });
    return citations;
  },

  // Appels Django internes (auth session) — gardés dans le store, pas dans llmClient.
  async fetchResourceFromApi(resourceId) {
    try {
      const response = await fetch(`/api/resources/${resourceId}/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
      });
      if (!response.ok) {
        console.warn(
          `Impossible de récupérer la ressource ${resourceId}:`,
          response.status
        );
        return null;
      }
      return await response.json();
    } catch (err) {
      console.error('Erreur lors de la récupération de la ressource:', err);
      return null;
    }
  },

  async fetchRecommendationDetails(projectId, recoId) {
    try {
      const response = await fetch(
        `/api/projects/${projectId}/tasks/${recoId}/`,
        {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'same-origin',
        }
      );
      if (!response.ok) {
        console.warn(
          `Impossible de récupérer la recommandation ${recoId}:`,
          response.status
        );
        return null;
      }
      return await response.json();
    } catch (err) {
      console.error(
        'Erreur lors de la récupération de la recommandation:',
        err
      );
      return null;
    }
  },

  async fetchResourceIdFromRecommendation(projectId, recoId) {
    const task = await this.fetchRecommendationDetails(projectId, recoId);
    if (!task) return null;
    if (task.resource?.id) return task.resource.id;
    if (task.resource_id) return task.resource_id;
    if (task.recommendations && task.recommendations.length > 0) {
      const reco = task.recommendations[0];
      if (reco.resource?.id) return reco.resource.id;
    }
    return null;
  },

  async fetchCoRecommendations() {
    let resourceIds = this.getSelectedResourceIds();
    const recoCitations = this.getSelectedRecommendationCitations();

    if (recoCitations.length > 0) {
      const resourceIdPromises = recoCitations.map(async (citation) => {
        if (citation.project_id && citation.reco_id) {
          const resourceId = await this.fetchResourceIdFromRecommendation(
            citation.project_id,
            citation.reco_id
          );
          if (resourceId) {
            citation.resource_id = resourceId;
          }
          return resourceId;
        }
        return null;
      });
      const additional = await Promise.all(resourceIdPromises);
      const valid = additional.filter((id) => id !== null);
      resourceIds = [...new Set([...resourceIds, ...valid])];
    }

    if (resourceIds.length === 0) {
      Alpine.store('app').displayToastMessage({
        message: 'Aucune ressource trouvée dans les éléments sélectionnés',
        type: ToastType.warning,
      });
      return;
    }

    this.selectedCitationsForStep2 = this.getSelectedCitations();
    this.isLoadingCoRecos = true;
    this.error = null;

    try {
      const items = await fetchCoRecommendations(resourceIds, {
        siteId: this.siteId,
      });

      if (items.length > 0) {
        const resourcePromises = items.map(async (item) => {
          const resourceId = item.resource_id || item;
          const score = item.co_occurrence_score || null;
          const resource = await this.fetchResourceFromApi(resourceId);
          return resource ? { resource, score } : null;
        });
        const results = await Promise.all(resourcePromises);
        this.coRecommendations = results
          .filter((r) => r !== null)
          .map(({ resource, score }) => ({
            id: resource.id,
            title: resource.title || 'Sans titre',
            content:
              resource.summary || resource.content || resource.text || '',
            url: resource.url || null,
            category: resource.category?.name || null,
            tags: resource.tags || [],
            resourceId: resource.id,
            coOccurrenceScore: score,
          }));
      } else {
        this.coRecommendations = [];
      }

      if (this.currentPhase === 1) {
        this.recordSelectedItems();
        this.currentPhase = 2;
        this.answerChunks = [];
        this.citations = [];
        this.selectedChunks = [];
      }

      Alpine.store('app').displayToastMessage({
        message: `${this.coRecommendations.length} ressource(s) co-recommandée(s) trouvée(s)`,
        type: ToastType.success,
      });
    } catch (err) {
      this.error = 'Erreur lors de la récupération des co-recommandations.';
      console.error('ExplorationIA co-recommendations error:', err);
      Alpine.store('app').displayToastMessage({
        message: 'Erreur lors de la récupération des co-recommandations',
        type: ToastType.error,
      });
    } finally {
      this.isLoadingCoRecos = false;
    }
  },

  toggleCoRecoSelection(resourceId) {
    const idx = this.selectedCoRecoIds.indexOf(resourceId);
    if (idx > -1) {
      this.selectedCoRecoIds.splice(idx, 1);
    } else {
      this.selectedCoRecoIds.push(resourceId);
    }
  },

  isCoRecoSelected(resourceId) {
    return this.selectedCoRecoIds.includes(resourceId);
  },

  clearCoRecoSelection() {
    this.selectedCoRecoIds = [];
  },

  selectAllCoRecos() {
    this.selectedCoRecoIds = this.coRecommendations.map((r) => r.id);
  },

  getSelectedCoRecommendations() {
    return this.coRecommendations.filter((r) =>
      this.selectedCoRecoIds.includes(r.id)
    );
  },

  // ============================================================
  // PHASE 3 : SYNTHÈSE
  // ============================================================

  /**
   * Combine toutes les ressources sélectionnées (étapes 1 et 2) pour la synthèse.
   */
  getAllSelectedResources() {
    const all = [];
    this.selectedCitationsForStep2.forEach((citation) => {
      all.push({
        id: citation.label,
        title: citation.title,
        content: citation.content,
        source_type: citation.source_type,
        resource_id: citation.resource_id,
        reco_id: citation.reco_id,
        project_id: citation.project_id,
        label: citation.label,
        chunkTexts: citation.chunkTexts || [],
        fromStep: 1,
      });
    });
    this.getSelectedCoRecommendations().forEach((resource) => {
      all.push({
        id: resource.id,
        title: resource.title,
        content: resource.content,
        source_type: 'resource',
        resource_id: resource.resourceId || resource.id,
        category: resource.category,
        tags: resource.tags,
        coOccurrenceScore: resource.coOccurrenceScore,
        fromStep: 2,
      });
    });
    return all;
  },

  // ============================================================
  // NAVIGATION ENTRE PHASES
  // ============================================================

  canProceedToNextPhase() {
    if (this.currentPhase === 1) {
      return this.selectedChunks.length > 0;
    }
    if (this.currentPhase === 2) {
      return (
        this.selectedCitationsForStep2.length > 0 ||
        this.selectedCoRecoIds.length > 0
      );
    }
    return false;
  },

  proceedToNextPhase() {
    if (!this.canProceedToNextPhase()) return;
    this.recordSelectedItems();

    if (this.currentPhase < 3) {
      this.currentPhase++;
    }
  },

  /**
   * Capture les sélections de chunks de la phase courante dans `allSelectedItems`,
   * en évitant les doublons sur `label`. Appelée avant de quitter une phase qui
   * peut comporter des sélections de chunks (transitions 1 → 2 et 2 → 3).
   */
  recordSelectedItems() {
    const existingLabels = new Set(this.allSelectedItems.map((item) => item.id));
    this.selectedChunks.forEach((index) => {
      const chunk = this.answerChunks[index];
      if (!chunk || !chunk.sources) return;
      chunk.sources.forEach((label) => {
        if (existingLabels.has(label)) return;
        const citation = this.getCitationByLabel(label);
        if (!citation) return;
        existingLabels.add(label);
        this.allSelectedItems.push({
          id: citation.label,
          title: citation.title,
          content: citation.content,
          type: citation.source_type,
          resourceId: citation.resource_id,
          recoId: citation.reco_id,
          projectId: citation.project_id,
        });
      });
    });
  },

  /**
   * Réinitialise toute l'exploration (utilisé par le bouton "Nouvelle exploration"
   * et "Recommencer"). Conserve la configuration (projectId, siteId, projectContext).
   */
  resetExploration() {
    this.currentPhase = 1;
    this.searchQuery = '';
    this.allSelectedItems = [];
    this.answerChunks = [];
    this.citations = [];
    this.foundAnswer = null;
    this.selectedChunks = [];
    this.hoveredSources = [];
    this.coRecommendations = [];
    this.isLoadingCoRecos = false;
    this.selectedCitationsForStep2 = [];
    this.selectedCoRecoIds = [];
    this.resourceModal = {
      isOpen: false,
      isLoading: false,
      citation: null,
      resource: null,
      recommendation: null,
      error: null,
    };
    this.error = null;
  },

  // === Contexte du projet ===
  toggleEditContext() {
    this.isEditingContext = !this.isEditingContext;
  },

  // ============================================================
  // MODALE RESSOURCE
  // ============================================================

  async openResourceModal(citation) {
    if (!citation) return;
    this.resourceModal = {
      isOpen: true,
      isLoading: true,
      citation,
      resource: null,
      recommendation: null,
      error: null,
    };

    try {
      let resourceId = citation.resource_id;

      if (!resourceId && citation.reco_id && citation.project_id) {
        const recommendation = await this.fetchRecommendationDetails(
          citation.project_id,
          citation.reco_id
        );
        if (recommendation) {
          this.resourceModal.recommendation = recommendation;
          if (recommendation.resource?.id) {
            resourceId = recommendation.resource.id;
          } else if (recommendation.resource_id) {
            resourceId = recommendation.resource_id;
          }
          if (resourceId) citation.resource_id = resourceId;
        }
      }

      if (resourceId) {
        const resource = await this.fetchResourceFromApi(resourceId);
        if (resource) this.resourceModal.resource = resource;
      }

      if (!this.resourceModal.resource && !this.resourceModal.recommendation) {
        this.resourceModal.error = 'Impossible de charger les détails.';
      }
    } catch (err) {
      console.error('Erreur lors du chargement:', err);
      this.resourceModal.error = 'Erreur lors du chargement.';
    } finally {
      this.resourceModal.isLoading = false;
    }
  },

  closeResourceModal() {
    this.resourceModal = {
      isOpen: false,
      isLoading: false,
      citation: null,
      resource: null,
      recommendation: null,
      error: null,
    };
  },

  hasModalContent() {
    return this.resourceModal.resource || this.resourceModal.recommendation;
  },

  // ============================================================
  // UTILITAIRES PARTAGÉS
  // ============================================================

  parseMarkdown(text) {
    if (!text) return '';
    let html = marked.parse(text, { breaks: true });
    const listStartMatch = text.match(/^(\d+)\.\s/);
    if (listStartMatch) {
      const startNum = parseInt(listStartMatch[1], 10);
      if (startNum > 1) {
        html = html.replace(/^<ol>/, `<ol start="${startNum}">`);
      }
    }
    return DOMPurify.sanitize(html, { ADD_ATTR: ['start'] });
  },

  truncate(text, maxLength = 100) {
    if (!text) return '';
    return text.length > maxLength
      ? text.substring(0, maxLength) + '...'
      : text;
  },

  getPhaseTitle(phase) {
    const titles = {
      1: 'Recherche initiale',
      2: 'Exploration itérative',
      3: 'Synthèse des résultats',
    };
    return titles[phase] || '';
  },

  getPhaseDescription(phase) {
    const descriptions = {
      1: 'Sélectionnez les passages qui vous semblent pertinents avant de continuer',
      2: 'Continuez à explorer ou lancez la synthèse',
      3: 'Analyse des résultats sélectionnés',
    };
    return descriptions[phase] || '';
  },

  getSourceTypeLabel(sourceType) {
    const labels = {
      resource: 'Ressource',
      recommendation: 'Recommandation',
      project: 'Projet',
      document: 'Document',
    };
    return labels[sourceType] || sourceType;
  },
});

export default Alpine.store('explorationIA');
