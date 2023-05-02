import Alpine from 'alpinejs'
import { formatDate } from '../utils/date';
import { gravatar_url } from '../utils/gravatar';
import { makeProjectURL } from '../utils/createProjectUrl'

import * as L from 'leaflet';
import 'leaflet-control-geocoder';
import 'leaflet-providers'
import 'leaflet/dist/leaflet.css'
import 'leaflet-control-geocoder/dist/Control.Geocoder.css'

function PersonalAdvisorDashboard() {
    return {
        data: [],
        displayedData: [],
        nbNewProjects: 0,
        errors: null,
        formatDate,
        gravatar_url,
        makeProjectURL,
        // filters
        search: '',
        select:'',
        //departments
        departments:[],
        async getData() {

            const projects = await this.$store.projects.getProjects()

            this.nbNewProjects = projects.filter(p =>  p.status === 'NEW').length
            this.extractAndCreateAdvisorDepartments(projects);

            this.data = projects
            this.displayedData = this.data.sort(this.sortProjectStatus);

            const Map = initMap(projects);

            //Center Map
            // TODO center in middle of all projects
            Map.panTo(new L.LatLng(46.51, 1.20));
            Map.zoomIn()
        },
        get isBusy() {
            return this.$store.app.isLoading
        },
        extractAndCreateAdvisorDepartments(projects) {
            const departments = []

            projects.forEach(item => {
                //If the department code is already in our deparments array
                if (departments.findIndex(department => department.code === item.project?.commune?.department?.code) != -1) return

                departments.push(item.project?.commune?.department)
            })

            this.departments = departments;
        },
        handleProjectsSearch(event) {

            if (this.search === "") return this.displayedData = this.data
            
            const newProjectList = this.data.filter(item => {
                if (item.project?.name?.toLowerCase().includes(this.search.toLowerCase())) return item
                if (item.project?.commune?.name?.toLowerCase().includes(event.target.value.toLowerCase())) return item
            })

            this.displayedData = newProjectList
        },
        handleProjectsSelect(event){
            switch(event.target.value) {
                case "commune-name":
                    return this.displayedData = this.data.sort(this.sortProjectCommuneName)
                case "date":
                    return this.displayedData = this.data.sort(this.sortProjectDate)
                case "insee":
                    return this.displayedData = this.data.sort(this.sortProjectInsee)
                default:
                    return this.displayedData = this.data.sort(this.sortProjectStatus)
            }
        },
        sortProjectCommuneName(a, b){
            if (a.project?.commune?.name < b.project?.commune?.name) {
                return -1
            } else if (a.project?.commune?.name > b.project?.commune?.name) {
                return 1
            } else return 0
        },
        sortProjectDate(a, b){
            if (new Date(a.project?.created_on) < new Date(b.project?.created_on)) {
                return -1
            } else if (new Date(a.project?.created_on) > new Date(b.project?.created_on)) {
                return 1
            } else return 0
        },
        sortProjectInsee(a, b){
            if (a.project?.commune?.insee < b.project?.commune?.insee) {
                return -1
            } else if (a.project?.commune?.insee > b.project?.commune?.insee) {
                return 1
            } else return 0
        },
        sortProjectStatus(a, b) {
            if (a.status === 'NEW') {
                return -1
            } else if (b.status === 'NEW') {
                return 1
            } else return 0
        }
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
            L.marker([item.project.commune.latitude, item.project.commune.longitude], { icon: createMarkerIcon(item) }).addTo(map)
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
