import Alpine from 'alpinejs'

import * as L from 'leaflet';
import 'leaflet-control-geocoder';
import 'leaflet-providers'

import { statusToText, statusToColorClass } from '../utils/statusToText'

import api from '../utils/api'

function ProjectLocation() {
	return {
		data: null,
		// map
		map: null,
		mapIsSmall: false,
		markersLayer: "",

		get isBusy() {
			return this.$store.app.isLoading
		},
		async getData(projectId) {
			if(projectId) {
				const json = await api.get(`/api/projects/${projectId}`);
				this.data = json.data
			}
		},
	
		async init(projectId) {
			await this.getData(projectId);
			if(!this.map){
				this.map = initMap();
			}
			initMapController(this.map);
			if(this.data) {
				initMapLayers(this.map , this.data)
			} else {
				//Center Map
				this.map .panTo(new L.LatLng(46.51, 1.20));
			}
            this.handleBodyTopPaddingScroll(this.bodyScrollTopPadding);
		},
		handleBodyTopPaddingScroll(height) {
			this.bodyScrollTopPadding = height
			window.document.body.style.scrollPaddingTop = `${this.bodyScrollTopPadding}px`;
			window.document.documentElement.style.scrollPaddingTop = `${this.bodyScrollTopPadding}px`;
		},
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

// Crete layers composed with markers
function initMapLayers(map, project) {
	let projectsByStatus = {}
	//Creates markers with icon
	//Add thoses markers to a global object - projectsByStatus
	if (project.commune?.latitude && project?.commune?.longitude) {
		let marker = L.marker([project.commune.latitude, project.commune.longitude], { icon: createMarkerIcon(project) }).addTo(map)
		marker.bindPopup(markerPopupTemplate(project))

		if (!projectsByStatus[statusToText(project.status)]) projectsByStatus[statusToText(project.status)] = []

		projectsByStatus[statusToText(project.status)].push(marker)


		//Center Map
		map.panTo(new L.LatLng(project.commune.latitude, project.commune.longitude));
	}
	// For each status, we create a layerGroup composed with markers
	Object.entries(projectsByStatus).forEach(([key, value]) => {
		projectsByStatus[key] = L.layerGroup(value)
	})

	L.control.layers(null, projectsByStatus).addTo(map);
}

function createMarkerIcon(project) {
	return L.divIcon({ className: 'map-marker ' + statusToColorClass(project.status) });
}

function markerPopupTemplate(project) {
	const date = new Date(project.created_on).toLocaleDateString()

	return `
		<div class="marker-popup">
			<header><h3${project.name}</h3></header>
			<main class="d-flex flex-column">
				<p class="m-0 mb-2 fs-6 fw-bold">Commune</p>
				<p class="m-0 fs-7 text-capitalize">${project?.commune?.name} (${project?.commune?.postal})</p>
				<hr/>
			</main>
		</div>
	`
}

export function makeProjectPositioningActionURL(url, id) {
    return url.replace('0', id);
}

Alpine.data("ProjectLocation", ProjectLocation)