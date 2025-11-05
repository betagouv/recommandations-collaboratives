import Alpine from 'alpinejs';
import api, { projectsUrl } from '../../utils/api';

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
        return 'Brouillon';
      case 'TO_PROCESS':
        return 'A modérer';
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
        return 'fr-badge--info';
      case 'READY':
      case 'IN_PROGRESS':
      case 'DONE':
      case 'STUCK':
        return 'fr-badge--success-lighter';
      case 'REJECTED':
        return 'fr-badge--error';
      default:
        return 'fr-badge--white';
    }
  },
}));
