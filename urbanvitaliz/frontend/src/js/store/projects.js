import Alpine from 'alpinejs'
import api, { userProjectStatusUrl } from '../utils/api'

Alpine.store('projects', {
    projects: [],
    async getProjects() {

        const json = await api.get(userProjectStatusUrl())

        return this.projects = json.data;
    }
})

export default Alpine.store('projects')
