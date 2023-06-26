import Alpine from 'alpinejs'
import api, { tasksUrl } from '../utils/api'
import { generateUUID } from '../utils/uuid'

Alpine.store('tasks', {
    init() {
        console.log('tasks store init ', this.currentView);
    },
    currentView: 'inline',
    tasks: [],
    switchView() {
        this.currentView === 'inline' ? this.currentView = 'kanban' : this.currentView = 'inline'
    },
    async getTasks(projectId) {
        const json = await api.get(tasksUrl(projectId))

        const data = json.data.map(d => Object.assign(d, {
            uuid: generateUUID()
        }));

        return this.tasks = data;
    }
})

export default Alpine.store('tasks')
