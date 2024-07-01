import Alpine from 'alpinejs';
import api, { userProjectStatusListUrl } from '../utils/api';

Alpine.store('projects', {
  projects: [],
  async getProjects() {
    const json = await api.get(userProjectStatusListUrl());
    return (this.projects = json.data.results);
  },
});

export default Alpine.store('projects');
