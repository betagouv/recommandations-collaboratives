import Alpine from 'alpinejs';
import { generateUUID } from '../utils/uuid';
import { makeProjectURL } from '../utils/createProjectUrl';

import api, { projectsProjectSitesUrl, projectsUrl } from '../utils/api';

Alpine.data('KanbanProjects', function (currentSiteId, departments, regions) {
  return {
    makeProjectURL,
    projectList: null,
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
    filterProjectLastActivity: localStorage.getItem('lastActivity') ?? '30',
    searchText: '',
    selectedDepartment: null,
    departments: JSON.parse(departments.textContent),
    regions: JSON.parse(regions.textContent),
    territorySelectAll: true,
    boards: [
      {
        code: 'TO_PROCESS',
        title: 'À traiter',
        color_class: 'border-secondary',
      },
      { code: 'READY', title: 'En attente', color_class: 'border-info' },
      { code: 'IN_PROGRESS', title: 'En cours', color_class: 'border-primary' },
      { code: 'DONE', title: 'Traité', color_class: 'border-success' },
      {
        code: 'STUCK',
        title: 'Conseil interrompu',
        color_class: 'border-dark',
      },
    ],
    async init() {
      await this.getData();
      this.constructRegionsFilter(this.departments, this.regions);
      this.isViewInitialized = true;
    },
    async getData() {
      const { searchText, searchDepartment, lastActivity } = this.backendSearch;
      const projects = await api.get(
        projectsUrl(searchText, searchDepartment, lastActivity)
      );
      this.projectList = await this.$store.projects.mapperProjetsProjectSites(
        projects.data,
        this.currentSiteId
      );

      this.projectList = projects.data.map((d) =>
        Object.assign(d, {
          uuid: generateUUID(),
        })
      );
    },
    get view() {
      return this.projectList.sort(this.sortFn.bind(this));
    },
    column(status) {
      if (status instanceof Array) {
        return this.view.filter((d) => status.indexOf(d.status) !== -1);
      } else {
        return this.view.filter((d) => d.status === status);
      }
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
    async onDrop(event, status) {
      event.preventDefault();

      this.currentlyHoveredElement.classList.remove('drag-target');
      this.currentlyHoveredElement = null;

      const uuid = event.dataTransfer.getData('application/uuid');
      if (!uuid) {
        return;
      }
      const droppedProject = this.projectList.find((d) => d.uuid === uuid);
      if (!droppedProject) {
        return;
      }
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
    },
    constructRegionsFilter(departments, regions) {
      const currentRegions = [];
      const displayedProjectsDepartments =
        this.extractDepartmentFromDisplayedProjects(this.projectList);

      regions.forEach((region) => {
        //Iterate through regions.departments and look for advisors departments
        const foundDepartments = departments
          .filter((department) =>
            region.departments.find(
              (regionDepartment) => regionDepartment.code === department.code
            )
          )
          .map((department) => {
            const isIncludeInDisplayedProjects =
              displayedProjectsDepartments.includes(department.code);
            const departmentData = {
              ...department,
              active: isIncludeInDisplayedProjects,
            };
            if (isIncludeInDisplayedProjects)
              this.departments.push(departmentData);
            return departmentData;
          });

        if (foundDepartments.length > 0) {
          const currentRegion = {
            code: region.code,
            departments: foundDepartments,
            name: region.name,
            active:
              foundDepartments.length ===
              foundDepartments.filter((department) => department.active).length,
          };

          return currentRegions.push(currentRegion);
        }
      });
      this.regions = currentRegions;
    },
    extractDepartmentFromDisplayedProjects(projects) {
      const departments = projects.map(
        (project) => project?.commune?.department.code
      );
      return [...new Set(departments)];
    },
    async onSearch(event) {
      this.backendSearch.searchText = event.target.value;
      await this.backendSearchProjects({ resetLastActivity: true });
    },
    async backendSearchProjects(options = { resetLastActivity: false }) {
      if (this.backendSearch.searchText !== '') {
        this.$refs.selectFilterProjectDuration.disabled = true;
        this.$refs.selectFilterProjectDuration.value = 1460;
        this.backendSearch.lastActivity = '';
      } else if (options.resetLastActivity) {
        this.$refs.selectFilterProjectDuration.disabled = false;
        this.$refs.selectFilterProjectDuration.value = 30;
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
  };
});
