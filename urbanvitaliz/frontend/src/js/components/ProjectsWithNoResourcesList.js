import Alpine from 'alpinejs'
import api, { tasksUrl } from '../utils/api'

function ProjecstWithNoResourcesList() {
    return {
        data: [],
        async init() {
            await this.getData()
        },
        async getData() {
            const json = await api.get('/api/projects/');

            await Promise.all(json.data.map(async project => {
                const tasks = await (await api.get(tasksUrl(project.id))).data.filter(task => !task.resource_id)

                tasks.length > 0 ? this.data.push({
                    id: project.id,
                    name: project.name,
                    tasks: tasks.map(task => ({
                        id: task.id,
                        name: task.intent,
                        content: task.content
                    }))
                }) : null
            }))
        },
    }
}

Alpine.data("ProjecstWithNoResourcesList", ProjecstWithNoResourcesList)
