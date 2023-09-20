import Alpine from 'alpinejs'

import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css'
import 'leaflet-control-geocoder/dist/Control.Geocoder.css'
import 'leaflet-control-geocoder';
import 'leaflet-providers'

import { statusToColorClass } from '../utils/statusToText'


function ProjectLocation(nameProject, status, nameCommune, postal, longitude, latitude) {
	return {
		mapIsSmall: true,

		async init() {
			let project = {
				name: nameProject,
				status,
				commune: {
					name: nameCommune,
					postal,
					latitude: latitude ? parseFloat(latitude) : 46.51,
					longitude: longitude ? parseFloat(longitude) :1.20,
				}
			}
			const	Map = initMap(project.commune.latitude, project.commune.longitude);
			initMapLayers(Map, project)
			//Center Map
			Map.panTo(new L.LatLng(project.commune.latitude, project.commune.longitude));
		},
	}
}

// Map base layer 
function initMap(latitude, longitude) {
	const map = L.map('map').setView([latitude, longitude], 7);
	setTimeout(function(){  map.invalidateSize()}, 0); // forces map redraw to fit container

	L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
		maxZoom: 20,
		attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
	});
	
	L.tileLayer.provider('OpenStreetMap.France').addTo(map);

	return map
}

// Crete layers composed with markers
function initMapLayers(map, project) {
		const { latitude, longitude } = project.commune;
		let marker = L.marker([latitude, longitude], { icon: createMarkerIcon(project.status) }).addTo(map)

		marker.bindPopup(markerPopupTemplate(project))
		L.layerGroup(marker)
}

function createMarkerIcon(status) {
	return L.divIcon({ className: 'map-marker ' + statusToColorClass(status) });
}

function markerPopupTemplate(project) {

	return `
		<div class="marker-popup">
			<main class="d-flex flex-column">
				<p class="m-0 mb-2 fs-6 fw-bold">Commune</p>
				<p class="m-0 fs-7 text-capitalize">${project.commune.name} (${project.commune.postal})</p>
			</main>
		</div>
	`
}

Alpine.data("ProjectLocation", ProjectLocation)