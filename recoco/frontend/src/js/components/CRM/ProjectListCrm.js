import Alpine from 'alpinejs';
import api, { projectsUrl } from '../../utils/api';
import { ToastType } from '../../models/toastType';

Alpine.data('ProjectListCrm', (departments, regions) => ({
  dataLoaded: false,
  projects: [],
  projectsToDisplay: [],
  projectsTotal: 0,
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
      tooltip: "Le demandeur ou la demandeuse n'a pas encore créé son compte",
    },
    {
      value: 'DRAFT',
      text: 'A modérer',
      color: 'fr-badge--new fr-badge fr-badge--no-icon font-size-10px',
    },
    {
      value: 'TO_PROCESS',
      text: 'A traiter',
      color: 'fr-badge--info fr-badge fr-badge--no-icon font-size-10px',
    },
    {
      value: 'READY',
      text: 'En attente',
      color:
        'fr-badge--success-lighter fr-badge fr-badge--no-icon font-size-10px',
    },
    {
      value: 'IN_PROGRESS',
      text: 'En cours',
      color:
        'fr-badge--success-lighter fr-badge fr-badge--no-icon font-size-10px',
    },
    {
      value: 'DONE',
      text: 'Traité',
      color:
        'fr-badge--success-lighter fr-badge fr-badge--no-icon font-size-10px',
    },
    {
      value: 'STUCK',
      text: 'Conseil interrompu',
      color: 'fr-badge--info fr-badge fr-badge--no-icon font-size-10px',
    },
    {
      value: 'REJECTED',
      text: 'Rejeté',
      color: 'fr-badge--error fr-badge fr-badge--no-icon font-size-10px',
    },
  ],
  displayProjectIndex: false,
  async init() {
    const projectsResponse = await this.getProjects();
    this.projects.push([...projectsResponse.results]);
    this.projectsToDisplay = [...projectsResponse.results];
    this.projectsTotal = projectsResponse.count;
    this.pagination.total = Math.ceil(
      projectsResponse.count / this.pagination.limit
    );
    this.dataLoaded = true;
  },
  /************************
   * Filtering functions
   **************************/
  updateProjectListAndPagination(projects) {
    this.projects = [];
    this.projects.push([...projects.results]);
    this.projectsToDisplay = [...projects.results];
    this.projectsTotal = projects.count;
    this.pagination.total = Math.ceil(projects.count / this.pagination.limit);
  },
  async saveSelectedDepartment(event) {
    if (!event.detail) return;

    this.backendSearch.searchDepartment = [...event.detail];
    const projects = await this.handleProjectSearch();
    this.updateProjectListAndPagination(projects);
  },
  async saveSelectedStatus(event) {
    if (!event.detail) return;

    this.backendSearch.searchStatus = [...event.detail];
    const projects = await this.handleProjectSearch();
    this.updateProjectListAndPagination(projects);
  },
  async onSearch() {
    const projects = await this.handleProjectSearch();
    this.updateProjectListAndPagination(projects);
  },
  async handleProjectSearch() {
    try {
      return await this.getProjects({
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
      throw new Error(`Error while searching projects`, error);
    }
  },

  /************************
   * Pagination functions
   **************************/
  async onChangePage(pageNumber) {
    if (this.projects.length <= this.pagination.limit * (pageNumber - 1)) {
      const projectsResponse = await this.getProjects({
        offset: this.pagination.limit * (pageNumber - 1),
        page: pageNumber,
      });
      this.projects[pageNumber - 1] = [...projectsResponse.results];
    }
    this.projectsToDisplay = [...this.projects[pageNumber - 1]];
    this.pagination.currentPage = pageNumber;
  },
  async handleChangePage(pageNumber) {
    const projects = await api.get(
      projectsUrl({
        limit: this.pagination.limit,
        offset: 0,
        page: 1,
        search: this.backendSearch.searchText,
        departments: this.backendSearch.searchDepartment,
      })
    );
    this.projects.push(...projects.data.results);
    this.pagination.currentPage = pageNumber;
  },

  /************************
   * CRUD functions
   **************************/
  async getProjects({ offset = 0, page = 1 } = {}) {
    try {
      const response = await api.get(
        projectsUrl({
          limit: this.pagination.limit,
          offset: offset,
          page: page,
          search: this.backendSearch.searchText,
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
      throw new Error(`Error while getting projects from page ${page}`, error);
    }
  },
  async updateProject(projectToUpdate, url, data) {
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
      const updatedProject = {
        ...projectToUpdate,
        exclude_stats: !data.statistics,
        muted: !data.notifications,
      };
      const updatedProjectIndex = this.projects[
        this.pagination.currentPage - 1
      ].findIndex((x) => x.id === projectToUpdate.id);

      this.projects[this.pagination.currentPage - 1].splice(
        updatedProjectIndex,
        1,
        updatedProject
      );
      this.projectsToDisplay = [
        ...this.projects[this.pagination.currentPage - 1],
      ];
      this.showToast(
        this.getToastMessage(projectToUpdate, data),
        ToastType.success
      );
    } catch (error) {
      this.showToast(
        'Erreur lors de la mise à jour des paramètres du projet',
        ToastType.error
      );
      throw new Error('Error while updating project param', error);
    }
  },

  /************************
   * Informational functions
   **************************/
  getToastMessage(projectToUpdate, dataToUpdate) {
    if (dataToUpdate.statistics === projectToUpdate.exclude_stats) {
      if (dataToUpdate.statistics) {
        return 'Le projet apparaitra dans les statistics';
      } else {
        return "Le projet n'apparaitra pas dans les statistics";
      }
    } else if (dataToUpdate.notifications === projectToUpdate.muted) {
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
  projectsCountLabel() {
    if (this.projectsTotal > 0) {
      return `${this.projectsTotal} résultat${this.projectsTotal > 1 ? 's' : ''}`;
    } else {
      return 'Aucun résultat';
    }
  },
  projectStatusLabel(status) {
    switch (status) {
      case 'PRE_DRAFT':
        return 'Incomplet';
      case 'DRAFT':
        return 'A modérer';
      case 'TO_PROCESS':
        return 'A traiter';
      case 'READY':
        return 'En attente';
      case 'IN_PROGRESS':
        return 'En cours';
      case 'DONE':
        return 'Traité';
      case 'STUCK':
        return 'Bloqué';
      case 'REJECTED':
        return 'Rejeté';
      default:
        return status;
    }
  },
  projectStatusColor(status) {
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
  projectTooltip(project) {
    return this.options.find((option) => option.value === project.status)
      .tooltip;
  },
}));
