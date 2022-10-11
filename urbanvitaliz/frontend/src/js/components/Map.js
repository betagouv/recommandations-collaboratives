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

            // Map base layer 
            L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
                maxZoom: 20,
                attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            });

            const map = L.map('map').setView([48.51, 10.20], 5);

            L.tileLayer.provider('OpenStreetMap.France').addTo(map);

            // Map controller 
            L.Control.geocoder({
                geocoder: L.Control.Geocoder.nominatim()
            }).addTo(map);

            const controller = document.getElementsByClassName('leaflet-control-geocoder');
            controller[0].classList.add('leaflet-control-geocoder-expanded');
            const inputController = controller[0].querySelector('input')
            inputController.addEventListener('blur', (e) => {
                controller[0].classList.add('leaflet-control-geocoder-expanded');
            })

            // Map data layer project layer group
            const status = extractAllStatus(this.data);

            let projectsByStatus = {}

            status.forEach(status => {
                let filteredProjects = []

                this.data.forEach(project => {

                    if (project.status === status) {

                        const myIcon = L.divIcon({ className: 'map-marker ' + statusToColorClass(project.status) });
                        let marker = L.marker([project.commune.latitude, project.commune.longitude], { icon: myIcon }).addTo(map)
                        marker.bindPopup(markerPopupTemplate(project))

                        filteredProjects.push(marker);
                    }
                })
                
                projectsByStatus[statusToText(status)] = L.layerGroup(filteredProjects)
            })

            L.control.layers(null, projectsByStatus).addTo(map);

            //Center map
            map.panTo(new L.LatLng(46.51, 1.20));
        }
    }
}

function extractAllStatus(data) {

    let status = []
    let flags = []

    data.filter(project => project.status !== "DRAFT").forEach(project => {
        if (!flags[project.status]) {
            flags[project.status] = true;
            status.push(project.status);
        }
    });

    return status
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
