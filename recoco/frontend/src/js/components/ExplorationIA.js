import Alpine from 'alpinejs';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { ToastType } from '../models/toastType';

// const ML_API_BASE_URL = 'https://ml.recoconseil.fr';
const ML_API_BASE_URL = 'http://localhost:9080';

Alpine.data('ExplorationIA', (config = {}) => ({
  // === CONFIGURATION ===
  projectId: config.projectId || null,
  apiToken: config.apiToken || 'blahblah',

  // === CONTEXTE DU PROJET ===
  projectContext: config.projectContext || '',
  isEditingContext: false,

  // === ETAT DES PHASES ===
  currentPhase: 1, // 1 = Recherche initiale, 2 = Exploration iterative, 3 = Synthese
  phaseHistory: [], // Historique des phases completees

  // === ETAT DE RECHERCHE ===
  searchQuery: '',
  isLoading: false,
  error: null,

  // === RESULTATS ===
  results: [], // Resultats de la recherche courante (ancien format)
  selectedResults: [], // IDs des resultats selectionnes dans la phase courante

  // === REPONSE IA (nouveau format) ===
  answerChunks: [], // Textes de reponse avec sources
  citations: [], // Sources/bibliographie
  foundAnswer: null, // Si une reponse a ete trouvee
  selectedChunks: [], // Indices des chunks selectionnes
  hoveredSources: [], // Labels des sources survolees

  // === ACCUMULATION POUR SYNTHESE ===
  allSelectedItems: [], // Tous les items selectionnes au fil des phases

  // === SYNTHESE (Phase 3) ===
  synthesis: {
    resources: [],
    projects: [],
    recommendations: [],
  },
  isSynthesizing: false,

  // === LIFECYCLE ===
  init() {
    // Initialisation du composant
  },

  // === MODE TEST ===
  loadMockData() {
    this.answerChunks = [
      {
        text: "Voici les informations trouvées concernant les aides pour mettre en place un jardin partagé.",
        sources: []
      },
      {
        text: "Le plan de relance a prévu un budget de **17 millions d'euros en 2021** pour financer les jardins partagés et collectifs via des appels à projets départementaux gérés par les DDT (Directions Départementales des Territoires).",
        sources: ["1.1"]
      },
      {
        text: "Les taux de subvention varient selon le bénéficiaire :\n- **Associations** : jusqu'à **80%** du coût global du projet\n- **Collectivités territoriales et leurs groupements** : jusqu'à **50%**\n- **Bailleurs sociaux (publics ou privés)** : jusqu'à **50%**",
        sources: ["1.1"]
      },
      {
        text: "Les dépenses éligibles incluent les investissements **matériels et immatériels**, comme les prestations d'ingénierie ou les études de sols.",
        sources: ["1.1"]
      },
      {
        text: "Vous pouvez aussi consulter les aides régionales et européennes en cliquant sur ce lien : [Aides et appels à projets de la région Île-de-France](https://www.iledefrance.fr/aides-et-appels-a-projets).",
        sources: ["2.1"]
      },
      {
        text: "Un guide méthodologique sur l'accès collectif au foncier (mis à jour en 2007) évoque des montages juridiques et financiers, comme l'association des amis d'une SCI, pour faciliter l'obtention de subventions.",
        sources: ["3.1"]
      }
    ];

    this.citations = [
      {
        label: "1.1",
        title: "Financer la création de jardins partagés et collectifs",
        content: "Pour encourager le développement de l'agriculture urbaine, le plan de relance a prévu d'engager un budget global de 17 millions d'euros en 2021...",
        resource_id: 120,
        reco_id: null,
        project_id: null,
        source_type: "Resource"
      },
      {
        label: "2.1",
        title: "Bénéficier des aides régionales et européennes",
        content: "Vous pouvez également retrouver l'ensemble des aides de la région...",
        resource_id: null,
        reco_id: 5623,
        project_id: 2557,
        source_type: "Recommendation"
      },
      {
        label: "3.1",
        title: "Quelques éléments sur l'articulation SCI - association",
        content: "Par ailleurs, il existe un guide méthodologique sur l'accès collectif et solidaire au foncier et au bâti...",
        resource_id: null,
        reco_id: 4521,
        project_id: 778,
        source_type: "Recommendation"
      }
    ];

    this.foundAnswer = true;
    this.searchQuery = "Quelles aides puis-je avoir pour mettre en place un jardin partagé ?";
  },

  // === RECHERCHE API ML ===
  async performSearch() {
    if (!this.searchQuery.trim()) {
      this.error = 'Veuillez saisir des mots-cles';
      return;
    }
    this.isLoading = true;
    this.error = null;
    this.results = [];

    try {
      const headers = {
        'Content-Type': 'application/json',
      };

      if (this.apiToken) {
        headers['Authorization'] = `Bearer ${this.apiToken}`;
      }

      const response = await fetch(`${ML_API_BASE_URL}/ask`, {
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
      console.log('ExplorationIA API response:', data);

      // Nouveau format avec answer_chunks et citations
      if (data.answer_chunks && data.citations) {
        this.answerChunks = data.answer_chunks || [];
        this.citations = data.citations || [];
        this.foundAnswer = data.found_answer || false;
        this.selectedChunks = [];
      } else {
        // Ancien format (fallback)
        this.results = this.mapResults(data);
      }
      console.log('ExplorationIA mapped results:', this.answerChunks, this.citations);
    } catch (err) {
      this.error = 'Erreur lors de la recherche. Veuillez reessayer.';
      console.error('ExplorationIA search error:', err);
      this.$store.app.displayToastMessage({
        message: 'Erreur lors de la recherche',
        type: ToastType.error,
      });
    } finally {
      this.isLoading = false;
    }
  },

  mapResults(apiResponse) {
    // L'API renvoie un tableau de [document, score]
    // Adapter la reponse API au format interne
    return (apiResponse || []).map((item) => {
      // Chaque item est un tableau [document, score]
      const doc = Array.isArray(item) ? item[0] : item;
      const score = Array.isArray(item) ? item[1] : item.score || 0;

      return {
        id: doc.id,
        title: doc.metadata?.title || 'Sans titre',
        resourceId: doc.metadata?.resource_id,
        startIndex: doc.metadata?.start_index,
        content: doc.page_content || '',
        type: doc.type || 'resource',
        score: score,
        isSelected: false,
      };
    });
  },

  // === SELECTION ===
  toggleSelection(resultId) {
    const result = this.results.find((r) => r.id === resultId);
    if (!result) return;

    result.isSelected = !result.isSelected;

    if (result.isSelected) {
      this.selectedResults.push(resultId);
    } else {
      this.selectedResults = this.selectedResults.filter(
        (id) => id !== resultId
      );
    }

    this.$dispatch('exploration-selection-change', {
      selected: this.selectedResults,
      phase: this.currentPhase,
    });
  },

  isSelected(resultId) {
    return this.selectedResults.includes(resultId);
  },

  get selectedCount() {
    return this.selectedResults.length;
  },

  get hasSelection() {
    return this.selectedResults.length > 0;
  },

  // === NAVIGATION ENTRE PHASES ===
  canProceedToNextPhase() {
    if (this.currentPhase === 1) {
      return this.hasSelection;
    }
    if (this.currentPhase === 2) {
      return this.allSelectedItems.length >= 1 || this.hasSelection;
    }
    return false;
  },

  async proceedToNextPhase() {
    if (!this.canProceedToNextPhase()) return;

    // Sauvegarder les selections courantes
    this.saveCurrentPhaseSelections();

    if (this.currentPhase < 3) {
      this.currentPhase++;

      if (this.currentPhase === 2) {
        // Phase 2 : Continuer l'exploration
        this.preparePhase2();
      } else if (this.currentPhase === 3) {
        // Phase 3 : Lancer la synthese
        await this.performSynthesis();
      }
    }
  },

  saveCurrentPhaseSelections() {
    const selectedItems = this.results.filter((r) => r.isSelected);
    if (selectedItems.length > 0) {
      this.phaseHistory.push({
        phase: this.currentPhase,
        query: this.searchQuery,
        selectedItems: [...selectedItems],
      });
      this.allSelectedItems = [...this.allSelectedItems, ...selectedItems];
    }
  },

  preparePhase2() {
    // Reinitialiser pour la nouvelle exploration
    this.searchQuery = '';
    this.results = [];
    this.selectedResults = [];
  },

  continueExploration() {
    // Permet de continuer a explorer avec une nouvelle recherche
    this.searchQuery = '';
    this.results = [];
    this.selectedResults = [];
  },

  // === RECHERCHE BASEE SUR SELECTION ===
  async searchBasedOnSelection() {
    if (!this.hasSelection) return;

    // Construire une requete basee sur les titres selectionnes
    const selectedItems = this.results.filter((r) => r.isSelected);
    const keywords = selectedItems
      .map((item) => item.title)
      .join(' ')
      .split(/\s+/)
      .filter((word) => word.length > 3)
      .slice(0, 5)
      .join(' ');

    this.searchQuery = keywords;
    await this.performSearch();
  },

  // === PHASE 3 : SYNTHESE ===
  async performSynthesis() {
    this.isSynthesizing = true;
    this.error = null;

    try {
      // Regrouper les items selectionnes par type
      const grouped = this.groupByType(this.allSelectedItems);

      this.synthesis = {
        resources: grouped.resource || grouped.Document || [],
        projects: grouped.project || [],
        recommendations: grouped.recommendation || [],
      };

      // Si tous les types sont vides, mettre tout dans resources
      if (
        this.synthesis.resources.length === 0 &&
        this.synthesis.projects.length === 0 &&
        this.synthesis.recommendations.length === 0
      ) {
        this.synthesis.resources = [...this.allSelectedItems];
      }
    } catch (err) {
      this.error = 'Erreur lors de la synthese';
      console.error('ExplorationIA synthesis error:', err);
    } finally {
      this.isSynthesizing = false;
    }
  },

  groupByType(items) {
    return items.reduce((acc, item) => {
      const type = item.type || 'resource';
      if (!acc[type]) {
        acc[type] = [];
      }
      acc[type].push(item);
      return acc;
    }, {});
  },

  // === ACTIONS FINALES ===
  viewResource(item) {
    if (item.resourceId) {
      window.open(`/ressource/${item.resourceId}/`, '_blank');
    }
  },

  // === RESET ===
  resetExploration() {
    this.currentPhase = 1;
    this.phaseHistory = [];
    this.searchQuery = '';
    this.results = [];
    this.selectedResults = [];
    this.allSelectedItems = [];
    this.answerChunks = [];
    this.citations = [];
    this.foundAnswer = false;
    this.selectedChunks = [];
    this.hoveredSources = [];
    this.synthesis = {
      resources: [],
      projects: [],
      recommendations: [],
    };
    this.error = null;
  },

  // === CONTEXTE DU PROJET ===
  toggleEditContext() {
    this.isEditingContext = !this.isEditingContext;
  },

  saveContext() {
    this.isEditingContext = false;
  },

  // === GESTION DES CHUNKS ===
  toggleChunkSelection(index) {
    const chunk = this.answerChunks[index];
    // Ne permettre la selection que des chunks avec sources
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

  getSelectedChunksData() {
    return this.selectedChunks.map((index) => {
      const chunk = this.answerChunks[index];
      const sourceCitations = (chunk.sources || []).map((label) =>
        this.getCitationByLabel(label)
      ).filter(Boolean);
      return {
        text: chunk.text,
        sources: chunk.sources,
        citations: sourceCitations,
      };
    });
  },

  async searchRelatedRecommendations() {
    if (this.selectedChunks.length === 0) return;

    const selectedData = this.getSelectedChunksData();

    // Construire le contexte a partir des chunks selectionnes
    const selectedTexts = selectedData.map((d) => d.text).join('\n\n');
    const citationTitles = selectedData
      .flatMap((d) => d.citations.map((c) => c.title))
      .filter((v, i, a) => a.indexOf(v) === i) // unique
      .join(', ');

    // Mettre a jour la requete avec le contexte des selections
    this.searchQuery = `Recommandations liées à : ${citationTitles}`;

    // Ajouter le contexte des selections au contexte du projet
    const enhancedContext = `${this.projectContext}\n\nPassages sélectionnés :\n${selectedTexts}`;

    this.isLoading = true;
    this.error = null;

    try {
      const headers = {
        'Content-Type': 'application/json',
      };

      if (this.apiToken) {
        headers['Authorization'] = `Bearer ${this.apiToken}`;
      }

      const response = await fetch(`${ML_API_BASE_URL}/ask`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          query: this.searchQuery,
          context: enhancedContext,
        }),
      });

      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`);
      }

      const data = await response.json();
      console.log('ExplorationIA related search response:', data);

      if (data.answer_chunks && data.citations) {
        this.answerChunks = data.answer_chunks || [];
        this.citations = data.citations || [];
        this.foundAnswer = data.found_answer || false;
        this.selectedChunks = [];
      }
    } catch (err) {
      this.error = 'Erreur lors de la recherche. Veuillez reessayer.';
      console.error('ExplorationIA related search error:', err);
    } finally {
      this.isLoading = false;
    }
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
    // Verifie si la source est liee a un chunk selectionne
    return this.selectedChunks.some((index) => {
      const chunk = this.answerChunks[index];
      return chunk && chunk.sources && chunk.sources.includes(label);
    });
  },

  getCitationUrl(citation) {
    if (citation.resource_id) {
      return `/ressource/${citation.resource_id}/`;
    }
    if (citation.reco_id && citation.project_id) {
      return `/project/${citation.project_id}/actions/#action-${citation.reco_id}`;
    }
    return null;
  },

  getSourceTypeLabel(sourceType) {
    const labels = {
      Resource: 'Ressource',
      Recommendation: 'Recommandation',
      Project: 'Projet',
    };
    return labels[sourceType] || sourceType;
  },

  hasAnswerResults() {
    return this.answerChunks.length > 0 || this.citations.length > 0;
  },

  parseMarkdown(text) {
    if (!text) return '';
    const html = marked.parse(text, { breaks: true });
    return DOMPurify.sanitize(html);
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
      2: 'Exploration iterative',
      3: 'Synthese des resultats',
    };
    return titles[phase] || '';
  },

  getPhaseDescription(phase) {
    const descriptions = {
      1: 'Formulez votre besoin sur ce projet et découvrez des ressources pertinentes',
      2: 'Continuez à explorer ou lancez la synthèse',
      3: 'Analyse des résultats sélectionnés',
    };
    return descriptions[phase] || '';
  },

  formatScore(score) {
    if (!score) return '';
    // Le score semble etre une distance, plus bas = plus pertinent
    // On inverse pour l'affichage (plus haut = plus pertinent)
    const normalized = Math.max(0, Math.min(100, 100 - score * 50));
    return Math.round(normalized);
  },
}));
