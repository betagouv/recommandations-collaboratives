import Alpine from 'alpinejs'
import api from '../utils/api'
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
        currentSort: this.sortProjectDate,
        search: '',
        select: '',
        //departments
        departments: [],
        // map
        map: null,
        mapIsWide: false,
        markersLayer: "",
        //options
        bodyScrollTopPadding: 215,
        init() {
            this.handleBodyTopPaddingScroll(this.bodyScrollTopPadding);
        },
        async getData() {

            const projects = await this.$store.projects.getProjects()

            this.nbNewProjects = projects.filter(p => p.status === 'NEW').length
            this.extractAndCreateAdvisorDepartments(projects);

            this.data = projects.map(project => ({...project, isLoading:false}))
            this.displayedData = this.data.sort(this.sortProjectDate)

            const { map, markersLayer } = initMap(projects)

            this.map = map
            this.markersLayer = markersLayer

            if (projects.length > 0) {
                zoomToCentroid(this.map, this.markersLayer);
            } else {
                setTimeout(() => this.map.invalidateSize(), 251)
            }
        },
        get isBusy() {
            return this.$store.app.isLoading
        },
        extractAndCreateAdvisorDepartments(projects) {
            const departments = []

            projects.forEach(item => {

                const foundDepartment = departments.find(department => department.code === item.project?.commune?.department?.code)

                if (foundDepartment) return foundDepartment.nbProjects++;

                const deparmentItem = { ...item.project?.commune?.department, active: true, nbProjects: 1 }

                departments.push(deparmentItem)
            })

            return this.departments = departments;
        },
        handleProjectsSearch(event) {

            if (this.search === "") {
                return this.filterProjectsByDepartments().sort(this.currentSort);
            }

            const newProjectList = this.displayedData.filter(item => {
                if (item.project.name?.toLowerCase().includes(this.search.toLowerCase())) return item
                if (item.project.commune?.name?.toLowerCase().includes(event.target.value.toLowerCase())) return item
                if (item.project.commune.insee.includes(event.target.value)) return item
                if (item.project.id.toString().includes(event.target.value) && event.target.value.length < 4) return item
            })

            return this.displayedData = newProjectList.sort(this.currentSort)
        },
        handleTerritoryFilter(event) {

            this.departments = this.departments.map(department => {
                if (department.code === event.target.value) {
                    department.active = event.target.checked
                }

                return department
            })

            return this.filterProjectsByDepartments().sort(this.currentSort);
        },
        filterProjectsByDepartments() {
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

            this.currentSort = sortCriterion

            return this.displayedData = this.displayedData.sort(sortCriterion)
        },
        sortProjectCommuneName(a, b) {
            if (a.project?.commune?.name < b.project?.commune?.name) {
                return -1
            } else if (a.project?.commune?.name > b.project?.commune?.name) {
                return 1
            } else return 0
        },
        sortProjectDate(a, b) {
            if (new Date(a.project?.created_on) > new Date(b.project?.created_on)) {
                return -1
            } else if (new Date(a.project?.created_on) < new Date(b.project?.created_on)) {
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
            //450 -> header + map.height
            //todo calculate it

            setTimeout(() => this.map.invalidateSize(), 251)
            setTimeout(() => zoomToCentroid(this.map, this.markersLayer), 251)

            this.mapIsWide = !this.mapIsWide

            this.handleBodyTopPaddingScroll(this.mapIsWide ? 455 : 215)
        },
        handleBodyTopPaddingScroll(height) {
            this.bodyScrollTopPadding = height
            window.document.body.style.scrollPaddingTop = `${this.bodyScrollTopPadding}px`;
            window.document.documentElement.style.scrollPaddingTop = `${this.bodyScrollTopPadding}px`;
        },
        async handlePositioningAction(url, id) {

            const projectUpdated = this.displayedData.find(item => item.project.id === id)
            this.open = false;

            try {
                projectUpdated.isLoading = true

                await api.post(url.replace('0', id))
                const updatedProjects = await this.$store.projects.getProjects()

                const updatedProject = updatedProjects.find(({project}) => project.id === id)
                this.displayedData = this.displayedData.map(item => item.project.id === id ? updatedProject : item)

                projectUpdated.isLoading = false

            } catch (err) {
                console.error('Something went wrong : ', err)
                this.errors = err;
                projectUpdated.isLoading = false
            }
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
    const markersLayer = createMarkersLayer(map, markers)

    return { map, markersLayer }
}

//Create a layer in order to zoom-in at the center of each markers
function createMarkersLayer(map, markers) {
    const markersLayer = new L.FeatureGroup();
    markers.forEach(marker => markersLayer.addLayer(marker))
    markersLayer.addTo(map);

    return markersLayer
}

function zoomToCentroid(map, markersLayer) {
    return map.fitBounds(markersLayer.getBounds());
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

export function makeProjectPositioningActionURL(url, id) {
    return url.replace('0', id);
}

Alpine.data("PersonalAdvisorDashboard", PersonalAdvisorDashboard)
