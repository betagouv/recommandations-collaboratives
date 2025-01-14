import Alpine from 'alpinejs';
import { generateUUID } from '../utils/uuid';

import api, {
  projectsProjectSitesUrl,
  projectsUrl,
  regionsUrl,
} from '../utils/api';

Alpine.data('KanbanProjects', boardProjectsApp);

function boardProjectsApp(currentSiteId) {
  return {
    projectList: [],
    currentSiteId: currentSiteId,
    isDisplayingOnlyUserProjects:
      JSON.parse(localStorage.getItem('isDisplayingOnlyUserProjects')) ?? false,
    get isBusy() {
      return this.$store.app.isLoading;
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
    searchText: '',
    async getData(postProcess = true) {
      const projects = await api.get(projectsUrl(this.searchText));

      await this.$store.projects.mapperProjetsProjectSites(
        projects.data.results,
        this.currentSiteId
      );

      const projectList = projects.data.results.map((d) =>
        Object.assign(d, {
          uuid: generateUUID(),
        })
      );

      // FIXME: check pagination in /api/regions is off
      if (postProcess) {
        await this.postProcessData(projectList);
      }

      console.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>")
      console.log('projectList', projectList);

      this.projectList = [...projectList];
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
      // FIXME: filterProjectsByDepartments is not working anymore
      // but we should move filter stuff to backend anyway
      return this.projectList
        // .filter(this.filterProjectsByDepartments.bind(this))
        // .sort(this.sortFn.bind(this));
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
    onSearch() {
      this.getData();
    },
    async postProcessData(projectList) {
      const departments = this.extractAndCreateAdvisorDepartments(projectList);
      const regionsData = await api.get(regionsUrl());
      this.constructRegionsFilter(departments, regionsData.data);
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
    handleTerritorySelectAll() {
      this.territorySelectAll = !this.territorySelectAll;

      this.regions = this.regions.map((region) => ({
        ...region,
        active: this.territorySelectAll,
        departments: region.departments.map((department) => ({
          ...department,
          active: this.territorySelectAll,
        })),
      }));
    },
    handleRegionFilter(selectedRegion) {
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
    },
    handleDepartmentFilter(selectedDepartment) {
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
