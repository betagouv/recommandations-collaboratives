import Alpine from 'alpinejs';
import { generateUUID } from '../utils/uuid';
import { makeProjectURL } from '../utils/createProjectUrl';

import api, { projectsProjectSitesUrl, projectsUrl } from '../utils/api';

Alpine.data('KanbanProjects', function (currentSiteId, departments, regions) {
  return {
    makeProjectURL,
    isViewInitialized: false,
    currentSiteId: currentSiteId,
    isDisplayingOnlyUserProjects:
      JSON.parse(localStorage.getItem('isDisplayingOnlyUserProjects')) ?? false,
    get isBusy() {
      return this.$store.app.isLoading;
    },
    backendSearch: {
      searchText: '',
      searchDepartment: [],
      lastActivity: localStorage.getItem('lastActivity') ?? '30',
    },
    searchText: '',
    filterProjectLastActivity: localStorage.getItem('lastActivity') ?? '30',
    regions: JSON.parse(regions.textContent),
    territorySelectAll: true,
    boards: [
      {
        code: 'TO_PROCESS',
        title: 'À traiter',
        color_class: 'border-secondary',
        projects: [],
        allProjects: [],
      },
      {
        code: 'READY',
        title: 'En attente',
        color_class: 'border-info',
        projects: [],
        allProjects: [],
      },
      {
        code: 'IN_PROGRESS',
        title: 'En cours',
        color_class: 'border-primary',
        projects: [],
        allProjects: [],
      },
      {
        code: 'DONE',
        title: 'Traité',
        color_class: 'border-success',
        projects: [],
        allProjects: [],
      },
      {
        code: 'STUCK',
        title: 'Conseil interrompu',
        color_class: 'border-dark',
        projects: [],
        allProjects: [],
      },
    ],
    async init() {
      await this.getData();
      this.isViewInitialized = true;
    },
    async getData() {
      await Promise.all(
        this.boards.map(async (board) => {
          const response = await api.get(
            projectsUrl({
              searchText: this.backendSearch.searchText,
              departments: this.backendSearch.searchDepartment,
              lastActivity: this.backendSearch.lastActivity,
              limit: 10,
              status: [board.code],
            })
          );

          const mappedProjects =
            await this.$store.projects.mapperProjetsProjectSites(
              response.data.results,
              this.currentSiteId
            );

          board.projects = mappedProjects.map((d) =>
            Object.assign(d, { uuid: generateUUID() })
          );
          board.allProjects = [...board.projects];
        })
      );
      this.filterMyProjects();
    },
    getBoard(status) {
      return this.boards.find((board) => board.code === status);
    },
    column(status) {
      const board = this.getBoard(status);
      return board ? board.projects.sort(this.sortFn.bind(this)) : [];
    },
    onDragStart(event, uuid) {
      event.dataTransfer.clearData();
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('application/uuid', uuid);
      event.target.classList.add('drag-dragging');
      document
        .querySelectorAll('.drop-column')
        .forEach((e) => e.classList.add('drop-highlight'));
    },
    onDragEnd(event) {
      event.target.classList.remove('drag-dragging');
      document
        .querySelectorAll('.drop-column')
        .forEach((e) => e.classList.remove('drop-highlight'));
    },
    onDragEnter(event) {
      if (
        this.currentlyHoveredElement &&
        this.currentlyHoveredElement !== event.currentTarget
      ) {
        this.currentlyHoveredElement.classList.remove('drag-target');
      }
      this.currentlyHoveredElement = event.currentTarget;
      event.currentTarget.classList.add('drag-target');
    },
    onDragLeave(event) {
      if (event.target === this.currentlyHoveredElement) {
        event.target.classList.remove('drag-target');
      }
    },
    onDragOver(event) {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
    },
    findProjectByUuid(uuid) {
      for (const board of this.boards) {
        const project = board.projects.find((d) => d.uuid === uuid);
        if (project) {
          return project;
        }
      }
      return null;
    },
    async onDrop(event, status) {
      event.preventDefault();

      this.currentlyHoveredElement.classList.remove('drag-target');
      this.currentlyHoveredElement = null;

      const uuid = event.dataTransfer.getData('application/uuid');
      if (!uuid) {
        return;
      }
      const found = this.findProjectByUuid(uuid);
      if (!found) {
        return;
      }
      const droppedProject = found;
      const projectSite = droppedProject.project_sites.find(
        (project_site) => project_site.site === this.currentSiteId
      );
      if (!projectSite) {
        return;
      }
      await api.patch(`${projectsProjectSitesUrl()}${projectSite.id}/`, {
        status: status,
      });

      await this.getData();
    },
    async onLastActivityChange(event) {
      this.backendSearch.lastActivity = event.target.value;
      localStorage.setItem('lastActivity', this.backendSearch.lastActivity);
      await this.getData();
    },
    toggleMyProjectsFilter() {
      this.isDisplayingOnlyUserProjects = !this.isDisplayingOnlyUserProjects;
      localStorage.setItem(
        'isDisplayingOnlyUserProjects',
        this.isDisplayingOnlyUserProjects
      );
      this.filterMyProjects();
    },
    filterMyProjects() {
      this.boards.forEach((board) => {
        if (this.isDisplayingOnlyUserProjects) {
          board.projects = board.allProjects.filter(
            (d) => d.is_observer || d.is_switchtender
          );
        } else {
          board.projects = [...board.allProjects];
        }
      });
    },
    async onSearch(event) {
      this.backendSearch.searchText = event.target.value;
      await this.backendSearchProjects({ resetLastActivity: true });
    },
    async backendSearchProjects(options = { resetLastActivity: false }) {
      if (this.backendSearch.searchText !== '') {
        if (this.$refs.selectFilterProjectDuration) {
          this.$refs.selectFilterProjectDuration.disabled = true;
          this.$refs.selectFilterProjectDuration.value = 1460;
        }
        this.backendSearch.lastActivity = '';
      } else if (options.resetLastActivity) {
        if (this.$refs.selectFilterProjectDuration) {
          this.$refs.selectFilterProjectDuration.disabled = false;
          this.$refs.selectFilterProjectDuration.value = 30;
        }
        this.backendSearch.lastActivity = '30';
      }

      await this.getData();
    },
    async saveSelectedDepartment(event) {
      if (!event.detail) return;

      this.backendSearch.searchDepartment = [...event.detail];
      await this.backendSearchProjects();
    },

    sortFn(a, b) {
      if (b.notifications.count - a.notifications.count)
        return b.notifications.count - a.notifications.count;
      else {
        return b.created_on - a.created_on;
      }
    },
    truncate(input, size = 30) {
      return input.length > size ? `${input.substring(0, size)}...` : input;
    },
    formatDateDisplay(date) {
      return new Date(date).toLocaleDateString('fr-FR');
    },
    async onTagClick(tag) {
      this.backendSearch.searchText = tag;
      this.searchText = '#' + tag;
      await this.backendSearchProjects({ resetLastActivity: true });
    },
  };
});
