import Alpine from 'alpinejs';
import api, { sitesConfigUrl, userProjectStatusUrl } from '../utils/api';

Alpine.store('projects', {
  projects: [],
  userProjetsStatus: [],
  sitesConfig: [],
  async getUserProjetsStatus() {
    const json = await api.get(userProjectStatusUrl());

    return (this.userProjetsStatus = json.data);
  },
  async getSitesConfig() {
    const json = await api.get(sitesConfigUrl());

    return (this.sitesConfig = json.data);
  },
  async mapperProjetsProjectSites(projects, projectSites) {
    if (this.sitesConfig.length === 0) {
      await this.getSitesConfig();
    }

    projects.forEach((project) => {
      const foundProjectSite = projectSites.find(
        (site) => site.project === project.id
      );
      const foundSiteConfig = this.sitesConfig.find(
        (config) => config.id === foundProjectSite.site
      );
      foundProjectSite.siteConfig = foundSiteConfig;
      project.origin = foundProjectSite;
    });

    return projects;
  },
});

export default Alpine.store('projects');
