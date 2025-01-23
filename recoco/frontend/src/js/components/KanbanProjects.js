import Alpine from 'alpinejs';
import { generateUUID } from '../utils/uuid';
import Fuse from 'fuse.js';

import api, {
  projectsProjectSitesUrl,
  projectsUrl,
  regionsUrl,
  projectsMyDepartmentsUrl,
  searchProjectUrl,
} from '../utils/api';

Alpine.data('KanbanProjects', boardProjectsApp);

function boardProjectsApp(currentSiteId) {
  return {
    projectList: [],
    rawProjectList: [],
    currentSiteId: currentSiteId,
    isDisplayingOnlyUserProjects:
      JSON.parse(localStorage.getItem('isDisplayingOnlyUserProjects')) ?? false,
    get isBusy() {
      return this.$store.app.isLoading;
    },
    backendSearch: {
      searchText: '',
      searchDepartment: [],
    },
    selectedDepartment: null,
    departments: [],
    regions: [],
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
    fuse: null,
    searchText: '',
    lastActivity: '30',
    async getData(postProcess = true) {
      // const myDepartments = await api.get(projectsMyDepartmentsUrl());
      // debugger;

      const projects = await api.get(projectsUrl(this.lastActivity));
      await this.$store.projects.mapperProjetsProjectSites(
        projects.data,
        this.currentSiteId
      );

      const projectList = projects.data.map((d) =>
        Object.assign(d, {
          uuid: generateUUID(),
        })
      );

      if (postProcess) {
        await this.postProcessData();
      }
      this.projectList = [...projectList];
      this.rawProjectList = [...projectList];
      const fuseOptions = {
        keys: [
          'name',
          'commune.name',
          'commune.insee',
          'commune.department.name',
        ],
        isCaseSensitive: false,
        minMatchCharLength: 2,
        threshold: 0.3,
        findAllMatches: true,
        ignoreLocation: true,
      };
      this.fuse = new Fuse(projectList, fuseOptions);
      if (this.searchText) {
        this.filterProject(this.searchText);
      }
      return projectList;
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

      await this.getData(false);
    },
    findByUuid(uuid) {
      return this.projectList.find((d) => d.uuid === uuid);
    },
    findById(id) {
      return this.projectList.find((d) => d.id === id);
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
    onLastActivityChange(event) {
      this.lastActivity = event.target.value;
      this.getData();
    },
    // filterProject(search) {
    //   if (search === '') {
    //     this.projectList = [...this.rawProjectList];
    //     return;
    //   }
    //   const filtered = this.fuse.search(search).map((r) => r.item);
    //   this.projectList = [...filtered];
    // },
    async postProcessData() {
      const departments = await api.get(projectsMyDepartmentsUrl());
      const regionsData = await api.get(regionsUrl());
      this.constructRegionsFilter(departments.data, regionsData.data);
    },
    toggleMyProjectsFilter() {
      this.isDisplayingOnlyUserProjects = !this.isDisplayingOnlyUserProjects;
      localStorage.setItem(
        'isDisplayingOnlyUserProjects',
        this.isDisplayingOnlyUserProjects
      );
    },
    extractAndCreateAdvisorDepartments(projects) {
      const departments = [];

      projects.forEach((project) => {
        const foundDepartment = departments.find(
          (department) => department.code === project?.commune?.department?.code
        );

        if (foundDepartment) {
          return foundDepartment.nbProjects++;
        }

        const deparmentItem = {
          ...project?.commune?.department,
          active: true,
          nbProjects: 1,
        };

        departments.push(deparmentItem);
      });

      return (this.departments = departments.sort((a, b) =>
        a.name?.localeCompare(b.name)
      ));
    },
    constructRegionsFilter(departments, regions) {
      const currentRegions = [];

      regions.forEach((region) => {
        //Iterate through regions.departments and look for advisors departments
        const foundDepartments = departments.filter((department) =>
          region.departments.find(
            (regionDepartment) => regionDepartment.code === department.code
          )
        );

        if (foundDepartments.length > 0) {
          const currentRegion = {
            code: region.code,
            departments: foundDepartments,
            name: region.name,
            active: true,
          };

          return currentRegions.push(currentRegion);
        }
      });
      this.regions = currentRegions;
    },
    async onSearch(event) {
      this.backendSearch.searchText = event.target.value;
      await this.backendSearchProjects();
    },
    async backendSearchProjects() {
      this.$refs.selectFilterProjectDuration.disabled = true;
      this.$refs.selectFilterProjectDuration.value = 1460;

      const filteredProject = await api.get(
        searchProjectUrl(
          this.backendSearch.searchText,
          this.backendSearch.searchDepartment
        )
      );
      this.projectList = filteredProject.data;
    },
    saveSelectedDepartment() {
      const extractedDepartements = this.regions
        .filter((region) => region.active)
        .flatMap((region) =>
          region.departments.map((department) => department.code)
        );
      this.backendSearch.searchDepartment = [...extractedDepartements];
    },
    async handleTerritorySelectAll() {
      this.territorySelectAll = !this.territorySelectAll;

      this.regions = this.regions.map((region) => ({
        ...region,
        active: this.territorySelectAll,
        departments: region.departments.map((department) => ({
          ...department,
          active: this.territorySelectAll,
        })),
      }));

      this.saveSelectedDepartment();

      await this.backendSearchProjects();
    },
    async handleRegionFilter(selectedRegion) {
      this.regions = this.regions.map((region) => {
        if (region.code === selectedRegion.code) {
          region.active = !region.active;
          region.departments = region.departments.map((department) => ({
            ...department,
            active: region.active,
          }));
        }

        return region;
      });

      this.territorySelectAll =
        this.regions.filter((region) => region.active).length ===
        this.regions.length;

      this.saveSelectedDepartment();

      await this.backendSearchProjects();
    },
    async handleDepartmentFilter(selectedDepartment) {
      this.regions = this.regions.map((region) => ({
        ...region,
        departments: region.departments.map((department) => {
          if (department.code === selectedDepartment.code) {
            department.active = !department.active;
          }

          return department;
        }),
        active:
          region.departments.length ===
          region.departments.filter((department) => department.active).length,
      }));

      this.territorySelectAll =
        this.regions.filter((region) => region.active).length ===
        this.regions.length;

      this.saveSelectedDepartment();

      await this.backendSearchProjects();
    },
    filterProjectsByDepartments(project) {
      return this.regions.find(
        (region) =>
          region.departments.find(
            (department) =>
              department.code === project?.commune?.department?.code
          )?.active
      );
    },
    sortFn(a, b) {
      if (b.notifications.count - a.notifications.count)
        return b.notifications.count - a.notifications.count;
      else {
        return b.created_on - a.created_on;
      }
    },
    filterFn(d) {
      if (this.selectedDepartment && this.selectedDepartment !== '') {
        return (
          d.commune && d.commune.department.code == this.selectedDepartment
        );
      } else {
        return true;
      }
    },
    truncate(input, size = 30) {
      return input.length > size ? `${input.substring(0, size)}...` : input;
    },
    formatDateDisplay(date) {
      return new Date(date).toLocaleDateString('fr-FR');
    },
    isInactive(project) {
      return project.inactive_since;
    },
  };
}
