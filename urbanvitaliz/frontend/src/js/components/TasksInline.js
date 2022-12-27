import Alpine from 'alpinejs'
import TaskApp from './Tasks'

function TasksInline(projectId) {

    const app = {}

    return TaskApp(app, projectId);
}

Alpine.data("TasksInline", TasksInline)
