import Alpine from "alpinejs";
import * as L from 'leaflet';
import 'leaflet-control-geocoder';
import 'leaflet-providers'

import { statusToText, statusToColorClass } from '../utils/statusToText'

import api from '../utils/api'
Alpine.data("Map", Map)

function Map() {
    return {
        data: [],

        get isBusy() {
            return this.$store.app.isLoading
        },

        async getData() {
            const json = await api.get('/api/projects/');

            this.data = json.data
        },

        async init() {

            await this.getData();

            const Map = initMap();
            initMapController(Map);
            initMapLayers(Map, this.data)

            //Center Map
            Map.panTo(new L.LatLng(46.51, 1.20));
        }
    }
}

// Map base layer 
function initMap() {
    L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
        maxZoom: 20,
        attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });

    const map = L.map('map').setView([48.51, 10.20], 5);

    L.tileLayer.provider('OpenStreetMap.France').addTo(map);

    return map
}

// Crete layers composed with markers
function initMapLayers(map, projects) {
    let projectsByStatus = {}

    //Creates markers with icon
    //Add thoses markers to a global object - projectsByStatus
    projects.forEach(project => {
        if (project?.commune?.latitude && project?.commune?.longitude) {
            let marker = L.marker([project.commune.latitude, project.commune.longitude], { icon: createMarkerIcon(project) }).addTo(map)
            marker.bindPopup(markerPopupTemplate(project))

            if (!projectsByStatus[statusToText(project.status)]) projectsByStatus[statusToText(project.status)] = []

            projectsByStatus[statusToText(project.status)].push(marker)
        }
    })

    // For each status, we create a layerGroup composed with markers
    Object.entries(projectsByStatus).forEach(([key, value]) => {
        projectsByStatus[key] = L.layerGroup(value)
    })

    L.control.layers(null, projectsByStatus).addTo(map);
}

function initMapController(map) {
    L.Control.geocoder({
        geocoder: L.Control.Geocoder.nominatim()
    }).addTo(map);

    const controller = document.getElementsByClassName('leaflet-control-geocoder');
    controller[0].classList.add('leaflet-control-geocoder-expanded');
    const inputController = controller[0].querySelector('input')
    inputController.addEventListener('blur', (e) => {
        controller[0].classList.add('leaflet-control-geocoder-expanded');
    })
}

function createMarkerIcon(project) {
    return L.divIcon({ className: 'map-marker ' + statusToColorClass(project.status) });
}

function markerPopupTemplate(project) {
    const date = new Date(project.created_on).toLocaleDateString()

    return `
        <div class="marker-popup">
            <header><h3><a href="/project/${project.id}/presentation">${project.name}</a></h3></header>
            <main class="d-flex flex-column">
                <p class="m-0 mb-2 fs-6 fw-bold">Organisation</p>
                <p class="m-0 fs-7">${project.org_name}</p>
                <hr/>
                <p class="m-0 mb-2 fs-6 fw-bold">Lieu</p>
                <p class="m-0 fs-7">${project.location}</p>
                <hr/>
                <p class="m-0 mb-2 fs-6 fw-bold">Date de dépot</p>
                <p class="m-0 fs-7">${date}</p>
            </main>
        </div>
    `
}
