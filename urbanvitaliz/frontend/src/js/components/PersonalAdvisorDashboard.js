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
        territorySelectAll: true,
        // map
        map: null,
        mapIsSmall: false,
        markersLayer: "",
        //options
        //header's height + some px
        bodyScrollTopPadding: 80,
        init() {
            this.handleBodyTopPaddingScroll(this.bodyScrollTopPadding);
        },
        async getData(currentUser) {

            const projects = await this.$store.projects.getProjects()

            this.nbNewProjects = projects.filter(p => p.status === 'NEW').length

            this.extractAndCreateAdvisorDepartments(projects);
            this.data = projects.map(project => ({ ...project, isLoading: false }))
            this.data = this.createProjectListWithNewActivities(projects);

            this.displayedData = this.data.sort(this.sortProjectDate)
            const { map, markersLayer } = initMap(projects)

            this.map = map
            this.markersLayer = markersLayer

            if (projects.length > 0) {
                zoomToCentroid(this.map, this.markersLayer);
            } else {
                setTimeout(() => this.map.invalidateSize(), 251)
            }

            const sameUser = this.isSameUser(currentUser)

            if (sameUser) {
                return this.checkCurrentState();
            } else {
                //Changing current user and re-init current state
                this.removeStateFromStore('departments')
                this.removeStateFromStore('sort')
                this.removeStateFromStore('search')
                this.addCurrentStateToStore('currentUser', currentUser)
            }
        },
        checkCurrentState() {

            const currentSort = this.readCurrentStateFromStore('sort')
            const currentDepartments = this.readCurrentStateFromStore('departments')

            if (currentSort) {
                this.select = JSON.parse(currentSort)
                this.currentSort = this.getCurrentSortFn(this.select)
            }

            if (currentDepartments) {
                this.departments = JSON.parse(currentDepartments)
            }

            //If we can't find an active department in state 
            // then uncheck select all departments in filter
            if (this.departments.findIndex(department => department.active) === -1) {
                this.territorySelectAll = false
            }

            return this.displayedData = this.filterProjectsByDepartments(this.data).sort(this.currentSort);
        },
        isSameUser(currentUser) {

            const previousUser = this.readCurrentStateFromStore('currentUser')

            if (!previousUser) {
                this.addCurrentStateToStore('currentUser', currentUser)
            }

            return (JSON.parse(previousUser) == currentUser)
        },
        get isBusy() {
            return this.$store.app.isLoading
        },
        getProjectStatusClass(item) {
            if (item.project.inactive_since !== null) {
                return 'inactive'
            }
        },
        getProjectStatusColor(item) {
            if (item.status === "NEW") {
                return 'text-new-project'
            } else if (item.project.inactive_since) {
                return 'text-inactive'
            } else if (item.project.is_switchtender && !item.project.is_observer) {
                return 'text-green'
            } else if (item.project.is_observer && item.project.is_switchtender) {
                return 'text-blue'
            }
        },
        getNewRecommendations(item) {
            const newRecommendations = item.project.notifications.new_recommendations

            if (newRecommendations > 1) {
                return `(${newRecommendations} nouvelles)`
            } else if (newRecommendations === 1) {
                return `(${newRecommendations} nouvelle)`
            }

            return null
        },
        getUnreadPublicMessages(item) {

            const unreadPublicMessages = item.project.notifications.unread_public_messages

            if (unreadPublicMessages > 1) {
                return `(${unreadPublicMessages} nouveaux)`
            } else if (unreadPublicMessages === 1) {
                return `(${unreadPublicMessages} nouveau)`
            }

            return null
        },
        getUnreadPrivateMessages(item) {
            const unreadPrivateMessages = item.project.notifications.unread_private_messages

            if (unreadPrivateMessages > 1) {
                return `(${unreadPrivateMessages} nouveaux)`
            } else if (unreadPrivateMessages === 1) {
                return `(${unreadPrivateMessages} nouveau)`
            }

            return null
        },
        createProjectListWithNewActivities(projects) {
            const projectsWithNewActivities = projects.map(item => {

                let newActivities = 0;

                if (item.project.is_observer || item.project.is_switchtender) {
                    newActivities = item.project.notifications.new_recommendations + item.project.notifications.unread_private_messages + item.project.notifications.unread_public_messages
                }

                const project = { ...item.project, newActivities }

                return { ...item, project }
            })

            return projectsWithNewActivities;
        },
        extractAndCreateAdvisorDepartments(projects) {
            const departments = []

            projects.forEach(item => {

                const foundDepartment = departments.find(department => department.code === item.project?.commune?.department?.code)

                if (foundDepartment) {
                    foundDepartment.nbProjects++
                    return foundDepartment
                };

                const deparmentItem = { ...item.project?.commune?.department, active: true, nbProjects: 1 }

                departments.push(deparmentItem)
            })

            return this.departments = departments.sort(this.sortDepartments);
        },
        handleTerritorySelectAll() {
            this.territorySelectAll = !this.territorySelectAll

            this.departments = this.departments.map(department => ({ ...department, active: this.territorySelectAll }))

            return this.displayedData = this.filterProjectsByDepartments(this.searchProjects(this.search)).sort(this.currentSort);
        },
        handleTerritoryFilter(selectedDepartment) {
            this.departments = this.departments.map(department => {
                if (department.code === selectedDepartment.code) {
                    department.active = !department.active
                }

                return department
            })

            this.territorySelectAll = this.departments.filter(department => department.active).length === this.departments.length

            return this.displayedData = this.filterProjectsByDepartments(this.searchProjects(this.search)).sort(this.currentSort);
        },
        filterProjectsByDepartments(projects) {
            this.addCurrentStateToStore('departments', this.departments)

            //find department item from departments for each project and return if the department is active
            return projects.filter(item => this.departments.find(department => department.code === item.project.commune.department.code)?.active)
        },
        handleProjectsSearch(event) {

            const searchValue = event.target.value

            if (searchValue === "") {
                this.addCurrentStateToStore('search', searchValue)
                return this.displayedData = this.filterProjectsByDepartments(this.data).sort(this.currentSort);
            }

            const newProjectList = this.searchProjects(searchValue)

            this.addCurrentStateToStore('search', searchValue)

            return this.displayedData = this.filterProjectsByDepartments(newProjectList).sort(this.currentSort)
        },
        searchProjects(searchValue) {
            return this.data.filter(item => {
                if (item.project.name?.toLowerCase().includes(searchValue.toLowerCase())) return item
                if (item.project.commune?.name?.toLowerCase().includes(searchValue.toLowerCase())) return item
                if (item.project.commune?.insee?.includes(searchValue)) return item
                if (item.project.id.toString().includes(searchValue) && searchValue.length < 4) return item
            })
        },
        addCurrentStateToStore(item, value) {
            return window.localStorage.setItem(item, JSON.stringify(value));
        },
        readCurrentStateFromStore(item) {
            return localStorage.getItem(item);
        },
        removeStateFromStore(item) {
            return localStorage.removeItem(item)
        },
        handleProjectsSelect(event) {
            this.currentSort = this.getCurrentSortFn(event.target.value)

            this.select = event.target.value
            this.addCurrentStateToStore('sort', this.select)

            return this.displayedData = this.displayedData.sort(this.currentSort)
        },
        getCurrentSortFn(select) {

            let sortCriterion;

            switch (select) {
                case "commune-name":
                    sortCriterion = this.sortProjectCommuneName
                    break;
                case "date":
                    sortCriterion = this.sortProjectDate
                    break;
                case "insee":
                    sortCriterion = this.sortProjectInsee
                    break;
                case "recent-activities":
                    sortCriterion = this.sortProjectRecentActivities
                    break;
                case "role":
                    sortCriterion = this.sortProjectRole
                    break;
                default:
                    sortCriterion = this.sortProjectDate
                    break;
            }

            return sortCriterion
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
        sortProjectRecentActivities(a, b) {
            if (a.project.newActivities === a.project.newActivities && new Date(a.project.updated_on) === new Date(b.project.updated_on)) {
                if (new Date(a.project?.created_on) > new Date(b.project?.created_on)) {
                    return -1
                } else if (new Date(a.project.created_on) < new Date(b.project.created_on)) {
                    return 1
                } else return 0
            }
            else if (a.project.newActivities === b.project.newActivities) {
                if (new Date(a.project?.updated_on) > new Date(b.project?.updated_on)) {
                    return -1
                } else if (new Date(a.project.updated_on) < new Date(b.project.updated_on)) {
                    return 1
                } else return 0
            } else {
                if (a.project.newActivities > b.project.newActivities) {
                    return -1
                } else if (a.project.newActivities < b.project.newActivities) {
                    return 1
                } else return 0
            }
        },
        sortProjectRole(a, b) {

            if (a.project.is_switchtender && !a.project.is_observer) {
                return -1
            }
            if (b.project.is_switchtender && !b.project.is_observer) {
                return 1
            }
            if (a.project.is_switchtender && a.project.is_switchtender) {
                return -1
            }
            if (b.project.is_switchtender && b.project.is_observer) {
                return 1
            }

            return 0
        },
        sortDepartments(a, b) {
            if (a.code < b.code) {
                return -1
            } else if (a.code > b.code) {
                return 1
            } else return 0
        },
        handleMapOpen() {
            //251 -> 0.25s for the map height transition +1 ms
            setTimeout(() => this.map.invalidateSize(), 251)
            setTimeout(() => zoomToCentroid(this.map, this.markersLayer), 251)

            this.mapIsSmall = !this.mapIsSmall

            this.handleBodyTopPaddingScroll(80)
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

                const updatedProject = updatedProjects.find(({ project }) => project.id === id)
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
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    });

    const map = L.map('map').setView([48.51, 10.20], 2);

    L.tileLayer.provider('CartoDB.Positron').addTo(map);

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

            let lat = item.project?.commune?.latitude + (Math.random() * 0.001)
            let long = item.project?.commune?.longitude + (Math.random() * 0.001)

            return L.marker([lat, long], { icon: createMarkerIcon(item) }).addTo(map).bindPopup(markerPopupTemplate(item), {
                maxWidth: "auto"
            })
        }
    })
}

function createMarkerIcon(item) {
    return L.divIcon({ className: `map-marker ${item.status === "NEW" ? 'project-marker new-project-marker' : 'project-marker'}` });
}


function markerPopupTemplate(item) {

    let roleTemplate = null;

    if (item.status === "NEW") {
        roleTemplate = `
        <div class="project-card-top-information new">
            <span>Nouveau projet</span>
        </div>
        `
    }

    if (item.project.is_observer) {
        roleTemplate = `
        <div class="project-card-top-information observer">
            <span>Observateur</span>
        </div>
        `
    }

    if (item.project.is_switchtender && !item.project.is_observer) {
        roleTemplate = `
        <div class="project-card-top-information advisor">
            <span>Conseiller</span>
        </div>
        `
    }

    return `
        <div class="dashboard-marker-popup ${item.status === "NEW" && "new-project"}" style="${item.status === "NEW" ? 'border:solid 1px #FDCD6D' : 'border:solid 1px #222'}">
            ${roleTemplate != null ? roleTemplate : ''}
            <a class="text-nowrap project-link d-flex align-items-center" href="/project/${item.project.id}/presentation">
                <span class="text-nowrap fw-bold title-info text-dark me-2 location">${item.project.commune.name}</span>
                <span class="text-nowrap text-info-custom text-grey-dark name">${item.project.name}</span>
            </a>
        </div>
    `
}

export function makeProjectPositioningActionURL(url, id) {
    return url.replace('0', id);
}


Alpine.data("PersonalAdvisorDashboard", PersonalAdvisorDashboard)
