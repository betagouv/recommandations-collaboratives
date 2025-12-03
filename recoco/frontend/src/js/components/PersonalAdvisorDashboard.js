import Alpine from 'alpinejs';
import api, { projectsUrl } from '../utils/api';
import { formatDate } from '../utils/date';
import { gravatar_url } from '../utils/gravatar';
import { makeProjectURL } from '../utils/createProjectUrl';

import * as L from 'leaflet';
import 'leaflet-control-geocoder';
import 'leaflet-providers';
import 'leaflet/dist/leaflet.css';
import 'leaflet-control-geocoder/dist/Control.Geocoder.css';
import _ from 'lodash';

function PersonalAdvisorDashboard(currentSiteId, departments, regions) {
  return {
    currentSiteId: currentSiteId,
    data: [],
    displayedData: [],
    errors: null,
    formatDate,
    gravatar_url,
    makeProjectURL,
    //*** new filters for map
    backendSearch: {
      searchText: '',
      searchDepartment: [],
      lastActivity: localStorage.getItem('lastActivity') ?? '30',
    },
    searchText: '',
    filterProjectLastActivity: localStorage.getItem('lastActivity') ?? '30',
    isDisplayingOnlyUserProjects:
      JSON.parse(localStorage.getItem('isDisplayingOnlyUserProjects')) ?? false,
    //*** departments
    regions: JSON.parse(regions.textContent),
    territorySelectAll: true,
    //*** map
    map: null,
    mapIsSmall: false,
    markersLayer: '',
    //*** options
    //*** header's height + some px
    bodyScrollTopPadding: 80,
    allProjects: [],
    async init() {
      this.allProjects = await this.$store.projects.getUserProjetsStatus();
      await this.getDataFiltered();
    },
    async getData(currentUser) {
      const projects = await this.$store.projects.getUserProjetsStatus();
      await this.$store.projects.mapperProjetsProjectSites(
        projects,
        this.currentSiteId
      );
      this.nbNewProjects = projects.filter((p) => p.status === 'NEW').length;

      this.data = projects.map((project) => ({ ...project, isLoading: false }));

      this.data = _.unionBy(this.data, 'project.id');
      this.displayedData = this.data.sort(this.sortProjectDate);
      if (this.map) {
        this.map.remove();
      }
      if (this.markersLayer) {
        this.markersLayer.remove();
      }
      const { map, markersLayer } = initMap(projects);

      this.map = map;
      this.markersLayer = markersLayer;

      if (projects.length > 0) {
        zoomToCentroid(this.map, this.markersLayer);
      } else {
        setTimeout(() => this.map.invalidateSize(), 251);
      }
    },
    get isBusy() {
      return this.$store.app.isLoading;
    },
    regionsFilterResponse(event) {
      if (!event.detail) return;

      this.departments = event.detail;

      return (this.displayedData = this.filterProjectsByDepartments(
        this.searchProjects(this.search)
      ).sort(this.currentSort));
    },
    filterProjectsByDepartments(projects) {
      this.addCurrentStateToStore('departments', this.departments);

      //find department item from departments for each project and return if the department is active
      return projects.filter(
        (item) =>
          this.departments.find(
            (department) =>
              department.code === item.project.commune?.department?.code
          )?.active
      );
    },
    handleProjectsSearch(event) {
      const searchValue = event.target.value;

      if (searchValue === '') {
        this.addCurrentStateToStore('search', searchValue);
        return (this.displayedData = this.filterProjectsByDepartments(
          this.data
        ).sort(this.currentSort));
      }

      const newProjectList = this.searchProjects(searchValue);

      this.addCurrentStateToStore('search', searchValue);

      return (this.displayedData = this.filterProjectsByDepartments(
        newProjectList
      ).sort(this.currentSort));
    },
    searchProjects(searchValue) {
      return this.data.filter((item) => {
        if (
          item.project.name?.toLowerCase().includes(searchValue.toLowerCase())
        )
          return item;
        if (
          item.project.commune?.name
            ?.toLowerCase()
            .includes(searchValue.toLowerCase())
        )
          return item;
        if (item.project.commune?.insee?.includes(searchValue)) return item;
        if (
          item.project.id.toString().includes(searchValue) &&
          searchValue.length < 4
        )
          return item;
      });
    },
    handleMapOpen() {
      //251 -> 0.25s for the map height transition +1 ms
      setTimeout(() => this.map.invalidateSize(), 251);
      setTimeout(() => zoomToCentroid(this.map, this.markersLayer), 251);

      this.mapIsSmall = !this.mapIsSmall;
    },
    //*** filters functions

    async onLastActivityChange(event) {
      this.backendSearch.lastActivity = event.target.value;
      localStorage.setItem('lastActivity', this.backendSearch.lastActivity);
      await this.getDataFiltered();
    },

    async getDataFiltered() {
      const { searchText, searchDepartment, lastActivity } = this.backendSearch;
      const projects = await api.get(
        projectsUrl(searchText, searchDepartment, lastActivity)
      );
      this.projectList = await this.$store.projects.mapperProjetsProjectSites(
        projects.data,
        this.currentSiteId
      );
      this.projectList = this.projectList
        .filter((fp) => this.allProjects.some((p) => p.project.id === fp.id))
        .map((fp) => {
          return this.allProjects.find((p) => p.project.id === fp.id);
        });
      this.projectListFiltered = [...this.projectList];
      this.filterMyProjects();
    },

    filterMyProjects() {
      if (this.isDisplayingOnlyUserProjects) {
        this.projectListFiltered = this.projectList.filter(
          (d) => d.project.is_observer || d.project.is_switchtender
        );
      } else {
        this.projectListFiltered = [...this.projectList];
      }
      if (this.map) {
        this.map.remove();
      }
      if (this.markersLayer) {
        this.markersLayer.remove();
      }
      const { map, markersLayer } = initMap(this.projectListFiltered);
      this.map = map;
      this.markersLayer = markersLayer;
      if (this.projectListFiltered.length > 0) {
        zoomToCentroid(this.map, this.markersLayer);
      } else {
        setTimeout(() => this.map.invalidateSize(), 251);
      }
    },

    toggleMyProjectsFilter() {
      this.isDisplayingOnlyUserProjects = !this.isDisplayingOnlyUserProjects;
      localStorage.setItem(
        'isDisplayingOnlyUserProjects',
        this.isDisplayingOnlyUserProjects
      );
      this.filterMyProjects();
    },

    async onSearch(event) {
      this.backendSearch.searchText = event.target.value;
      await this.backendSearchProjects({ resetLastActivity: true });
    },

    async backendSearchProjects(options = { resetLastActivity: false }) {
      if (this.backendSearch.searchText !== '') {
        if (this.$refs.selectFilterProjectDuration) {
          this.$refs.selectFilterProjectDuration.disabled = true;
          this.$refs.selectFilterProjectDuration.value = 1460;
        }
        this.backendSearch.lastActivity = '';
      } else if (options.resetLastActivity) {
        const lastActivity = localStorage.getItem('lastActivity') ?? 30;
        if (this.$refs.selectFilterProjectDuration) {
          this.$refs.selectFilterProjectDuration.disabled = false;
          this.$refs.selectFilterProjectDuration.value = lastActivity;
        }
        this.backendSearch.lastActivity = lastActivity.toString();
      }

      await this.getDataFiltered();
    },

    async saveSelectedDepartment(event) {
      if (!event.detail) return;

      this.backendSearch.searchDepartment = [...event.detail];
      await this.backendSearchProjects();
    },
  };
}

// Map base layer
function initMap(projects) {
  L.tileLayer(
    'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 20,
    }
  );

  // Guard against double-initialization on the same container
  const existing = L.DomUtil.get('map');
  if (existing && existing._leaflet_id) {
    // If a map is already bound to this element, remove it first
    existing._leaflet_id = null;
  }
  const map = L.map('map').setView([48.51, 10.2], 2);

  L.tileLayer.provider('CartoDB.Positron').addTo(map);

  const markers = createMapMarkers(map, projects);
  const markersLayer = createMarkersLayer(map, markers);

  return { map, markersLayer };
}

//Create a layer in order to zoom-in at the center of each markers
function createMarkersLayer(map, markers) {
  const markersLayer = new L.FeatureGroup();
  markers.forEach((marker) => {
    if (marker) markersLayer.addLayer(marker);
  });
  markersLayer.addTo(map);

  return markersLayer;
}

function zoomToCentroid(map, markersLayer) {
  return map.fitBounds(markersLayer.getBounds());
}

// Crete layers composed with markers
function createMapMarkers(map, projects) {
  return projects.map((item) => {
    if (item.project?.commune?.latitude && item.project?.commune?.longitude) {
      let lat = item.project?.commune?.latitude + Math.random() * 0.001;
      let long = item.project?.commune?.longitude + Math.random() * 0.001;

      return L.marker([lat, long], { icon: createMarkerIcon(item) })
        .addTo(map)
        .bindPopup(markerPopupTemplate(item), {
          maxWidth: 'auto',
        });
    }
  });
}

function createMarkerIcon(item) {
  return L.divIcon({
    className: `map-marker ${item.status === 'NEW' ? 'project-marker new-project-marker' : 'project-marker'}`,
  });
}

function markerPopupTemplate(item) {
  let roleTemplate = null;

  if (item.status === 'NEW') {
    roleTemplate = `
        <div class="project-card-top-information new">
            <span>Nouveau dossier</span>
        </div>
        `;
  }

  if (item.project.is_observer) {
    roleTemplate = `
        <div class="project-card-top-information observer">
            <span>Observateur</span>
        </div>
        `;
  }

  if (item.project.is_switchtender && !item.project.is_observer) {
    roleTemplate = `
        <div class="project-card-top-information advisor">
            <span>Conseiller</span>
        </div>
        `;
  }

  return `
        <div class="dashboard-marker-popup ${item.status === 'NEW' && 'new-project'} tmp-usevar" style="${item.status === 'NEW' ? 'border:solid 1px #FDCD6D' : 'border:solid 1px #222'}">
            ${roleTemplate != null ? roleTemplate : ''}
            <a class="text-nowrap project-link d-flex align-items-center" href="/project/${item.project.id}/presentation">
                <span class="text-nowrap fw-bold title-info text-dark fr-mr-2v location">${item.project.commune.name}</span>
                <span class="text-nowrap text-info-custom text-grey-dark name">${item.project.name}</span>
            </a>
        </div>
    `;
}

export function makeProjectPositioningActionURL(url, id) {
  return url.replace('0', id);
}

Alpine.data('PersonalAdvisorDashboard', PersonalAdvisorDashboard);
