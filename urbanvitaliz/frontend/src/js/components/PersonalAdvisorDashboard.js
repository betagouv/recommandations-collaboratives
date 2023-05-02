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
        select: '',
        //departments
        departments: [],
        // map
        map: null,
        mapIsWide: false,
        //options
        bodyScrollTopPadding: 215,
        init() {
            this.handleBodyTopPaddingScroll(this.bodyScrollTopPadding);
        },
        async getData() {

            const projects = await this.$store.projects.getProjects()

            this.nbNewProjects = projects.filter(p => p.status === 'NEW').length
            this.extractAndCreateAdvisorDepartments(projects);

            this.data = projects
            this.displayedData = this.data.sort(this.sortProjectStatus);

            this.map = initMap(projects);
        },
        get isBusy() {
            return this.$store.app.isLoading
        },
        extractAndCreateAdvisorDepartments(projects) {
            const departments = []

            projects.forEach(item => {
                //If the department code is already in our deparments array
                if (departments.findIndex(department => department.code === item.project?.commune?.department?.code) != -1) return

                const deparmentItem = { ...item.project?.commune?.department, active: true }

                departments.push(deparmentItem)
            })

            return this.departments = departments;
        },
        handleProjectsSearch(event) {

            if (this.search === "") {
                return this.displayedData = this.data
            }

            const newProjectList = this.data.filter(item => {
                if (item.project?.name?.toLowerCase().includes(this.search.toLowerCase())) return item
                if (item.project?.commune?.name?.toLowerCase().includes(event.target.value.toLowerCase())) return item
            })

            return this.displayedData = newProjectList
        },
        handleTerritoryFilter(event) {

            this.departments = this.departments.map(department => {
                if (department.code === event.target.value) {
                    department.active = event.target.checked
                }

                return department
            })

            //find department item from departments for each project and return if the department is active
            return this.displayedData = this.data.filter(item => this.departments.find(department => department.code === item.project.commune.department.code).active)
        },
        handleProjectsSelect(event) {

            let sortCriterion;

            switch (event.target.value) {
                case "commune-name":
                    sortCriterion = this.sortProjectCommuneName
                    break;
                case "date":
                    sortCriterion = this.sortProjectDate
                    break;
                case "insee":
                    sortCriterion = this.sortProjectInsee
                    break;
                default:
                    sortCriterion = this.sortProjectStatus
                    break;
            }

            return this.displayedData = this.data.sort(sortCriterion)
        },
        sortProjectCommuneName(a, b) {
            if (a.project?.commune?.name < b.project?.commune?.name) {
                return -1
            } else if (a.project?.commune?.name > b.project?.commune?.name) {
                return 1
            } else return 0
        },
        sortProjectDate(a, b) {
            if (new Date(a.project?.created_on) < new Date(b.project?.created_on)) {
                return -1
            } else if (new Date(a.project?.created_on) > new Date(b.project?.created_on)) {
                return 1
            } else return 0
        },
        sortProjectInsee(a, b) {
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
        },
        handleMapOpen() {
            //resize map
            //rezoom to centroide
            //450 -> header + map.height
            //todo calculate it
            this.handleBodyTopPaddingScroll(455)
            this.map()
            return this.mapIsWide = !this.mapIsWide
        },
        handleBodyTopPaddingScroll(height) {
            this.bodyScrollTopPadding = height
            window.document.body.style.scrollPaddingTop = `${this.bodyScrollTopPadding}px`;
            window.document.documentElement.style.scrollPaddingTop = `${this.bodyScrollTopPadding}px`;
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

    const markers = createMapMarkers(map, projects)

    var markersLayer = new L.FeatureGroup();

    //Create a layer in order to zoom-in at the center of each markers
    markers.forEach(marker => markersLayer.addLayer(marker))
    markersLayer.addTo(map);
    map.fitBounds(markersLayer.getBounds());

    return map
}

// Crete layers composed with markers
function createMapMarkers(map, projects) {
    return projects.map((item) => {
        if (item.project?.commune?.latitude && item.project?.commune?.longitude) {
            return L.marker([item.project.commune.latitude, item.project.commune.longitude], { icon: createMarkerIcon(item) }).addTo(map)
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
