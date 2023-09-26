import Alpine from 'alpinejs'

import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css'
import 'leaflet-providers'

import { statusToColorClass } from '../utils/statusToText'

const codesComParis = ['75101','75102','75103','75104','75105','75106','75107','75108','75109','75110','75111','75112','75113','75114','75115','75116','75117','75118','75119','75120']
const codesComLyon = ['69381','69382','69383','69384','69385','69386','69387','69388','69389']
const codesComMarseille = ['13201','13202','13203','13204','13205','13206','13207','13208','13209','13210','13211','13212','13213','13214','13215','13216']
const apiCadastre = 'https://apicarto.ign.fr/api/cadastre/'

function getGlobalCityCodeFromCodeInsee(codeInsee) {
    if (codesComParis.includes(codeInsee)) {
        return '75056'
    }
    if (codesComLyon.includes(codeInsee)) {
        return '69123'
    }
    if (codesComMarseille.includes(codeInsee)) {
        return '13055'
    }
}

function getCodeArrFromCodeInsee(codeInsee) {
    return codeInsee.slice(-3)
}

async function fetchCommuneIgn(codeInsee) {
    const apiEndpoint = `${apiCadastre}/commune?`;
    const headers = new Headers({
        "Content-Type": "application/json",
    });
	const searchParams = {}
	if (!getGlobalCityCodeFromCodeInsee(codeInsee)) {
        searchParams['code_insee'] = codeInsee;
    } else {
        const codeArr = getCodeArrFromCodeInsee(codeInsee);
		const insee = getGlobalCityCodeFromCodeInsee(codeInsee);
        searchParams['code_arr'] = codeArr;
        searchParams['code_insee'] = insee;
    }
    return fetch(apiEndpoint + new URLSearchParams(searchParams)).then(response => response.json());
}

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

			const Map = initMap('map', this.project, options, zoom);
			
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

			this.interactiveMap = initMap('map-modal', project, options, zoom);
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
function initMap(idMap, project, options, zoom) {
	const { latitude, longitude } = project.commune;
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
	if(project.location) {  // TODO: use location for marker (?)
		const { latitude, longitude } =  project.commune;
		let marker = L.marker([latitude, longitude], { icon: createMarkerIcon(project.status) }).addTo(map)
		marker.bindPopup(markerPopupTemplate(project))
		L.layerGroup(marker)
	} else if(project.commune.insee) {
		addLayerCommune(map, project)
	}
}

function addLayerCommune(map, project) {
	let { insee } =  project.commune;
	const communeGeo = fetchCommuneIgn(insee)
	if (communeGeo.code && communeGeo.code == 400) {
		return false; // TODO: handle error
	} else {
		const communeLayer = L.geoJSON(null, communeGeo).addTo(map);
		return communeLayer
	}
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