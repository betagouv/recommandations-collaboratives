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
		project: null,
		projectMapModal: null,

		async init() {
			this.project = {
				name: nameProject,
				status,
				commune: {
					name: nameCommune,
					postal,
					latitude: latitude ? parseFloat(latitude) : 46.51,
					longitude: longitude ? parseFloat(longitude) :1.20,
				}
			}
			const options = mapOptions({interactive: false});
			const	Map = initMap('map', this.project.commune.latitude, this.project.commune.longitude, options);
			initMapLayers(Map, this.project);
			this.initProjectMapModal();
			//Center Map
			Map.panTo(new L.LatLng(this.project.commune.latitude, this.project.commune.longitude));
		},
		initProjectMapModal() {
			const element = document.getElementById("project-map-modal");
			this.projectMapModal = new bootstrap.Modal(element);
		},
		openProjectMapModal() {
			this.interactive = true;
			this.mapIsSmall = false;
			const options = mapOptions({interactive: false});
			// const	Map = initMap('map-modal', this.project.commune.latitude, this.project.commune.longitude, options);
			this.projectMapModal.show();
		},
	}
}

// Map base layer 
function initMap(idMap, latitude, longitude, options) {
	const map = L.map(idMap, options).setView([latitude, longitude],12);
	setTimeout(function(){  map.invalidateSize()}, 0); // forces map redraw to fit container

	L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
		maxZoom: 20,
		attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
	});
	
	L.tileLayer.provider('OpenStreetMap.France').addTo(map);

	return map;
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