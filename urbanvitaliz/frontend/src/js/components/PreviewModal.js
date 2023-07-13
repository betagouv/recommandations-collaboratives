import Alpine from 'alpinejs'
import { resourcePreviewUrl } from '../utils/api'
import { renderMarkdown } from '../utils/markdown'
import { formatDate } from '../utils/date';
import {gravatar_url} from '../utils/gravatar'
import { isStatusUpdate, statusText } from "../utils/taskStatus"

export default function PreviewModal() {
    return {
        currentTaskNotifications: [],
        get index() {
            return this.$store.previewModal.index
        },
        get taskId() {
            return this.$store.previewModal.taskId
        },
        get task() {
            return this.$store.tasksData.getTaskById(this.taskId)
        },
        get followups() {
            return this.$store.previewModal.followups
        },
        get newTasks() {
            return this.$store.previewModal.newTasks
        },
        async refresh() {
            this.followupScrollToLastMessage();
        },
        resourcePreviewUrl,
        renderMarkdown,
        formatDate,
        gravatar_url,
        isStatusUpdate,
        statusText,
        newTasksNavigationText() {
            return `${this.index + 1} sur ${this.newTasks.length} recommandation${this.newTasks.length > 0 ? 's' : ''}`
        },
        hasNotification(followupId) {
            return this.currentTaskNotifications.filter(n => n.action_object.who && n.action_object.id === followupId).length > 0;
        },
        
        //TODO use TaskComment()
    }
}

Alpine.data("PreviewModal", PreviewModal)
