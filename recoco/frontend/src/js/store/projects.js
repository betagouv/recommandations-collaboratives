import Alpine from 'alpinejs';
import api, { sitesConfigUrl, userProjectStatusUrl } from '../utils/api';

Alpine.store('projects', {
  projects: [],
  userProjetsStatus: [],
  sitesConfig: [],
  async getUserProjetsStatus() {
    const json = await api.get(userProjectStatusUrl());

    return (this.userProjetsStatus = json.data.results);
  },
  async getSitesConfig() {
    const json = await api.get(sitesConfigUrl());

    return (this.sitesConfig = json.data.results);
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
    });

    return projects;
  },
});

export default Alpine.store('projects');
