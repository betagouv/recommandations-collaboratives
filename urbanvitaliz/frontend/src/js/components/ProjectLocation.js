import Alpine from 'alpinejs'

import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css'
import 'leaflet-control-geocoder/dist/Control.Geocoder.css'
import 'leaflet-control-geocoder';
import 'leaflet-providers'

import { statusToColorClass } from '../utils/statusToText'


function ProjectLocation(latitude, longitude, status) {
	return {
		// map
		map: null,
		mapIsSmall: true,

		async init() {
			if(!this.map){
				this.map = initMap(parseFloat(latitude), parseFloat(longitude));
			}
			initMapLayers(this.map, parseFloat(latitude), parseFloat(longitude), status)
			//Center Map
			this.map.panTo(new L.LatLng(46.51, 1.20));
		},
	}
}

// Map base layer 
function initMap(latitude, longitude) {
	const map = L.map('map').setView([latitude, longitude], 5);
	L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
		maxZoom: 20,
		attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
	});
	
	L.tileLayer.provider('OpenStreetMap.France').addTo(map);

	setTimeout(function(){  map.invalidateSize()}, 0);
	return map
}

// Crete layers composed with markers
function initMapLayers(map, latitude, longitude, status) {
		let marker = L.marker([latitude, longitude], { icon: createMarkerIcon(status) }).addTo(map)
		L.layerGroup(marker)
}

function createMarkerIcon(status) {
	return L.divIcon({ className: 'map-marker ' + statusToColorClass(status) });
}

Alpine.data("ProjectLocation", ProjectLocation)