import Alpine from 'alpinejs'
import api from '../utils/api'
import { formatDate } from '../utils/date';
import { gravatar_url } from '../utils/gravatar';
import { makeProjectURL } from '../utils/createProjectUrl'
import { roles } from '../config/roles';
import List from 'list.js'

// A custom dashboard made for switctenders
// Expose a list of projects
// Filtered by a board.code 
// Drag n drops utils added
// TODO exctract drag n drop logics

function PersonalAdvisorDashboard() {
    return {
        data: [],
        totalNotifications: 0,
        nbNewProjects: 0,
        errors: null,
        formatDate,
        gravatar_url,
        makeProjectURL,
        init() {
            const options = {
                valueNames: ['name', 'location']
            };

            console.log(new List('projectsList', options));
        },
        async getData() {

            const projects = await this.$store.projects.getProjects()

            this.totalNotifications = 0
            this.nbNewProjects = 0

            projects.forEach(p => this.totalNotifications += p.project.notifications.count)
            projects.forEach(p => {
                if (p.status === 'NEW') return this.nbNewProjects += 1
            })

            this.data = projects
        },
        get isBusy() {
            return this.$store.app.isLoading
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
            if (project.is_observer) return roles.observer.color
            else if (project.is_switchtender) return roles.switchtender.color
            else return ''
        },
    }
}

Alpine.data("PersonalAdvisorDashboard", PersonalAdvisorDashboard)
