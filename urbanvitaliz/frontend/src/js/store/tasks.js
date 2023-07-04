import Alpine from 'alpinejs'
import api, { tasksUrl, taskUrl, moveTaskUrl, followupsUrl, taskNotificationsUrl, markTaskNotificationsAsReadUrl } from '../utils/api'
import { generateUUID } from '../utils/uuid'

document.addEventListener('alpine:init', () => {

    Alpine.store('tasksView', {
        currentView: 'kanban',
        init() {
            console.log('tasks view store init ');
        },
        switchView() {
            this.currentView === 'inline' ? this.currentView = 'kanban' : this.currentView = 'inline'
        },
    })

    Alpine.store('taskModal', {
        currentTask: null,

        previewModalHandle: null,
        deleteModalHandle: null,
        feedbackModalHandle: null,

        onPreviewClick(task) {
            this.currentTask = task
            console.log('preview click ? ', this.currentTask);
            this.previewModalHandle.show();
        },
        onDeleteClick(task) {
            this.currentTask = task
            console.log('delete task ', this.currentTask);
            this.deleteModalHandle.show();
        },
        onFeedbackClick(task) {
            this.currentTask = task
            console.log('delete task ', this.currentTask);
            this.feedbackModalHandle.show();
        }
    })
})

export default Alpine.store('tasksView')
