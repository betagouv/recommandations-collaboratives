import { TASK_STATUSES } from '../config/statuses';

import { isArchivedStatus } from "../utils/taskStatus"


export default function TasksApp(app) {
    const taskApp = {
        //utils function
        currentlyHoveredElement: null,
        canAdministrate: false,
        canUseTasks: false,
        canManageTasks: false,
        isSwitchtender: false,
        userEmail: null,
        isArchivedStatus,
        data: [],
        boards: [],
        STATUSES: TASK_STATUSES,
        get isBusy() {
            return this.$store.app.isLoading
        },
        sortFn(a, b) {
            return a.order - b.order;
        },
        filterFn(d) {
            return this.isSwitchtender ? true : (this.canAdministrate || d.public);
        },
        findByUuid(uuid) {
            return this.$store.tasksView.displayedTasks.find(d => d.uuid === uuid);
        },
        findById(id) {
            return this.$store.tasksView.displayedTasks.find(d => d.id === id);
        },
        get view() {
            const result = this.$store.tasksView.displayedTasks.filter((d) => this.filterFn(d)).sort((a, b) => this.sortFn(a, b));
            return result;
        },
        column(status) {
            if (status instanceof Array) {
                return this.view.filter(d => status.indexOf(d.status) !== -1);
            } else {
                return this.view.filter(d => d.status === status);
            }
        },
        // Administrate
        loadCanAdministrate() {
            const canAdministrate = document.getElementById("canAdministrate").textContent;
            this.canAdministrate = JSON.parse(canAdministrate);
        },
        loadUserProjectPerms() {
            const userProjectPerms = document.getElementById("userProjectPerms").textContent;
            this.$store.tasksData.canUseTasks = (userProjectPerms.indexOf("use_tasks") > -1);
            this.$store.tasksData.canManageTasks = (userProjectPerms.indexOf("manage_tasks") > -1);
        },
        loadIsSwitchtender() {
            const isSwitchtender = document.getElementById("isSwitchtender").textContent;
            this.isSwitchtender = JSON.parse(isSwitchtender);
        },

        // UserId
        loadUserId() {
            const userEmail = document.getElementById("userEmail").textContent;
            this.userEmail = JSON.parse(userEmail);
        },

        // Tooltips
        initTooltips() {
            new bootstrap.Tooltip(this.$el, {
                selector: "[data-bs-toggle='tooltip']"
            })
        },
        handleOpenFeedbackModal(task) {
            console.log('dispatch somthg', task);
            console.log(this.$dispatch('open-feedback-modal', task))
        },
    };

    return Object.assign(taskApp, app);
}
