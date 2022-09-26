import Alpine from "alpinejs";
import 'leaflet';
import 'leaflet-control-geocoder';

import data from '../utils/map.data.json';

Alpine.data("Map", Map)

function Map() {
    return {
        isLoaded: false,
        init() {
            const map = L.map('map').setView([48.51, 2.20], 5);

            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '© OpenStreetMap'
            }).addTo(map);

            L.Control.geocoder({
                geocoder: L.Control.Geocoder.nominatim()
            }).addTo(map);

            console.log('data :', data);
            console.log('friche 1 lat', data[0]);

            //We filter here : 
            // Project not excluded
            // Project with a known lat & long
            data.filter(project => project.exclude_stats == 'False' && project['commune.latitude'] && project['commune.longitude']).map((project) => {
                const marker = L.marker([project['commune.latitude'], project['commune.longitude']]).addTo(map);

                return marker.bindPopup(`<div><a href="/project/${project.id}/presentation">${project.name}</a><br/><strong>${project.org_name}</strong></div>`).openPopup();
            })

        }
    }
}
