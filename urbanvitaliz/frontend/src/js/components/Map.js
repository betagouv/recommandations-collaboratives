import Alpine from "alpinejs";
import * as L from 'leaflet';
import 'leaflet-control-geocoder';
import 'leaflet-providers'

import data from '../utils/map.data.json';

Alpine.data("Map", Map)

function Map() {
    return {
        isLoaded: false,
        init() {
            const map = L.map('map').setView([48.51, 2.20], 5);

            L.tileLayer.provider('OpenStreetMap.France').addTo(map);

            const frosm = L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
                maxZoom: 20,
                attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            });

            L.Control.geocoder({
                geocoder: L.Control.Geocoder.nominatim()
            }).addTo(map);

            console.log('data :', data);
            console.log('friche 1 lat', data[0]);

            var myIcon = L.divIcon({ className: 'my-div-icon' });

            const status = extractAllStatus(data);

            let projectsByStatus = {}

            status.forEach(status => {
                let filteredProjects = []

                data.forEach(project => {
                    if (project.status === status) {

                        let marker = L.marker([project['commune.latitude'], project['commune.longitude']], { icon: myIcon }).addTo(map)
                        marker.bindPopup(`<div><a href="/project/${project.id}/presentation">${project.name}</a><br/><strong>${project.org_name}</strong></div>`).openPopup();

                        filteredProjects.push(marker);
                    }
                })

                projectsByStatus[status] = L.layerGroup(filteredProjects)
                // projectsByStatus.push(layerGroup)
            })

            // L.control.layers(frosm, projectsByStatus).addTo(map);
            const layerControl = L.control.layers(null, projectsByStatus).addTo(map);
            console.log('project by status : ', projectsByStatus);

            // layerControl.addOverlay(projectsByStatus);
        }
    }
}

function extractAllStatus(data) {

    let status = []
    let flags = []

    data.forEach(project => {
        if (!flags[project.status]) {
            flags[project.status] = true;
            status.push(project.status);
        }
    });

    return status
}
