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

function MapDashboard(currentSiteId, regions) {
  return {
    currentSiteId: currentSiteId,
    formatDate,
    gravatar_url,
    makeProjectURL,
    //*** new filters for map
    backendSearch: {
      searchText: '',
      searchDepartment: [],
    },
    searchText: '',
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
    allProjects: [],
    async init() {
      // this.allProjects = await this.$store.projects.getUserProjetsStatus();
      // if (this.map) {
      //   this.map.remove();
      // }
      // if (this.markersLayer) {
      //   this.markersLayer.remove();
      // }
      // const { map, markersLayer } = initMap(this.allProjects);

      // this.map = map;
      // this.markersLayer = markersLayer;

      // if (this.allProjects.length > 0) {
      //   zoomToCentroid(this.map, this.markersLayer);
      // } else {
      //   setTimeout(() => this.map.invalidateSize(), 251);
      // }
      await this.getDataFiltered();
    },
    get isBusy() {
      return this.$store.app.isLoading;
    },
    handleMapOpen() {
      //251 -> 0.25s for the map height transition +1 ms
      setTimeout(() => this.map.invalidateSize(), 251);
      setTimeout(() => zoomToCentroid(this.map, this.markersLayer), 251);

      this.mapIsSmall = !this.mapIsSmall;
    },
    //*** filters functions

    async getDataFiltered() {
      const { searchText, searchDepartment } = this.backendSearch;
      const projects = await api.get(
        projectsUrl({
          searchText: searchText,
          departments: searchDepartment,
          status: ['TO_PROCESS', 'STUCK', 'READY', 'IN_PROGRESS', 'DONE'],
        })
      );
      this.projectList = await this.$store.projects.mapperProjetsProjectSites(
        projects.data.results,
        this.currentSiteId
      );
      this.projectListFiltered = [...this.projectList];
      this.filterMyProjects();
    },

    filterMyProjects() {
      if (this.isDisplayingOnlyUserProjects) {
        this.projectListFiltered = this.projectList.filter(
          (d) => d.is_observer || d.is_switchtender
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
      await this.getDataFiltered();
    },

    async saveSelectedDepartment(event) {
      if (!event.detail) return;

      this.backendSearch.searchDepartment = [...event.detail];
      await this.getDataFiltered();
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
    let lat = item.latitude || item.commune?.latitude;
    let long = item.longitude || item.commune?.longitude;
    if (lat && long) {
      lat = lat + Math.random() * 0.001;
      long = long + Math.random() * 0.001;

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

  if (item.is_observer) {
    roleTemplate = `
        <div class="project-card-top-information observer">
            <span>Observateur</span>
        </div>
        `;
  }

  if (item.is_switchtender && !item.is_observer) {
    roleTemplate = `
        <div class="project-card-top-information advisor">
            <span>Conseiller</span>
        </div>
        `;
  }

  return `
        <div class="dashboard-marker-popup ${item.status === 'NEW' && 'new-project'} tmp-usevar" style="${item.status === 'NEW' ? 'border:solid 1px #FDCD6D' : 'border:solid 1px #222'}">
            ${roleTemplate != null ? roleTemplate : ''}
            <a class="text-nowrap project-link d-flex align-items-center" href="/project/${item.id}/presentation">
                <span class="text-nowrap fw-bold title-info text-dark fr-mr-2v location">${item.commune.name}</span>
                <span class="text-nowrap text-info-custom text-grey-dark name">${item.name}</span>
            </a>
        </div>
    `;
}

Alpine.data('MapDashboard', MapDashboard);
