import Alpine from 'alpinejs'

import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css'
import 'leaflet-control-geocoder';
import 'leaflet-providers'

import { statusToColorClass } from '../utils/statusToText'

const codesComParis = ['75101','75102','75103','75104','75105','75106','75107','75108','75109','75110','75111','75112','75113','75114','75115','75116','75117','75118','75119','75120']
const codesComLyon = ['69381','69382','69383','69384','69385','69386','69387','69388','69389']
const codesComMarseille = ['13201','13202','13203','13204','13205','13206','13207','13208','13209','13210','13211','13212','13213','13214','13215','13216']

// const iconRetinaUrl = 'assets/marker-icon-2x.png';
// const iconUrl = 'assets/marker-icon.png';
// const shadowUrl = 'assets/marker-shadow.png';
// const iconDefault = L.icon({
//   iconRetinaUrl,
//   iconUrl,
//   shadowUrl,
//   iconSize: [25, 41],
//   iconAnchor: [12, 41],
//   popupAnchor: [1, -34],
//   tooltipAnchor: [16, -28],
//   shadowSize: [41, 41]
// });
// L.Marker.prototype.options.icon = iconDefault;


// Doc: https://apicarto.ign.fr/api/doc/cadastre#/Commune/get_cadastre_commune
const apiCadastre = 'https://apicarto.ign.fr/api/cadastre'
const apiAdresse = 'https://api-adresse.data.gouv.fr'
const latLongFrance = [46.5, 1.20] // latitude and longitude of centroid of France

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

async function fetchCommuneIgn(insee) {
	const apiEndpoint = `${apiCadastre}/commune?`;
	const searchParams = {}

	if (!getGlobalCityCodeFromCodeInsee(codeInsee)) {
        searchParams['code_insee'] = insee;
    } else {
        var codeArr = getCodeArrFromCodeInsee(codeInsee);
        var codeInsee = getGlobalCityCodeFromCodeInsee(codeInsee);
        searchParams['code_arr'] = codeArr;
        searchParams['code_insee'] = codeInsee;
    }

	const communeGeo = await fetch(apiEndpoint + new URLSearchParams(searchParams)).then(response => response.json());

	return communeGeo;
}

async function fetchGeolocationByAddress(address) {
	const apiEndpoint = `${apiAdresse}/search?`;
	const searchParams = { q: address, limit: 10 } // TODO
	const geoJSON = await fetch(apiEndpoint + new URLSearchParams(searchParams)).then(response => response.json());
	return geoJSON;
}

function ProjectLocation(projectOptions) {
	return {
		mapIsSmall: true,
		project: null,
		mapModal: null,
		interactiveMap: null,
		zoom: 5,

		async init() {
			this.project = {
				...projectOptions,
				commune: {
					...projectOptions.commune,
					latitude: projectOptions.commune.latitude ? parseFloat(projectOptions.commune.latitude) : null,
					longitude: projectOptions.commune.longitude ? parseFloat(projectOptions.commune.longitude) : null,
				}
			}
			const options = mapOptions({interactive: false});
			const { latitude, longitude, insee } = this.project.commune;

			this.zoom = latitude && longitude ? 11 : this.zoom;

			const Map = initMap('map', this.project, options, this.zoom);
			
			const geoData = {}
			geoData.commune = await fetchCommuneIgn(insee);
			geoData.location = await fetchGeolocationByAddress(this.project.location)
			initMapLayers(Map, this.project, geoData);
			
			// forces map redraw to fit container
			setTimeout(function(){Map.invalidateSize()}, 0);
			//Center Map
			Map.panTo(new L.LatLng(latitude, longitude));

			this.initProjectMapModal(this.project, geoData);
		},

		initProjectMapModal(project, geoData) {
			const element = document.getElementById("project-map-modal");
			this.mapModal = new bootstrap.Modal(element);

			const options = mapOptions({interactive: true});
			const zoom = this.zoom + 1;
			const latitude = project.commune.latitude ?? latLongFrance[0];
			const longitude = project.commune.longitude ?? latLongFrance[1];

			this.interactiveMap = initMap('map-modal', project, options, zoom);
			this.interactiveMap.panTo(new L.LatLng(latitude, longitude));
			this.interactiveMap.setMinZoom(zoom - 7);
			this.interactiveMap.setMaxZoom(zoom + 6);

			const map = this.interactiveMap;
			element.addEventListener('shown.bs.modal', function (event) {
				 // forces map redraw to fit container
				setTimeout(function(){  map.invalidateSize()}, 0);
			})
			initMapLayers(this.interactiveMap, project, geoData);
		},

		openProjectMapModal() {
			this.mapIsSmall = false;
			this.mapModal.show();
		},
	}
}

// Map base layer 
function initMap(idMap, project, options, zoom) {
	const latitude = project.commune.latitude ?? latLongFrance[0];
	const longitude = project.commune.longitude ?? latLongFrance[1];
	const map = L.map(idMap, options).setView([latitude, longitude], zoom);

	L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
		maxZoom: 20,
		attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
	});
	
	L.tileLayer.provider('OpenStreetMap.France').addTo(map);

	return map;
}

// Create layers composed with markers
function initMapLayers(map, project, geoData) {
	try {
		addLayerLatLong(map, geoData.location, project);
	} catch(e) {
		try {
			addLayerAreaCommune(map, geoData.commune);
		} catch(e) {
			if(project.commune.latitude && project.commune.longitude) {
				addLayerAreaCircle(map, project)
			}
		}
	}
}

function addLayerAreaCommune(map, geoData) {
	if(geoData.code && geoData.code === 400 || geoData.features.length === 0) {
		throw Error(`Données IGN indisponibles pour la commune ${geoData.commune.name}`)
	}

	L.geoJSON(geoData.features[0].geometry).addTo(map);
}

function addLayerLatLong(map, geoData, project) {
	if(geoData.code && geoData.code === 400 || geoData.features.length === 0) {
		throw Error(`Données API Adresse indisponibles pour ' ${geoData.location}`)
	}
	const coordinates = geoData.features[0].geometry.coordinates
  L.marker(coordinates, { icon: createMarkerIcon(project) }).addTo(map)
}
// Create layers composed with markers
function addLayerAreaCircle(map, project) {
	const { latitude, longitude } = project.commune;
	L.circle([latitude, longitude], {
			color: '#0063CB',
			fillColor: '#0063CB',
			fillOpacity: 0.25,
			radius: 5000,
			className: 'area-circle'
	}).addTo(map);
}


function createMarkerIcon(project) {
	return L.divIcon({ className: `map-marker ${project.status === "NEW" ? 'project-marker new-project-marker' : 'project-marker'}` });
}

function markerPopupTemplate(project) {
	const date = new Date(project.created_on).toLocaleDateString()

	return `
			<div class="marker-popup">
					<header><h3><a href="/project/${project.id}/presentation">${project.name}</a></h3></header>
					<main class="d-flex flex-column">
							<p class="m-0 mb-2 fs-6 fw-bold">Organisation</p>
							<p class="m-0 fs-7">${project.org_name}</p>
							<hr/>
							<p class="m-0 mb-2 fs-6 fw-bold">Lieu</p>
							<p class="m-0 fs-7 text-capitalize">${project?.commune?.name} (${project?.commune?.postal})</p>
							<hr/>
							<p class="m-0 mb-2 fs-6 fw-bold">Date de dépot</p>
							<p class="m-0 fs-7">${date}</p>
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