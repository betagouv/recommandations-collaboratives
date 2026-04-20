import Alpine from 'alpinejs';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { ToastType } from '../models/toastType';

const ML_API_BASE_URL = import.meta.env.VITE_ML_API_BASE_URL;

Alpine.data('ExplorationIA', (config = {}) => ({
  // === CONFIGURATION ===
  apiToken: config.apiToken || 'blahblah',
  siteId: config.siteId || null,

  // === CONTEXTE DU PROJET ===
  projectContext: config.projectContext || '',
  isEditingContext: false,

  // === ETAT DES PHASES ===
  currentPhase: 1, // 1 = Recherche initiale, 2 = Exploration iterative, 3 = Synthese

  // === ETAT DE RECHERCHE ===
  searchQuery: '',
  isLoading: false,
  error: null,

  // === REPONSE IA ===
  answerChunks: [],
  citations: [],
  foundAnswer: null,
  selectedChunks: [],
  hoveredSources: [],

  // === CO-RECOMMANDATIONS (Etape 2) ===
  coRecommendations: [],
  isLoadingCoRecos: false,
  selectedCitationsForStep2: [],
  selectedCoRecoIds: [],

  // === MODALE RESSOURCE ===
  resourceModal: {
    isOpen: false,
    isLoading: false,
    citation: null,
    resource: null,
    recommendation: null,
    error: null,
  },

  // === LIFECYCLE ===
  init() {
    this.$watch('currentPhase', () => {
      this.scrollToTop();
    });
  },

  scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  },

  // === RECHERCHE API ML ===
  async performSearch() {
    if (!this.searchQuery.trim()) {
      this.error = 'Veuillez saisir des mots-clés';
      return;
    }
    this.isLoading = true;
    this.error = null;

    try {
      const headers = {
        'Content-Type': 'application/json',
      };

      if (this.apiToken) {
        headers['Authorization'] = `Bearer ${this.apiToken}`;
      }

      const askParams = new URLSearchParams();
      if (this.siteId) {
        askParams.append('site_id', this.siteId);
      }
      const askUrl = `${ML_API_BASE_URL}/ask${askParams.toString() ? '?' + askParams.toString() : ''}`;

      const response = await fetch(askUrl, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          query: this.searchQuery.trim(),
          context: this.projectContext || '',
        }),
      });

      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`);
      }

      const data = await response.json();

      this.answerChunks = data.answer_chunks || [];
      this.citations = data.citations || [];
      this.foundAnswer = data.found_answer || false;
      this.selectedChunks = [];
    } catch (err) {
      this.error = 'Erreur lors de la recherche. Veuillez réessayer.';
      console.error('ExplorationIA search error:', err);
      this.$store.app.displayToastMessage({
        message: 'Erreur lors de la recherche',
        type: ToastType.error,
      });
    } finally {
      this.isLoading = false;
    }
  },

  // === NAVIGATION ENTRE PHASES ===
  canProceedToNextPhase() {
    // Phase 2 : au moins une citation étape 1 ou une co-reco étape 2
    return (
      this.selectedCitationsForStep2.length > 0 ||
      this.selectedCoRecoIds.length > 0
    );
  },

  proceedToNextPhase() {
    if (!this.canProceedToNextPhase()) return;
    if (this.currentPhase === 2) {
      this.currentPhase = 3;
    }
  },

  // === RESET ===
  resetExploration() {
    this.currentPhase = 1;
    this.searchQuery = '';
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

  // === CONTEXTE DU PROJET ===
  toggleEditContext() {
    this.isEditingContext = !this.isEditingContext;
  },

  // === GESTION DES CHUNKS ===
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
    return this.answerChunks.filter(
      (chunk) => chunk.sources && chunk.sources.length > 0
    ).length;
  },

  clearChunkSelection() {
    this.selectedChunks = [];
  },

  // === CO-RECOMMANDATIONS ===
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

  async fetchResourceIdFromRecommendation(projectId, recoId) {
    try {
      const response = await fetch(
        `/api/projects/${projectId}/tasks/${recoId}/`,
        {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'same-origin',
        }
      );

      if (!response.ok) return null;

      const task = await response.json();

      if (task.resource?.id) return task.resource.id;
      if (task.resource_id) return task.resource_id;
      if (task.recommendations && task.recommendations.length > 0) {
        const reco = task.recommendations[0];
        if (reco.resource?.id) return reco.resource.id;
      }
      return null;
    } catch (err) {
      console.error('Erreur lors de la récupération de la task:', err);
      return null;
    }
  },

  async fetchResourceFromApi(resourceId) {
    try {
      const response = await fetch(`/api/resources/${resourceId}/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
      });

      if (!response.ok) return null;
      return await response.json();
    } catch (err) {
      console.error('Erreur lors de la récupération de la ressource:', err);
      return null;
    }
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

      const additionalResourceIds = await Promise.all(resourceIdPromises);
      const validIds = additionalResourceIds.filter((id) => id !== null);
      resourceIds = [...new Set([...resourceIds, ...validIds])];
    }

    if (resourceIds.length === 0) {
      this.$store.app.displayToastMessage({
        message: 'Aucune ressource trouvée dans les éléments sélectionnés',
        type: ToastType.warning,
      });
      return;
    }

    this.selectedCitationsForStep2 = this.getSelectedCitations();

    this.isLoadingCoRecos = true;
    this.error = null;

    try {
      const headers = { 'Content-Type': 'application/json' };

      if (this.apiToken) {
        headers['Authorization'] = `Bearer ${this.apiToken}`;
      }

      const params = new URLSearchParams();
      resourceIds.forEach((id) => params.append('resource_ids', id));
      if (this.siteId) {
        params.append('site_id', this.siteId);
      }
      const url = `${ML_API_BASE_URL}/co-recommendations?${params.toString()}`;

      const response = await fetch(url, { method: 'GET', headers });

      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`);
      }

      const data = await response.json();
      const coRecoItems = data.co_recommendations || data || [];

      if (coRecoItems.length > 0) {
        const resourcePromises = coRecoItems.map(async (item) => {
          const resourceId = item.resource_id || item;
          const score = item.co_occurrence_score || null;
          const resource = await this.fetchResourceFromApi(resourceId);
          if (resource) {
            return { resource, score };
          }
          return null;
        });

        const results = await Promise.all(resourcePromises);
        this.coRecommendations = results
          .filter((result) => result !== null)
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
        this.currentPhase = 2;
        this.answerChunks = [];
        this.citations = [];
        this.selectedChunks = [];
      }

      this.$store.app.displayToastMessage({
        message: `${this.coRecommendations.length} ressource(s) co-recommandée(s) trouvée(s)`,
        type: ToastType.success,
      });
    } catch (err) {
      this.error = 'Erreur lors de la récupération des co-recommandations.';
      console.error('ExplorationIA co-recommendations error:', err);
      this.$store.app.displayToastMessage({
        message: 'Erreur lors de la récupération des co-recommandations',
        type: ToastType.error,
      });
    } finally {
      this.isLoadingCoRecos = false;
    }
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

  hasSelectedResources() {
    return (
      this.getSelectedResourceIds().length > 0 ||
      this.getSelectedRecommendationCitations().length > 0
    );
  },

  // === SÉLECTION DES CO-RECOMMANDATIONS (Étape 2) ===
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

  getAllSelectedResources() {
    const allResources = [];

    this.selectedCitationsForStep2.forEach((citation) => {
      allResources.push({
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
      allResources.push({
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

    return allResources;
  },

  get orderedCitations() {
    const labelOrder = [];
    this.answerChunks.forEach((chunk) => {
      (chunk.sources || []).forEach((label) => {
        if (!labelOrder.includes(label)) {
          labelOrder.push(label);
        }
      });
    });

    return [...this.citations].sort((a, b) => {
      const indexA = labelOrder.indexOf(a.label);
      const indexB = labelOrder.indexOf(b.label);
      const orderA = indexA === -1 ? Infinity : indexA;
      const orderB = indexB === -1 ? Infinity : indexB;
      return orderA - orderB;
    });
  },

  getCitationByLabel(label) {
    return this.citations.find((c) => c.label === label);
  },

  // === SURVOL DES SOURCES ===
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

  getCitationUrl(citation) {
    if (!citation) return null;
    if (citation.resource_id) {
      return `/ressource/${citation.resource_id}/`;
    }
    if (citation.reco_id && citation.project_id) {
      return `/project/${citation.project_id}/actions/#action-${citation.reco_id}`;
    }
    return null;
  },

  // === MODALE RESSOURCE ===
  async openResourceModal(citation) {
    if (!citation) return;

    this.resourceModal = {
      isOpen: true,
      isLoading: true,
      citation: citation,
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

          if (resourceId) {
            citation.resource_id = resourceId;
          }
        }
      }

      if (resourceId) {
        const resource = await this.fetchResourceFromApi(resourceId);
        if (resource) {
          this.resourceModal.resource = resource;
        }
      }

      if (!this.resourceModal.resource && !this.resourceModal.recommendation) {
        this.resourceModal.error = 'Impossible de charger les détails.';
      }
    } catch (err) {
      console.error('Erreur lors du chargement:', err);
      this.resourceModal.error = 'Erreur lors du chargement.';
    } finally {
      this.resourceModal.isLoading = false;
      this.$nextTick(() => {
        this.scrollToHighlight();
      });
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

      if (!response.ok) return null;
      return await response.json();
    } catch (err) {
      console.error('Erreur lors de la récupération de la recommandation:', err);
      return null;
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

  scrollToHighlight() {
    const modalBody = document.querySelector('.exploration-ia-modal__body');
    const highlight = modalBody?.querySelector('.exploration-ia-highlight');
    if (highlight && modalBody) {
      setTimeout(() => {
        highlight.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 100);
    }
  },

  highlightCitationInHtml(html, citationMarkdown) {
    if (!html || !citationMarkdown) return html;

    const cleanCitation = citationMarkdown
      .trim()
      .replace(/^["']|["']$/g, '')
      .trim();
    if (cleanCitation.length < 10) return html;

    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = marked.parse(cleanCitation, { breaks: true });
    const plainText = (tempDiv.textContent || '').trim();
    if (plainText.length < 10) return html;

    const escaped = plainText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    // Tolère espaces ou balises HTML entre les mots du texte original
    const pattern = escaped.replace(/\s+/g, '(?:\\s|<[^>]*>)+');

    try {
      const regex = new RegExp(`(${pattern})`, 'gis');
      return html.replace(regex, '<mark class="exploration-ia-highlight">$1</mark>');
    } catch (e) {
      return html;
    }
  },

  getResourceContentWithHighlight() {
    if (!this.resourceModal.resource || !this.resourceModal.citation) {
      return '';
    }

    const resource = this.resourceModal.resource;
    const citationContent = this.resourceModal.citation.content;
    const fullContent =
      resource.content || resource.text || resource.summary || '';

    const htmlContent = this.parseMarkdown(fullContent);
    return this.highlightCitationInHtml(htmlContent, citationContent);
  },

  getRecommendationContentWithHighlight() {
    if (!this.resourceModal.recommendation || !this.resourceModal.citation) {
      return '';
    }

    const recommendation = this.resourceModal.recommendation;
    const citationContent = this.resourceModal.citation.content;
    const fullContent =
      recommendation.content ||
      recommendation.comment ||
      recommendation.intent ||
      '';

    const htmlContent = this.parseMarkdown(fullContent);
    return this.highlightCitationInHtml(htmlContent, citationContent);
  },

  hasModalContent() {
    return this.resourceModal.resource || this.resourceModal.recommendation;
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

  hasAnswerResults() {
    return this.answerChunks.length > 0 || this.citations.length > 0;
  },

  parseMarkdown(text) {
    if (!text) return '';
    let html = marked.parse(text, { breaks: true });

    // Préserver la numérotation quand le texte démarre à N > 1
    const listStartMatch = text.match(/^(\d+)\.\s/);
    if (listStartMatch) {
      const startNum = parseInt(listStartMatch[1], 10);
      if (startNum > 1) {
        html = html.replace(/^<ol>/, `<ol start="${startNum}">`);
      }
    }

    return DOMPurify.sanitize(html, { ADD_ATTR: ['start'] });
  },

  // === UTILITAIRES ===
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
}));
