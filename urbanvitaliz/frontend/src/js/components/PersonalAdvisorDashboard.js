import Alpine from 'alpinejs'
import api from '../utils/api'
import { formatDate } from '../utils/date';
import { gravatar_url } from '../utils/gravatar';
import { makeProjectURL } from '../utils/createProjectUrl'
import { roles } from '../config/roles';
import List from 'list.js'

import * as L from 'leaflet';
import 'leaflet-control-geocoder';
import 'leaflet-providers'

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

            const Map = initMap(projects);

            console.log('big map', Map);

            //Center Map
            Map.panTo(new L.LatLng(46.51, 1.20));
            Map.zoomIn()
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

// Map base layer 
function initMap(projects) {
    L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
        maxZoom: 20,
        attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });

    const map = L.map('map').setView([48.51, 10.20], 2);

    L.tileLayer.provider('OpenStreetMap.France').addTo(map);

    initMapLayers(map, projects)

    return map
}

// Crete layers composed with markers
function initMapLayers(map, projects) {
    projects.forEach((item) => {
        if (item.project?.commune?.latitude && item.project?.commune?.longitude) {
            L.marker([item.project.commune.latitude, item.project.commune.longitude],{ icon: createMarkerIcon(item) }).addTo(map)
        }
    })
}

function createMarkerIcon(item) {
    return L.divIcon({ 
        className: `map-marker ${item.status === "NEW" ? 'project-marker new-project-marker' : 'project-marker'}`,
        html: `<a href="#project-${item.project.id}">${item.project.id}</a>`
    });
}

Alpine.data("PersonalAdvisorDashboard", PersonalAdvisorDashboard)
