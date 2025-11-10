import Alpine from 'alpinejs';
import api, { projectsUrl, projectUrl } from '../../utils/api';

Alpine.data('ProjectListCrm', () => ({
  projects: null,
  projectsTotal: 0,
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
  async updateProject(projectId, data) {
    try {
      const response = await api.patch(projectUrl(projectId), data);
      let index = this.projects.findIndex(
        (project) => project.id === projectId
      );
      if (index !== -1) {
        this.projects[index] = {
          ...this.projects[index],
          ...response.data.exclude_stats,
          ...response.data.muted,
        };
      }
    } catch (error) {
      console.error(error);
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
