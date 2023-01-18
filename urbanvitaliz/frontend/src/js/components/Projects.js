import Alpine from 'alpinejs'
import api from '../utils/api'
import { formatDate } from '../utils/date';
import { gravatar_url } from '../utils/gravatar';
import { makeProjectURL } from '../utils/createProjectUrl'

function AdvisorDashboard() {
    return {
        data: [],
        totalNotifications: 0,
        nbNewProjects: 0,
        gravatar_url,
        formatDate,
        makeProjectURL,
        boards: [
            { code: ['TODO', 'NEW'], title: 'À traiter', color_class: 'border-secondary', color: '#0063CB' },
            { code: 'WIP', title: "En cours", color_class: 'border-primary', color: '#FCC63A' },
            { code: "DONE", title: "Traité", color_class: 'border-success', color: '#F6F6F6' },
            { code: 'NOT_INTERESTED', title: "Dossier que je ne suis pas", color_class: 'border-danger', color: '#CE0500' },
        ],
        async getData() {

            const projects = await this.$store.projects.getProjects()

            this.totalNotifications = 0
            this.nbNewProjects = 0

            projects.forEach(p => this.totalNotifications += p.project.notifications.count)
            projects.forEach(p => {
                if (p.status === 'NEW') return this.nbNewProjects += 1
            })

            return this.data = projects
        },
        get isBusy() {
            return this.$store.app.isLoading
        },
        // View
        get view() {
            return this.data.filter(this.filterFn.bind(this)).sort(this.sortFn.bind(this)).sort(this.sortStatusFn.bind(this));
        },
        column(status) {
            if (status instanceof Array) {
                return this.view.filter(d => status.indexOf(d.status) !== -1);
            } else {
                return this.view.filter(d => d.status === status);
            }
        },
        sortStatusFn(a, b) {
            if (a.status === 'NEW') {
                return -1
            } else if (b.status === 'NEW') {
                return 1
            } else return 0
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
        getProjectRoleColor(project) {
            if (project.is_observer) return '#27A658'
            else if (project.is_switchtender) return '#0063CB'
            else return ''
        },
        // Drag n drop
        async onDrop(event, status) {

            if (status instanceof Array) status = status[0]

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
    }
}

Alpine.data("AdvisorDashboard", AdvisorDashboard)
