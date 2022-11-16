import Alpine from 'alpinejs'
import { generateUUID } from '../utils/uuid'

import api from '../utils/api'

Alpine.data("KanbanProjects", boardProjectsApp)

function boardProjectsApp() {
    const app = {
        data: [],
        get isBusy() {
            return this.$store.app.isLoading
        },
        selectedDepartment: null,
        departments: [],
        boards: [
            { code: 'TO_PROCESS', title: 'A traiter', color_class: 'border-secondary' },
            { code: 'READY', title: 'En attente', color_class: 'border-info' },
            { code: "IN_PROGRESS", title: "En cours", color_class: 'border-primary' },
            { code: "DONE", title: "Traité", color_class: 'border-success' },
            { code: "STUCK", title: "Conseil interrompu", color_class: 'border-dark' },
        ],
        async getData() {
            const json = await api.get('/api/projects/');

            const data = json.data.map(d => Object.assign(d, {
                uuid: generateUUID()
            }));

            this.data = data
        },
        async onDrop(event, status, targetUuid) {
            event.preventDefault();

            this.currentlyHoveredElement.classList.remove('drag-target');
            this.currentlyHoveredElement = null;

            const uuid = event.dataTransfer.getData("application/uuid");
            const data = this.data.find(d => d.uuid === uuid);

            await api.patch(`/api/projects/${data.id}/`, { status: status })

            await this.getData();
        },
        findByUuid(uuid) {
            return this.data.find(d => d.uuid === uuid);
        },
        findById(id) {
            return this.data.find(d => d.id === id);
        },
        get view() {
            return this.data.filter(this.filterFn.bind(this)).sort(this.sortFn.bind(this));
        },
        column(status) {
            if (status instanceof Array) {
                return this.view.filter(d => status.indexOf(d.status) !== -1);
            } else {
                return this.view.filter(d => d.status === status);
            }
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
        postProcessData(data) {
            const departments = [];
            data.forEach(d => {
                if (d.commune != null) {
                    const dept = {
                        code: d.commune.department.code,
                        name: d.commune.department.name,
                    };
                    const index = departments.findIndex(obj => obj.code == dept.code);
                    if (index === -1) {
                        departments.push(dept);
                    }
                }
            });
            departments.sort((a, b) => a.name.localeCompare(b.name));
            this.departments = departments;
        },

        sortFn(a, b) {
            if (b.notifications.count - a.notifications.count)
                return b.notifications.count - a.notifications.count;
            else {
                return b.created_on - a.created_on;
            }
        },
        filterFn(d) {
            if (this.selectedDepartment && this.selectedDepartment !== "") {
                return d.commune && (d.commune.department.code == this.selectedDepartment)
            } else {
                return true
            }
        },
        truncate(input, size = 30) {
            return input.length > size ? `${input.substring(0, size)}...` : input;
        },
        formatDateDisplay(date) {
            return new Date(date).toLocaleDateString('fr-FR');
        }
    }

    return app
}
