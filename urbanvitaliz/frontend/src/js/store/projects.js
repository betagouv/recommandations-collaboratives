import Alpine from 'alpinejs'
import api, { projectsUrl } from '../utils/api'

Alpine.store('projects', {
    projects: [],
    async getProjects() {

        const json = await api.get(projectsUrl())

        return this.projects = json.data;
    }
})

export default Alpine.store('projects')
