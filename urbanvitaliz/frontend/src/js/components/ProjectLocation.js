import Alpine from 'alpinejs'

import * as L from 'leaflet';
import 'leaflet-control-geocoder';
import 'leaflet-providers'

import { statusToColorClass } from '../utils/statusToText'


function ProjectLocation(latitude, longitude, status) {
	return {
		// map
		map: null,

		async init() {
			if(!this.map){
				this.map = initMap(parseFloat(latitude), parseFloat(longitude));
			}
			initMapLayers(this.map, parseFloat(latitude), parseFloat(longitude), status)
		},
	}
}

// Map base layer 
function initMap(latitude, longitude) {
	L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
		maxZoom: 20,
		attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
	});

	const map = L.map('map').setView([latitude, longitude], 5);

	L.tileLayer.provider('OpenStreetMap.France').addTo(map);

	return map
}

// Crete layers composed with markers
function initMapLayers(map, latitude, longitude, status) {
		let marker = L.marker([latitude, longitude], { icon: createMarkerIcon(status) }).addTo(map)
		L.layerGroup(marker)
		//Center Map
		map.panTo(new L.LatLng(latitude, longitude));
}

function createMarkerIcon(status) {
	return L.divIcon({ className: 'map-marker ' + statusToColorClass(status) });
}


export function makeProjectPositioningActionURL(url, id) {
    return url.replace('0', id);
}

Alpine.data("ProjectLocation", ProjectLocation)