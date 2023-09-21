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
				latitude: projectOptions.latitude ? parseFloat(projectOptions.latitude) : 46.51,
				longitude: projectOptions.longitude ? parseFloat(projectOptions.longitude) :1.20,
			}
			const options = mapOptions({interactive: false});
			const zoom = 10;
			const Map = initMap('map', this.project.latitude, this.project.longitude, options, zoom);
			
			initMapLayers(Map, this.project);
			
			// forces map redraw to fit container
			setTimeout(function(){  Map.invalidateSize()}, 0); 
			//Center Map
			Map.panTo(new L.LatLng(this.project.latitude, this.project.longitude));

			this.initProjectMapModal();
		},

		initProjectMapModal() {
			const element = document.getElementById("project-map-modal");
			this.mapModal = new bootstrap.Modal(element);

			const options = mapOptions({interactive: true});
			const zoom = 13;
			this.interactiveMap = initMap('map-modal', this.project.latitude, this.project.longitude, options, zoom);
			this.interactiveMap.panTo(new L.LatLng(this.project.latitude, this.project.longitude));
			this.interactiveMap.setMinZoom(zoom - 7);
			this.interactiveMap.setMaxZoom(zoom + 6);

			const map = this.interactiveMap;
			element.addEventListener('shown.bs.modal', function (event) {
				 // forces map redraw to fit container
				setTimeout(function(){  map.invalidateSize()}, 0);
			})
			initMapLayers(this.interactiveMap, this.project);
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
		const { latitude, longitude } = project;
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
				<p class="m-0 fs-7 text-capitalize">${project.nameProject} (${project.nameCommune})</p>
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