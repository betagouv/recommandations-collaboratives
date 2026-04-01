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

  // === CO-RECOMMANDATIONS (Etape 2) ===
  coRecommendations: [], // Co-recommandations liées aux ressources sélectionnées
  isLoadingCoRecos: false, // Chargement des co-recommandations
  selectedCitationsForStep2: [], // Citations sélectionnées à l'étape 1, affichées à l'étape 2
  selectedCoRecoIds: [], // IDs des co-recommandations sélectionnées à l'étape 2

  // === SYNTHESE (Phase 3) ===
  synthesis: {
    resources: [],
    projects: [],
    recommendations: [],
  },
  isSynthesizing: false,

  // === MODALE RESSOURCE ===
  resourceModal: {
    isOpen: false,
    isLoading: false,
    citation: null, // La citation qui a déclenché l'ouverture
    resource: null, // Les détails complets de la ressource
    recommendation: null, // Les détails de la recommandation (si pas de ressource)
    error: null,
  },

  // === LIFECYCLE ===
  init() {
    // Scroll vers le haut lors des changements de phase
    this.$watch('currentPhase', () => {
      this.scrollToTop();
    });
  },

  scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
      // Peut continuer si on a des chunks sélectionnés ou des résultats sélectionnés (ancien format)
      return this.hasSelection || this.selectedChunks.length > 0;
    }
    if (this.currentPhase === 2) {
      // Peut continuer si on a des éléments sélectionnés (étape 1 ou co-recos étape 2)
      return this.selectedCitationsForStep2.length > 0 || this.selectedCoRecoIds.length > 0;
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
    // Collecter les items depuis l'ancien format (results)
    const selectedItems = this.results.filter((r) => r.isSelected);

    // Collecter les citations des chunks sélectionnés (nouveau format)
    const selectedCitations = [];
    this.selectedChunks.forEach((index) => {
      const chunk = this.answerChunks[index];
      if (chunk && chunk.sources) {
        chunk.sources.forEach((label) => {
          const citation = this.getCitationByLabel(label);
          if (citation && !selectedCitations.find((c) => c.label === citation.label)) {
            selectedCitations.push({
              id: citation.label,
              title: citation.title,
              content: citation.content,
              type: citation.source_type,
              resourceId: citation.resource_id,
              recoId: citation.reco_id,
              projectId: citation.project_id,
            });
          }
        });
      }
    });

    // Collecter les co-recommandations sélectionnées (à implémenter si besoin)
    const allItems = [...selectedItems, ...selectedCitations];

    if (allItems.length > 0) {
      this.phaseHistory.push({
        phase: this.currentPhase,
        query: this.searchQuery,
        selectedItems: [...allItems],
      });
      this.allSelectedItems = [...this.allSelectedItems, ...allItems];
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
      // Regrouper les items sélectionnés par type
      const grouped = this.groupByType(this.allSelectedItems);

      this.synthesis = {
        resources: grouped.resource || grouped.Resource || grouped.Document || [],
        projects: grouped.project || grouped.Project || [],
        recommendations: grouped.recommendation || grouped.Recommendation || [],
      };

      // Ajouter les co-recommandations SÉLECTIONNÉES aux ressources de la synthèse
      const selectedCoRecos = this.getSelectedCoRecommendations();
      if (selectedCoRecos.length > 0) {
        const coRecoItems = selectedCoRecos.map((resource) => ({
          id: resource.id || resource.resourceId,
          title: resource.title,
          content: resource.content || '',
          type: 'Resource',
          resourceId: resource.resourceId || resource.id,
          category: resource.category,
          tags: resource.tags,
          coOccurrenceScore: resource.coOccurrenceScore,
          isCoRecommendation: true, // Marqueur pour identifier les co-recos
        }));
        this.synthesis.resources = [...this.synthesis.resources, ...coRecoItems];
      }

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
    this.coRecommendations = [];
    this.isLoadingCoRecos = false;
    this.selectedCitationsForStep2 = [];
    this.selectedCoRecoIds = [];
    this.synthesis = {
      resources: [],
      projects: [],
      recommendations: [],
    };
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

  // === CO-RECOMMANDATIONS ===
  getSelectedResourceIds() {
    // Extraire les resource_ids directs des citations de type Resource
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
    // Récupérer les citations de type Recommendation qui n'ont pas de resource_id direct
    const recoCitations = [];
    this.selectedChunks.forEach((index) => {
      const chunk = this.answerChunks[index];
      if (chunk && chunk.sources) {
        chunk.sources.forEach((label) => {
          const citation = this.getCitationByLabel(label);
          if (citation && citation.source_type === 'Recommendation' && !citation.resource_id && citation.reco_id) {
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
    // Appeler l'API pour récupérer les détails de la recommandation et extraire le resource_id
    try {
      const response = await fetch(`/api/projects/${projectId}/tasks/${recoId}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
      });

      if (!response.ok) {
        console.warn(`Impossible de récupérer la task ${recoId}:`, response.status);
        return null;
      }

      const task = await response.json();
      console.log('ExplorationIA task details:', task);

      // Extraire le resource_id depuis la recommandation
      // La structure peut être task.resource ou task.recommendation.resource
      if (task.resource?.id) {
        return task.resource.id;
      }
      if (task.resource_id) {
        return task.resource_id;
      }
      // Chercher dans les sous-objets si nécessaire
      if (task.recommendations && task.recommendations.length > 0) {
        const reco = task.recommendations[0];
        if (reco.resource?.id) {
          return reco.resource.id;
        }
      }

      return null;
    } catch (err) {
      console.error('Erreur lors de la récupération de la task:', err);
      return null;
    }
  },

  async fetchResourceFromApi(resourceId) {
    // Récupérer les détails d'une ressource via l'API
    try {
      const response = await fetch(`/api/resources/${resourceId}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
      });

      if (!response.ok) {
        console.warn(`Impossible de récupérer la ressource ${resourceId}:`, response.status);
        return null;
      }

      return await response.json();
    } catch (err) {
      console.error('Erreur lors de la récupération de la ressource:', err);
      return null;
    }
  },

  async fetchCoRecommendations() {
    // Collecter les resource_ids directs
    let resourceIds = this.getSelectedResourceIds();

    // Récupérer les resource_ids depuis les recommandations sélectionnées
    const recoCitations = this.getSelectedRecommendationCitations();
    if (recoCitations.length > 0) {
      console.log('ExplorationIA: Récupération des resource_ids depuis les recommandations...', recoCitations);

      // Appeler l'API en parallèle pour chaque recommandation
      const resourceIdPromises = recoCitations.map(async (citation) => {
        if (citation.project_id && citation.reco_id) {
          const resourceId = await this.fetchResourceIdFromRecommendation(citation.project_id, citation.reco_id);
          if (resourceId) {
            // Mettre à jour la citation avec le resource_id trouvé
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

    console.log('ExplorationIA: Resource IDs pour co-recommandations:', resourceIds);

    // Sauvegarder les citations sélectionnées avant de passer à l'étape 2
    this.selectedCitationsForStep2 = this.getSelectedCitations();

    this.isLoadingCoRecos = true;
    this.error = null;

    try {
      const headers = {
        'Content-Type': 'application/json',
      };

      if (this.apiToken) {
        headers['Authorization'] = `Bearer ${this.apiToken}`;
      }

      // Construire l'URL avec les resource_ids
      const params = new URLSearchParams();
      resourceIds.forEach((id) => params.append('resource_ids', id));
      const url = `${ML_API_BASE_URL}/co-recommendations?${params.toString()}`;

      const response = await fetch(url, {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`);
      }

      const data = await response.json();
      console.log('ExplorationIA co-recommendations response:', data);

      // L'API retourne un tableau d'objets { resource_id, co_occurrence_score }
      // Il faut récupérer les détails de chaque ressource via /api/resources/{id}/
      const coRecoItems = data.co_recommendations || data || [];

      if (coRecoItems.length > 0) {
        console.log('ExplorationIA: Récupération des détails des ressources...', coRecoItems);

        // Appeler l'API en parallèle pour chaque resource_id
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
        // Filtrer les null (ressources non trouvées) et mapper vers le format attendu
        this.coRecommendations = results
          .filter((result) => result !== null)
          .map(({ resource, score }) => ({
            id: resource.id,
            title: resource.title || 'Sans titre',
            content: resource.summary || resource.content || resource.text || '',
            url: resource.url || null,
            category: resource.category?.name || null,
            tags: resource.tags || [],
            resourceId: resource.id,
            coOccurrenceScore: score,
          }));
      } else {
        this.coRecommendations = [];
      }

      // Passer à la phase 2 et effacer les chunks de l'étape 1
      if (this.currentPhase === 1) {
        this.currentPhase = 2;
        // Effacer les résultats de l'étape 1 pour afficher les co-recommandations à la place
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
    // Récupérer les citations uniques liées aux chunks sélectionnés
    // avec les textes des chunks associés (reformulations IA)
    const citations = [];

    console.log('getSelectedCitations - selectedChunks:', this.selectedChunks);
    console.log('getSelectedCitations - answerChunks:', this.answerChunks);
    console.log('getSelectedCitations - this.citations:', this.citations);

    this.selectedChunks.forEach((index) => {
      const chunk = this.answerChunks[index];
      console.log('getSelectedCitations - processing chunk at index', index, ':', chunk);

      if (chunk && chunk.sources) {
        chunk.sources.forEach((label) => {
          const citation = this.getCitationByLabel(label);
          console.log('getSelectedCitations - label:', label, 'citation found:', citation);

          if (citation) {
            const existingCitation = citations.find((c) => c.label === citation.label);
            if (existingCitation) {
              // Ajouter le texte du chunk s'il n'est pas déjà présent
              if (chunk.text && !existingCitation.chunkTexts.includes(chunk.text)) {
                existingCitation.chunkTexts.push(chunk.text);
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

    console.log('getSelectedCitations - final citations:', citations);
    return citations;
  },

  hasSelectedResources() {
    // Vérifie s'il y a des ressources directes OU des recommandations (qui peuvent avoir des ressources liées)
    const hasDirectResources = this.getSelectedResourceIds().length > 0;
    const hasRecommendations = this.getSelectedRecommendationCitations().length > 0;
    return hasDirectResources || hasRecommendations;
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
    return this.coRecommendations.filter((r) => this.selectedCoRecoIds.includes(r.id));
  },

  // Combine toutes les ressources sélectionnées (étape 1 + étape 2) pour la synthèse
  getAllSelectedResources() {
    const allResources = [];

    // Ajouter les citations de l'étape 1
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

    // Ajouter les co-recommandations de l'étape 2
    this.getSelectedCoRecommendations().forEach((resource) => {
      allResources.push({
        id: resource.id,
        title: resource.title,
        content: resource.content,
        source_type: 'Resource',
        resource_id: resource.resourceId || resource.id,
        category: resource.category,
        tags: resource.tags,
        coOccurrenceScore: resource.coOccurrenceScore,
        fromStep: 2,
      });
    });

    return allResources;
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

      // Si pas de resource_id direct mais c'est une recommandation, essayer de récupérer la ressource liée
      if (!resourceId && citation.reco_id && citation.project_id) {
        console.log('Récupération de la recommandation...', citation);
        const recommendation = await this.fetchRecommendationDetails(citation.project_id, citation.reco_id);

        if (recommendation) {
          this.resourceModal.recommendation = recommendation;

          // Extraire le resource_id depuis la recommandation
          if (recommendation.resource?.id) {
            resourceId = recommendation.resource.id;
          } else if (recommendation.resource_id) {
            resourceId = recommendation.resource_id;
          }

          // Mettre à jour la citation avec le resource_id trouvé
          if (resourceId) {
            citation.resource_id = resourceId;
          }
        }
      }

      // Si on a un resourceId, charger la ressource
      if (resourceId) {
        const resource = await this.fetchResourceFromApi(resourceId);
        if (resource) {
          this.resourceModal.resource = resource;
        }
      }

      // Si pas de ressource mais on a une recommandation, c'est OK (on affichera le contenu de la reco)
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

  async fetchRecommendationDetails(projectId, recoId) {
    try {
      const response = await fetch(`/api/projects/${projectId}/tasks/${recoId}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
      });

      if (!response.ok) {
        console.warn(`Impossible de récupérer la recommandation ${recoId}:`, response.status);
        return null;
      }

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

  highlightCitationInContent(content, citationContent) {
    if (!content || !citationContent) return content;

    // Nettoyer et normaliser le passage cité pour la recherche
    const normalizedCitation = citationContent.trim();
    if (normalizedCitation.length < 10) return content;

    // Échapper les caractères spéciaux pour l'expression régulière
    const escapedCitation = normalizedCitation.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

    // Créer une regex pour trouver le passage (insensible à la casse, avec tolérance aux espaces)
    const flexiblePattern = escapedCitation.replace(/\s+/g, '\\s+');

    try {
      const regex = new RegExp(`(${flexiblePattern})`, 'gi');
      const highlighted = content.replace(
        regex,
        '<mark class="exploration-ia-highlight">$1</mark>'
      );
      return highlighted;
    } catch (e) {
      // Si la regex échoue, essayer une recherche simple
      const index = content.toLowerCase().indexOf(normalizedCitation.toLowerCase());
      if (index !== -1) {
        const before = content.substring(0, index);
        const match = content.substring(index, index + normalizedCitation.length);
        const after = content.substring(index + normalizedCitation.length);
        return `${before}<mark class="exploration-ia-highlight">${match}</mark>${after}`;
      }
      return content;
    }
  },

  getResourceContentWithHighlight() {
    if (!this.resourceModal.resource || !this.resourceModal.citation) {
      return '';
    }

    const resource = this.resourceModal.resource;
    const citationContent = this.resourceModal.citation.content;

    // Construire le contenu complet de la ressource
    let fullContent = resource.content || resource.text || resource.summary || '';

    // Appliquer la mise en surbrillance
    const highlightedContent = this.highlightCitationInContent(fullContent, citationContent);

    // Parser le markdown et sanitize
    return this.parseMarkdown(highlightedContent);
  },

  getRecommendationContentWithHighlight() {
    if (!this.resourceModal.recommendation || !this.resourceModal.citation) {
      return '';
    }

    const recommendation = this.resourceModal.recommendation;
    const citationContent = this.resourceModal.citation.content;

    // Le contenu de la recommandation peut être dans différents champs
    let fullContent = recommendation.content || recommendation.comment || recommendation.intent || '';

    // Appliquer la mise en surbrillance
    const highlightedContent = this.highlightCitationInContent(fullContent, citationContent);

    // Parser le markdown et sanitize
    return this.parseMarkdown(highlightedContent);
  },

  // Vérifie si on a du contenu à afficher (ressource ou recommandation)
  hasModalContent() {
    return this.resourceModal.resource || this.resourceModal.recommendation;
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
      1: 'Sélectionner les passages qui vous semble pertinent avant de continuer',
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
