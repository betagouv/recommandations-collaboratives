import Alpine from 'alpinejs'

function AdvisorDashboard() {
    return {
        data: [],
        title:"qsdqsd",
        boards:[
            { code: 'TO_PROCESS', title: 'À traiter', color_class: 'border-secondary' },
            { code: 'READY', title: 'En attente', color_class: 'border-info' },
            { code: "IN_PROGRESS", title: "En cours", color_class: 'border-primary' },
            { code: "DONE", title: "Traité", color_class: 'border-success' },
        ],
        init() {
            console.log('advisor dashboard ready');
        },
        async getData() {
            return this.data = await this.$store.projects.getProjects()
        },
        get isBusy() {
            console.log('this data : ', this.data);
            console.log('this boards : ', this.boards);
            console.log(this.$store.app.isLoading);
            return this.$store.app.isLoading
        },
        // View
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
        }
    }
}

Alpine.data("AdvisorDashboard", AdvisorDashboard)
