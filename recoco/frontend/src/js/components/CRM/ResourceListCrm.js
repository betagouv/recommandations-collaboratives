import Alpine from 'alpinejs';
import api, { resourcesUrl } from '../../utils/api';
import { ToastType } from '../../models/toastType';

Alpine.data('ResourceListCrm', (departments, regions) => ({
  dataLoaded: false,
  resources: [],
  resourcesToDisplay: [],
  resourcesTotal: 0,
  departments: JSON.parse(departments.textContent),
  regions: JSON.parse(regions.textContent),
  territorySelectAll: true,
  backendSearch: {
    searchText: '',
    searchDepartment: [],
    searchStatus: [],
  },
  searchText: '',
  pagination: {
    currentPage: 1,
    limit: 20,
    total: 0,
  },
  options: [
    {
      value: 'PRE_DRAFT',
      text: 'Incomplet',
      color: 'fr-badge--new fr-badge fr-badge--no-icon font-size-10px',
      tooltip:
        "Le déposant n'est pas allé jusqu'au bout du dépôt de sa demande",
      dataTestId: 'status-pre-draft',
    },
    {
      value: 'DRAFT',
      text: 'A modérer',
      color: 'fr-badge--new fr-badge fr-badge--no-icon font-size-10px',
      tooltip: 'En attente de validation ou refus de votre part',
    },
    {
      value: 'TO_PROCESS',
      text: 'A traiter',
      color: 'fr-badge--info fr-badge fr-badge--no-icon font-size-10px',
      tooltip: "Statut d'avancement du dossier selon votre tableau de bord",
    },
    {
      value: 'READY',
      text: 'En attente',
      color:
        'fr-badge--success-lighter fr-badge fr-badge--no-icon font-size-10px',
      tooltip: "Statut d'avancement du dossier selon votre tableau de bord",
    },
    {
      value: 'IN_PROGRESS',
      text: 'En cours',
      color:
        'fr-badge--success-lighter fr-badge fr-badge--no-icon font-size-10px',
      tooltip: "Statut d'avancement du dossier selon votre tableau de bord",
    },
    {
      value: 'DONE',
      text: 'Traité',
      color:
        'fr-badge--success-lighter fr-badge fr-badge--no-icon font-size-10px',
      tooltip: "Statut d'avancement du dossier selon votre tableau de bord",
    },
    {
      value: 'STUCK',
      text: 'Interrompu',
      color: 'fr-badge--info fr-badge fr-badge--no-icon font-size-10px',
      tooltip: "Statut d'avancement du dossier selon votre tableau de bord",
    },
    {
      value: 'REJECTED',
      text: 'Rejeté',
      color: 'fr-badge--error fr-badge fr-badge--no-icon font-size-10px',
      tooltip: "Dossier refusé à l'étape de la modération",
    },
  ],
  displayResourceIndex: false,
  async init() {
    const resourcesResponse = await this.getResources();
    // this.resources.push([...resourcesResponse.results]);
    this.resources.push([...resourcesResponse]);
    // this.resourcesToDisplay = [...resourcesResponse.results];
    this.resourcesToDisplay = [...resourcesResponse];
    this.resourcesTotal = resourcesResponse.count;
    this.pagination.total = Math.ceil(
      resourcesResponse.count / this.pagination.limit
    );
    this.dataLoaded = true;
  },
  /************************
   * Filtering functions
   **************************/
  updateResourceListAndPagination(resources) {
    this.resources = [];
    // this.resources.push([...resources.results]);
    this.resources.push([...resources]);
    // this.resourcesToDisplay = [...resources.results];
    this.resourcesToDisplay = [...resources];
    this.resourcesTotal = resources.count;
    this.pagination.total = Math.ceil(resources.count / this.pagination.limit);
  },
  async saveSelectedDepartment(event) {
    if (!event.detail) return;

    this.backendSearch.searchDepartment = [...event.detail];
    const resources = await this.handleResourceSearch();
    this.updateResourceListAndPagination(resources);
  },
  async saveSelectedStatus(event) {
    if (!event.detail) return;

    this.backendSearch.searchStatus = [...event.detail];
    const resources = await this.handleResourceSearch();
    this.updateResourceListAndPagination(resources);
  },
  async onSearch() {
    const resources = await this.handleResourceSearch();
    this.updateResourceListAndPagination(resources);
  },
  async handleResourceSearch() {
    try {
      return await this.getResources({
        offset: 0,
        page: 1,
        search: this.backendSearch.searchText,
        departments: this.backendSearch.searchDepartment,
        status: this.backendSearch.searchStatus,
      });
    } catch (error) {
      this.showToast(
        `Erreur lors de la recherche des projets`,
        ToastType.error
      );
      throw new Error(`Error while searching resources`, error);
    }
  },

  /************************
   * Pagination functions
   **************************/
  async onChangePage(pageNumber) {
    if (this.resources.length <= this.pagination.limit * (pageNumber - 1)) {
      const resourcesResponse = await this.getResources({
        offset: this.pagination.limit * (pageNumber - 1),
        page: pageNumber,
      });
      // this.resources[pageNumber - 1] = [...resourcesResponse.results];
      this.resources[pageNumber - 1] = [...resourcesResponse];
    }
    this.resourcesToDisplay = [...this.resources[pageNumber - 1]];
    this.pagination.currentPage = pageNumber;
  },
  async handleChangePage(pageNumber) {
    const resources = await api.get(
      resourcesUrl({
        limit: this.pagination.limit,
        offset: 0,
        page: 1,
        searchText: this.backendSearch.searchText,
        departments: this.backendSearch.searchDepartment,
      })
    );
    // this.resources.push(...resources.data.results);
    this.resources.push(...resources.data);
    this.pagination.currentPage = pageNumber;
  },

  /************************
   * CRUD functions
   **************************/
  async getResources({ offset = 0, page = 1 } = {}) {
    try {
      const response = await api.get(
        resourcesUrl({
          limit: this.pagination.limit,
          offset: offset,
          page: page,
          searchText: this.backendSearch.searchText,
          departments: this.backendSearch.searchDepartment,
          status: this.backendSearch.searchStatus,
        })
      );
      return response.data;
    } catch (error) {
      this.showToast(
        `Erreur lors de la récupération des projets de la page ${page}`,
        ToastType.error
      );
      throw new Error(`Error while getting resources from page ${page}`, error);
    }
  },
  async updateResource(resourceToUpdate, url, data) {
    let formData = new FormData();
    for (let key in data) {
      formData.append(key, data[key]);
    }
    try {
      await fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]')
            .value,
        },
      });
      const updatedResource = {
        ...resourceToUpdate,
        exclude_stats: !data.statistics,
        muted: !data.notifications,
      };
      const updatedResourceIndex = this.resources[
        this.pagination.currentPage - 1
      ].findIndex((x) => x.id === resourceToUpdate.id);

      this.resources[this.pagination.currentPage - 1].splice(
        updatedResourceIndex,
        1,
        updatedResource
      );
      this.resourcesToDisplay = [
        ...this.resources[this.pagination.currentPage - 1],
      ];
      this.showToast(
        this.getToastMessage(resourceToUpdate, data),
        ToastType.success
      );
    } catch (error) {
      this.showToast(
        'Erreur lors de la mise à jour des paramètres du projet',
        ToastType.error
      );
      throw new Error('Error while updating resource param', error);
    }
  },

  /************************
   * Informational functions
   **************************/
  getToastMessage(resourceToUpdate, dataToUpdate) {
    if (dataToUpdate.statistics === resourceToUpdate.exclude_stats) {
      if (dataToUpdate.statistics) {
        return 'Le projet apparaitra dans les statistics';
      } else {
        return "Le projet n'apparaitra pas dans les statistics";
      }
    } else if (dataToUpdate.notifications === resourceToUpdate.muted) {
      if (dataToUpdate.notifications) {
        return 'Les notifications sont activées pour le projet';
      } else {
        return 'Les notifications sont désactivées pour le projet';
      }
    }
  },
  showToast(message, type) {
    this.$store.app.notification.message = message;
    this.$store.app.notification.timeout = 5000;
    this.$store.app.notification.isOpen = true;
    this.$store.app.notification.type = type || ToastType.error;
  },

  /*******************
   * Display functions
   ********************/
  resourcesCountLabel() {
    if (this.resourcesTotal > 0) {
      return `${this.resourcesTotal} résultat${this.resourcesTotal > 1 ? 's' : ''}`;
    } else {
      return 'Aucun résultat';
    }
  },
  resourceStatusLabel(status) {
    return (
      this.options.find((option) => option.value === status).text || status
    );
  },
  resourceStatusColor(status) {
    switch (status) {
      case 'PRE_DRAFT':
      case 'DRAFT':
        return 'fr-badge--new';
      case 'TO_PROCESS':
      case 'STUCK':
        return 'fr-badge--info';
      case 'READY':
      case 'IN_PROGRESS':
      case 'DONE':
        return 'fr-badge--success-lighter';
      case 'REJECTED':
        return 'fr-badge--error';
      default:
        return 'fr-badge--white';
    }
  },
  resourceTooltip(resource) {
    return this.options.find((option) => option.value === resource.status)
      .tooltip;
  },
}));
