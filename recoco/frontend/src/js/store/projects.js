import Alpine from 'alpinejs';
import api, { sitesConfigUrl, userProjectStatusUrl } from '../utils/api';

Alpine.store('projects', {
  projects: [],
  userProjetsStatus: [],
  sitesConfig: [],
  setProjectsToLocalStorage(projects, siteLabel = 'default') {
    Date.prototype.addHours = function (h) {
      this.setTime(this.getTime() + h * 60 * 60 * 1000);
      return this;
    };

    const saveObjects = {
      projects,
      expireAt: new Date().addHours(1),
    };

    localStorage.setItem(
      `projects-data-${siteLabel}`,
      JSON.stringify(saveObjects)
    );
  },
  getProjectsFromLocalStorage(siteLabel = 'default') {
    const localStorageProjects = localStorage.getItem(
      `projects-data-${siteLabel}`
    );
    if (!localStorageProjects) {
      return null;
    }
    const savedProjects = JSON.parse(localStorageProjects);
    const expireAt = new Date(savedProjects?.expireAt).valueOf();
    const now = new Date().valueOf();
    if (expireAt > now) {
      return savedProjects.projects;
    }
  },
  resetProjectsLocalStorage(siteLabel = 'default') {
    localStorage.removeItem(`projects-data-${siteLabel}`);
  },
  async getUserProjetsStatus() {
    const json = await api.get(userProjectStatusUrl());

    return (this.userProjetsStatus = json.data);
  },
  async getSitesConfig() {
    const json = await api.get(sitesConfigUrl());

    return (this.sitesConfig = json.data);
  },
  async mapperProjetsProjectSites(projects, currentSiteId) {
    if (this.sitesConfig.length === 0) {
      await this.getSitesConfig();
    }

    projects.forEach((project) => {
      project.project_sites.forEach((projectSite) => {
        projectSite.siteInfo = this.sitesConfig.find(
          (site) => site.id === projectSite.site
        );
      });
      project.origin = project.project_sites.find(
        (projectSite) => projectSite.is_origin
      );
      project.currentSite = project.project_sites.find(
        (projectSite) => projectSite.site === currentSiteId
      );
      project.publishTo = project.project_sites
        .filter((projectSite) => !projectSite.is_origin)
        .map((projectSite) => {
          return {
            ...projectSite,
            siteInfo: this.sitesConfig.find(
              (site) => site.id === projectSite.site
            ),
          };
        });
    });

    return projects;
  },
});

export default Alpine.store('projects');
