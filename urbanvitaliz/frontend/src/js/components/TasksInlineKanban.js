import Alpine from 'alpinejs'

//Global task component parent
import '../components/Tasks'
//Task inline child component
import TasksInline from './TasksInline'
//Task kanban child component
import TasksKanban from './TasksKanban'
import TasksApp from './Tasks'

Alpine.data("TasksInlineKanban", TasksInlineKanban)

const views = {
    inline: {
        name: "Thématique"
    },
    kanban: {
        name: "Status d'avancement"
    }
}

function TasksInlineKanban(projectId) {
    const tasksInlineKanban = {
        currentView: 'inline',
        async init() {
            console.log('task inline kanban ready');
            await this.getData(projectId);
        },
        handleSwitchView(view) {
            if (view !== this.currentView) {
                this.currentView = view
                handleSwitchViewComponent(view)
            }
        }
    }

    function handleSwitchViewComponent(view) {
           console.log('view :', view)

           const viewComponent = view === 'inline' ? TasksInline(projectId) : TasksKanban(projectId)
           console.log('view component : ', viewComponent);

           const app = Object.assign(viewComponent, tasksInlineKanban)

           console.log('app' , app);

           return app
    }

    // const TasksInlineComponent = TasksInline(projectId)
    // const TasksKanbanComponent = TasksKanban(projectId)

    // console.log('tasksinline app', TasksInline)

    // console.log('tasksinline comp', TasksInlineComponent)
    // console.log('taskskanban comp', TasksKanbanComponent)

    // console.log(tasksInlineKanban.currentView)
    // const app = Object.assign(TasksInlineComponent, tasksInlineKanban)

    return handleSwitchViewComponent(tasksInlineKanban.currentView)
}
