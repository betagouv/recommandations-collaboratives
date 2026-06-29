import Alpine from 'alpinejs';
import api, { projectsUrl } from '../../utils/api';
import { ToastType } from '../../models/toastType';
import { ProjectStatus } from '../../models/projectStatus.enum';

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
  ProjectStatus,
  options: [
    {
      value: 'PRE_DRAFT',
      text: ProjectStatus.PRE_DRAFT.text,
      color: ProjectStatus.PRE_DRAFT.color,
      tooltip:
        "Le déposant n'est pas allé jusqu'au bout du dépôt de sa demande",
      dataTestId: 'status-pre-draft',
    },
    {
      value: 'DRAFT',
      text:ProjectStatus.DRAFT.text,
      color: ProjectStatus.DRAFT.color,
      tooltip: 'En attente de validation ou refus de votre part',
    },
    {
      value: 'TO_PROCESS',
      text:ProjectStatus.TO_PROCESS.text,
      color:  ProjectStatus.TO_PROCESS.color,
      tooltip: "Statut d'avancement du dossier selon votre tableau de bord",
    },
    {
      value: 'READY',
      text:ProjectStatus.READY.text,
      color: ProjectStatus.READY.color,
      tooltip: "Statut d'avancement du dossier selon votre tableau de bord",
    },
    {
      value: 'IN_PROGRESS',
      text:ProjectStatus.IN_PROGRESS.text,
      color:  ProjectStatus.IN_PROGRESS.color,
      tooltip: "Statut d'avancement du dossier selon votre tableau de bord",
    },
    {
      value: 'DONE',
      text:ProjectStatus.DONE.text,
      color: ProjectStatus.DONE.color,
      tooltip: "Statut d'avancement du dossier selon votre tableau de bord",
    },
    {
      value: 'STUCK',
      text:ProjectStatus.STUCK.text,
      color:  ProjectStatus.STUCK.color,
      tooltip: "Statut d'avancement du dossier selon votre tableau de bord",
    },
    {
      value: 'REJECTED',
      text:ProjectStatus.REJECTED.text,
      color:  ProjectStatus.REJECTED.color,
      tooltip: "Dossier refusé à l'étape de la modération",
    },
  ].map(opt => {return {...opt, color: `${opt.color} fr-badge fr-badge--no-icon font-size-10px`}}),
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
      this.$store.app.displayToastMessage({
        message: `Erreur lors de la recherche des projets`,
        type: ToastType.error,
      });
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
          searchText: this.backendSearch.searchText,
          departments: this.backendSearch.searchDepartment,
          status: this.backendSearch.searchStatus,
        })
      );
      return response.data;
    } catch (error) {
      this.$store.app.displayToastMessage({
        message: `Erreur lors de la récupération des projets de la page ${page}`,
        type: ToastType.error,
      });
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
      this.$store.app.displayToastMessage({
        message: this.getToastMessage(projectToUpdate, data),
        type: ToastType.success,
      });
    } catch (error) {
      this.$store.app.displayToastMessage({
        message: 'Erreur lors de la mise à jour des paramètres du projet',
        type: ToastType.error,
      });
      throw new Error(`Error while updating project param`, error);
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
  projectTooltip(project) {
    return this.options.find((option) => option.value === project.status)
      .tooltip;
  },
}));
