import Alpine from 'alpinejs'
import TaskApp from './Tasks'

function TasksInline(projectId) {

    const app = {
        init() {
            console.log('task inline initialization');
            console.log('project id task inline', projectId);
        }
    }

    return TaskApp(app, projectId);
}

Alpine.data("TasksInline", TasksInline)
