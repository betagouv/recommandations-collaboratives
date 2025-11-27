import Alpine from 'alpinejs';
import api, { projectsUrl } from '../../utils/api';

Alpine.data('ProjectListCrm', (departments, regions) => ({
  projects: null,
  projectsTotal: 0,
  departments: JSON.parse(departments.textContent),
  regions: JSON.parse(regions.textContent),
  territorySelectAll: true,
  backendSearch: {
    searchText: '',
    searchDepartment: [],
  },
  searchText: '',
  pagination: {
    currentPage: 1,
    limit: 42,
    total: 0,
  },
  async init() {
    await this.getProjects();
  },
  async getProjects() {
    try {
      const response = await api.get(
        projectsUrl({ limit: 42, offset: 0, page: 1 })
      );
      this.projects = response.data.results;
      this.projectsTotal = response.data.count;
    } catch (error) {
      console.error(error);
    }
  },
  async handleProjectSearch() {
    const projects = await api.get(
      projectsUrl({
        limit: this.pagination.limit,
        offset: 0,
        page: 1,
        search: this.backendSearch.searchText,
        departments: this.backendSearch.searchDepartment,
      })
    );
    this.projects = projects.data.results;
    this.projectsTotal = projects.data.count;
    this.pagination.total = Math.ceil(
      projects.data.count / this.pagination.limit
    );
  },
  async saveSelectedDepartment(event) {
    if (!event.detail) return;

    this.backendSearch.searchDepartment = [...event.detail];
    await this.handleProjectSearch();
  },
  async onSearch() {
    await this.handleProjectSearch();
  },
  async updateProject(projectToUpdate, url, data) {
    let formData = new FormData();
    for (let key in data) {
      console.log(key, data[key]);
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
      const updatedProjectIndex = this.projects.findIndex(
        (x) => x.id === projectToUpdate.id
      );

      this.projects.splice(updatedProjectIndex, 1, updatedProject);
      this.projects = [...this.projects];
    } catch (error) {
      throw new Error('Error while updating project param', error);
    }
  },
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
}));
