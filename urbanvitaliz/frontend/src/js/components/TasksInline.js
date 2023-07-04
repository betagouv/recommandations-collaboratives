import Alpine from 'alpinejs'
import TaskApp from './Tasks'
import { TASK_STATUSES } from '../config/statuses';

export default function TasksInline(projectId) {

    const app = {
        filterIsDraft: false,
        boardsFiltered: [],
        boards: [
            { status: [TASK_STATUSES.PROPOSED,TASK_STATUSES.INPROGRESS,TASK_STATUSES.BLOCKED,TASK_STATUSES.DONE,TASK_STATUSES.NOT_INTERESTED,TASK_STATUSES.ALREADY_DONE], title: "Nouvelles", color_class: "border-error", color: "#0d6efd" },
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
            await this.$store.tasksData.patchTask(taskId, { public: true });
            await this.$store.tasksData.getTasks();
            // this.updateView()
        },
        //Custom behaviour
        // onPreviewClick(id) {
        //     this.currentTaskId = id;
        //     this.openPreviewModal();
        //     this.filterIsDraft = false
        // },
        updateView() {
            if (!this.filterIsDraft) return
            
            return this.data = this.data.filter((d) => d.public == !this.filterIsDraft);
        }
    }

    return TaskApp(app, projectId);
}

Alpine.data("TasksInline", TasksInline)
