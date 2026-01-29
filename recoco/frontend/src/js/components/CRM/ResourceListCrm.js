import Alpine from 'alpinejs';
import api, { resourcesUrl } from '../../utils/api';
import { ToastType } from '../../models/toastType';

Alpine.data('ResourceListCrm', (departments, regions, categories) => ({
  dataLoaded: false,
  resources: [],
  resourcesToDisplay: [],
  resourcesTotal: 0,
  departments: JSON.parse(departments.textContent),
  regions: JSON.parse(regions.textContent),
  categories: JSON.parse(categories.textContent),
  territorySelectAll: true,
  backendSearch: {
    searchText: '',
    searchDepartment: [],
    searchStatus: [],
    searchCategory: '',
  },
  searchText: '',
  pagination: {
    currentPage: 1,
    limit: 20,
    total: 0,
  },
  options: [
    {
      value: 0,
      text: 'Brouillon',// DRAFT
      color: 'fr-badge--new fr-badge fr-badge--no-icon font-size-10px',
      tooltip:
        "La ressource est en cours de création",
    },
    {
      value: 1,
      text: 'A relire',// TO_REVIEW
      color: 'fr-badge--info fr-badge fr-badge--no-icon font-size-10px',
      tooltip: 'La ressource est en attente de validation',
    },
    {
      value: 2,
      text: 'Publié',// PUBLISHED
      color: 'fr-badge--success-lighter fr-badge fr-badge--no-icon font-size-10px',
      tooltip: "La ressource est publiée",
    },
  ],
  displayResourceIndex: false,
  async init() {
    const resourcesResponse = await this.getResources();
    this.resources.push([...resourcesResponse.results]);
    this.resourcesToDisplay = [...resourcesResponse.results];
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
    this.resources.push([...resources.results]);
    this.resourcesToDisplay = [...resources.results];
    this.resourcesTotal = resources.count;
    this.pagination.currentPage = 1;
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
  async saveSelectedCategory() {
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
      });
    } catch (error) {
      this.showToast(
        `Erreur lors de la recherche des ressources`,
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
      });
      this.resources[pageNumber - 1] = [...resourcesResponse.results];
    }
    this.resourcesToDisplay = [...this.resources[pageNumber - 1]];
    this.pagination.currentPage = pageNumber;
  },
  async handleChangePage(pageNumber) {
    const resources = await api.get(
      resourcesUrl({
        limit: this.pagination.limit,
        offset: this.pagination.limit * (pageNumber - 1),
        search: this.backendSearch.searchText,
        status: this.backendSearch.searchStatus,
        category: this.backendSearch.searchCategory,
      })
    );
    this.resources.push(...resources.data.results);
    this.pagination.currentPage = pageNumber;
  },

  /************************
   * CRUD functions
   **************************/
  async getResources({ offset = 0 } = {}) {
    try {
      const response = await api.get(
        resourcesUrl({
          limit: this.pagination.limit,
          offset: offset,
          search: this.backendSearch.searchText,
          status: this.backendSearch.searchStatus,
          category: this.backendSearch.searchCategory,
        })
      );
      return response.data;
    } catch (error) {
      this.showToast(
        `Erreur lors de la récupération des ressources`,
        ToastType.error
      );
      throw new Error(`Error while getting resources`, error);
    }
  },

  /************************
   * Informational functions
   **************************/
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
  isResourceExpired(resource) {
    return resource?.expires_on && new Date(resource?.expires_on) < new Date();
  },
  resourceDepartmentsLabel(resource) {
    const response = {
      shortLabel: 'Non renseigné',
      fullLabel: 'Non renseigné',
    }
    if (resource?.departments.length) {
      const departments = [...resource?.departments];
      if(departments.length > 10) {
        response.shortLabel = `${departments.slice(0, 10).join(', ')}...`;
      } else {
        response.shortLabel = departments.join(', ');
      }
      response.fullLabel = departments.join(', ');
    }
    return response;
  },
  resourceStatusColor(status) {
    switch (status) {
      case 0:
        return 'fr-badge--new';
      case 1:
        return 'fr-badge--info';
      case 2:
        return 'fr-badge--success-lighter';
      default:
        return '';
    }
  },
  resourceTooltip(resource) {
    return this.options.find((option) => option.value === resource.status)
      .tooltip;
  },
}));
