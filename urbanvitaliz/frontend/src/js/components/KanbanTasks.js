import Alpine from "alpinejs"
import TaskApp from './Tasks'

import { STATUSES } from '../store/tasks'
import api, { taskUrl, editTaskUrl, deleteTaskReminderUrl, followupUrl, followupsUrl, moveTaskUrl, markTaskNotificationsAsReadUrl, taskNotificationsUrl } from '../utils/api'
import { formatReminderDate, daysFromNow, formatDate } from '../utils/date'
import { isStatusUpdate, statusText } from "../utils/taskStatus"
import { toArchiveTooltip, reminderTooltip } from '../utils/tooltip'
import { renderMarkdown } from '../utils/markdown'
import { generateGravatarUrl } from '../utils/gravatar'

Alpine.data("KanbanTasks", boardTasksApp)

function boardTasksApp(projectId) {

    const app = {
        init() {
            console.log('kanban init');
        },  
        onDragStart(event, uuid) {
            event.dataTransfer.clearData();
            event.dataTransfer.effectAllowed = "move";
            event.dataTransfer.setData('application/uuid', uuid);
            event.target.classList.add('drag-dragging');
            document.querySelectorAll(".drop-column").forEach(e => e.classList.add("drop-highlight"));
        },
        onDragEnd(event) {
            event.target.classList.remove('drag-dragging');
            document.querySelectorAll(".drop-column").forEach(e => e.classList.remove("drop-highlight"));
        },
        onDragEnter(event) {
            if (this.currentlyHoveredElement && this.currentlyHoveredElement !== event.currentTarget) {
                this.currentlyHoveredElement.classList.remove('drag-target');
            }
            this.currentlyHoveredElement = event.currentTarget;
            event.currentTarget.classList.add('drag-target');
        },
        onDragLeave(event) {
            if (event.target === this.currentlyHoveredElement) {
                event.target.classList.remove('drag-target');
            }
        },
        onDragOver(event) {
            event.preventDefault();
            event.dataTransfer.dropEffect = "move";
        },
        async onDrop(event, status, targetUuid) {
            event.preventDefault();

            this.currentlyHoveredElement.classList.remove('drag-target');
            this.currentlyHoveredElement = null;

            const uuid = event.dataTransfer.getData("application/uuid");

            const data = this.data.find(d => d.uuid === uuid);
            const nextData = this.data.find(d => d.uuid === targetUuid);

            if (status instanceof Array) {
                if (this.isArchivedStatus(data.status) && nextData) {
                    await moveTask(data.id, nextData.id);
                } else {
                    this.openFeedbackModal(data);
                }
            } else {
                await this.issueFollowup(data, status);
                if (nextData) await moveTask(data.id, nextData.id);
            }

            await this.getData();
        },
    }

    return TaskApp(app, projectId)
}
