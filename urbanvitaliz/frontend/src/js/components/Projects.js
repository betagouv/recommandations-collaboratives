import Alpine from 'alpinejs'

// USERPROJECT_STATES = (
//     ("TODO", "A traiter"),
//     ("WIP", "En cours"),
//     ("DONE", "Traité"),
//     ("NOT_INTERESTED", "Pas d'intérêt"),
// )

function AdvisorDashboard() {
    return {
        data: [],
        title:"qsdqsd",
        boards:[
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
        }
    }
}

Alpine.data("AdvisorDashboard", AdvisorDashboard)
