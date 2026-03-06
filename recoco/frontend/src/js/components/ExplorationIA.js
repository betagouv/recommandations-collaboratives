import Alpine from 'alpinejs';
import { ToastType } from '../models/toastType';

const ML_API_BASE_URL = 'https://ml.recoconseil.fr';

Alpine.data('ExplorationIA', (config = {}) => ({
  // === CONFIGURATION ===
  projectId: config.projectId || null,
  apiToken: config.apiToken || '',

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
  results: [], // Resultats de la recherche courante
  selectedResults: [], // IDs des resultats selectionnes dans la phase courante

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
      this.results = this.mapResults(data);
      console.log('ExplorationIA mapped results:', this.results);
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
      1: 'Saisissez des mots-cles pour decouvrir des ressources pertinentes',
      2: 'Continuez a explorer ou lancez la synthese',
      3: 'Analyse des resultats selectionnes',
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
