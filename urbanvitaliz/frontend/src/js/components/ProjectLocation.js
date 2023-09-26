import Alpine from 'alpinejs'

import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css'
import 'leaflet-providers'

import { statusToColorClass } from '../utils/statusToText'

function ProjectLocation(projectOptions) {
	return {
		mapIsSmall: true,
		project: null,
		mapModal: null,
		interactiveMap: null,

		async init() {
			this.project = {
				...projectOptions,
				commune: {
					...projectOptions.commune,
					latitude: projectOptions.commune.latitude ? parseFloat(projectOptions.commune.latitude) : 46.51,
					longitude: projectOptions.commune.longitude ? parseFloat(projectOptions.commune.longitude) :1.20,
				}
			}
			const options = mapOptions({interactive: false});
			const zoom = 10;
			const { latitude, longitude } = this.project.commune;

			const Map = initMap('map', latitude, longitude, options, zoom);
			
			initMapLayers(Map, this.project);
			
			// forces map redraw to fit container
			setTimeout(function(){  Map.invalidateSize()}, 0); 
			//Center Map
			Map.panTo(new L.LatLng(latitude, longitude));

			this.initProjectMapModal(this.project);
		},

		initProjectMapModal(project) {
			const element = document.getElementById("project-map-modal");
			this.mapModal = new bootstrap.Modal(element);

			const options = mapOptions({interactive: true});
			const zoom = 13;
			const { latitude, longitude } = project.commune;

			this.interactiveMap = initMap('map-modal', latitude, longitude, options, zoom);
			this.interactiveMap.panTo(new L.LatLng(latitude, longitude));
			this.interactiveMap.setMinZoom(zoom - 7);
			this.interactiveMap.setMaxZoom(zoom + 6);

			const map = this.interactiveMap;
			element.addEventListener('shown.bs.modal', function (event) {
				 // forces map redraw to fit container
				setTimeout(function(){  map.invalidateSize()}, 0);
			})
			initMapLayers(this.interactiveMap, project);
		},

		openProjectMapModal() {
			this.mapIsSmall = false;
			this.mapModal.show();
		},
	}
}

// Map base layer 
function initMap(idMap, latitude, longitude, options, zoom) {
	const map = L.map(idMap, options).setView([latitude, longitude], zoom);

	L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
		maxZoom: 20,
		attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
	});
	
	L.tileLayer.provider('OpenStreetMap.France').addTo(map);

	return map;
}

// Create layers composed with markers
function initMapLayers(map, project) {
		const { latitude, longitude } =  project.commune;
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
				<p class="m-0 fs-6"><span class="fw-bold">${project.name}</span> (${project.commune.name})</p>
			</main>
		</div>
	`
}

function mapOptions({interactive}) {
	return {
		dragging: interactive,
		touchZoom: interactive,
		doubleClickZoom: interactive,
		scrollWheelZoom: interactive,
		boxZoom: interactive,
		keyboard: interactive,
		zoomControl: interactive
	}
}

Alpine.data("ProjectLocation", ProjectLocation)