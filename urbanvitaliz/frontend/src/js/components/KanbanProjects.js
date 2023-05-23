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
        regions: [],
        territorySelectAll: true,
        boards: [
            { code: 'TO_PROCESS', title: 'À traiter', color_class: 'border-secondary' },
            { code: 'READY', title: 'En attente', color_class: 'border-info' },
            { code: "IN_PROGRESS", title: "En cours", color_class: 'border-primary' },
            { code: "DONE", title: "Traité", color_class: 'border-success' },
            { code: "STUCK", title: "Conseil interrompu", color_class: 'border-dark' },
        ],
        async getData(postProcess = true) {
            const json = await api.get('/api/projects/');

            const data = json.data.map(d => Object.assign(d, {
                uuid: generateUUID()
            }));

            if (postProcess) {
                await this.postProcessData(data);
            }

            this.data = data
        },
        async onDrop(event, status, targetUuid) {
            event.preventDefault();

            this.currentlyHoveredElement.classList.remove('drag-target');
            this.currentlyHoveredElement = null;

            const uuid = event.dataTransfer.getData("application/uuid");
            const data = this.data.find(d => d.uuid === uuid);

            await api.patch(`/api/projects/${data.id}/`, { status: status })

            await this.getData(false);
        },
        findByUuid(uuid) {
            return this.data.find(d => d.uuid === uuid);
        },
        findById(id) {
            return this.data.find(d => d.id === id);
        },
        get view() {
            return this.data.filter(this.filterProjectsByDepartments.bind(this)).sort(this.sortFn.bind(this));
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
        async postProcessData(data) {
            const departments = this.extractAndCreateAdvisorDepartments(data)
            const regionsData = await api.get('/api/regions/');
            this.constructRegionsFilter(departments, regionsData.data)
        },
        extractAndCreateAdvisorDepartments(projects) {
            const departments = []

            projects.forEach(project => {

                const foundDepartment = departments.find(department => department.code === project?.commune?.department?.code)

                if (foundDepartment) return foundDepartment.nbProjects++;

                const deparmentItem = { ...project?.commune?.department, active: true, nbProjects: 1 }

                departments.push(deparmentItem)
            })

            return this.departments = departments.sort((a, b) => a.name.localeCompare(b.name));
        },
        constructRegionsFilter(departments, regions) {
            const currentRegions = []

            regions.forEach(region => {
                //Iterate through regions.departments and look for advisors departments
                const foundDepartments = departments.filter(
                    department => region.departments.find(
                        regionDepartment => regionDepartment.code === department.code))

                if (foundDepartments.length > 0) {
                    const currentRegion = {
                        code: region.code,
                        departments: foundDepartments,
                        name: region.name,
                        active: true
                    }

                    return currentRegions.push(currentRegion)
                }
            })

            return this.regions = currentRegions
        },
        handleTerritorySelectAll() {
            this.territorySelectAll = !this.territorySelectAll

            this.regions = this.regions.map(
                region => ({
                    ...region,
                    active: this.territorySelectAll,
                    departments: region.departments.map(
                        department => ({ ...department, active: this.territorySelectAll })
                    )
                })
            )
        },
        handleRegionFilter(selectedRegion) {
            this.regions = this.regions.map(
                region => {
                    if (region.code === selectedRegion.code) {
                        region.active = !region.active
                        region.departments = region.departments.map(department => ({ ...department, active: region.active }))
                    }

                    return region
                }
            )

            this.territorySelectAll = this.regions.filter(region => region.active).length === this.regions.length
        },
        handleDepartmentFilter(selectedDepartment) {
            this.regions = this.regions.map(
                region => ({
                    ...region,
                    departments: region.departments.map(
                        department => {
                            if (department.code === selectedDepartment.code) {
                                department.active = !department.active
                            }

                            return department
                        }
                    ),
                    active: region.departments.length === region.departments.filter(department => department.active).length
                })
            )

            this.territorySelectAll = this.regions.filter(region => region.active).length === this.regions.length
        },
        filterProjectsByDepartments(project) {
            return this.regions.find(
                region => region.departments.find(
                    department => department.code === project.commune.department.code)?.active)
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
