import Alpine from 'alpinejs'
import TaskApp from './Tasks'
import { STATUSES } from '../config/statuses';

function TasksInline(projectId) {

    const app = {
        filterIsDraft: false,
        boardsFiltered: [],
        boards: [
            { status: [STATUSES.PROPOSED], title: "Nouvelles", color_class: "border-error", color: "#0d6efd" },
        ],
        filterFn(d) {
            return this.canAdministrate || d.public || !d.public;
        },
        init() {
            this.boardsFiltered = this.boards
        },
        async handleDraftFilterChange() {

            this.filterIsDraft = !this.filterIsDraft

            await this.getData();

            this.updateView()
        },
        async publishTask(taskId) {
            await this.patchTask(taskId, { public: true });
            await this.getData();
            this.updateView()
        },
        //Custom behaviour
        onPreviewClick(id) {
            this.currentTaskId = id;
            this.openPreviewModal();
            this.filterIsDraft = false
        },
        updateView() {
            if (!this.filterIsDraft) return
            
            return this.data = this.data.filter((d) => d.public == !this.filterIsDraft);
        }
    }

    return TaskApp(app, projectId);
}

Alpine.data("TasksInline", TasksInline)
