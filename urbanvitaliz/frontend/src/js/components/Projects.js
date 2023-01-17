import Alpine from 'alpinejs'
import api from '../utils/api'
import { formatDate } from '../utils/date';

function AdvisorDashboard() {
    return {
        data: [],
        boards: [
            { code: 'TODO', title: 'À traiter', color_class: 'border-secondary' },
            { code: 'NOT_INTERESTED', title: "Pas d'intérêt", color_class: 'border-danger' },
            { code: "WIP", title: "En cours", color_class: 'border-primary' },
            { code: "DONE", title: "Traité", color_class: 'border-success' },
        ],
        init() {
            console.log('advisor dashboard ready');
        },
        async getData() {
            return this.data = await this.$store.projects.getProjects()
        },
        get isBusy() {
            return this.$store.app.isLoading
        },
        // View
        get view() {
            return this.data.filter(this.filterFn.bind(this)).sort(this.sortFn.bind(this));
        },
        column(status) {
            if (status instanceof Array) {
                return this.view.filter(d => status.indexOf(d.project.status) !== -1);
            } else {
                return this.view.filter(d => d.status === status);
            }
        },
        sortFn(a, b) {
            if (b.project.notifications.count - a.project.notifications.count)
                return b.project.notifications.count - a.project.notifications.count;
            else {
                return b.project.created_on - a.project.created_on;
            }
        },
        filterFn(d) {
            if (this.selectedDepartment && this.selectedDepartment !== "") {
                return d.commune && (d.commune.department.code == this.selectedDepartment)
            } else {
                return true
            }
        },
        // Drang n drop
        async onDrop(event, status) {
            event.preventDefault();

            this.currentlyHoveredElement.classList.remove('drag-target');
            this.currentlyHoveredElement = null;

            const id = event.dataTransfer.getData("text/plain");

            const data = this.data.find(d => d.id === JSON.parse(id));

            await api.patch(`/api/userprojectstatus/${data.id}/`, { status: status })

            await this.getData();
        },
        onDragStart(event, id) {
            event.dataTransfer.clearData();
            event.dataTransfer.effectAllowed = "move";
            event.dataTransfer.setData('text/plain', id)
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
        // utils
        formatDate,
    }
}

Alpine.data("AdvisorDashboard", AdvisorDashboard)
