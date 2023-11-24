
import { statusToColorClass } from '../utils/statusToText'
import GeocoderBAN from './geocoderBAN'
import geolocUtils from './geolocation/'

function getDefaultLatLngForMap(project) {
	const longitude = project.location_x ? project.location_x
		: project.commune.latitude ? project.commune.latitude
		: undefined;
	const latitude = project.location_y ? project.location_y
		: project.commune.latitude ? project.commune.latitude
		: undefined;

	return [latitude, longitude]
}

// Map base layer
function initMap(idMap, project, options, zoom) {
	const [latitude, longitude] = getDefaultLatLngForMap(project)
	if(!latitude && !longitude) {
		latitude = geolocUtils.LAT_LNG_FRANCE[0]
		longitude = geolocUtils.LAT_LNG_FRANCE[1]
	}
	L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
		maxZoom: 20,
		attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
	});

	const osm = L.tileLayer.provider('OpenStreetMap.France')

	return L.map(idMap, {...options, layers:[osm]}).setView([latitude, longitude], zoom);
}

// Create layers composed with markers
function initMapLayers(map, project, geoData) {
	try {
		addLayerMarkerProjectCoordinates(map, project);
	} catch (e) {
		console.log(e);
		try {
			addLayerMarkerProjectLocation(map, project, geoData.location);
		} catch(e) {
			console.log(e);
			try {
				addLayerAreaCommune(map, geoData.commune);
			} catch(e) {
				console.log(e);
				if(project.commune.latitude && project.commune.longitude) {
					addLayerAreaCircle(map, project)
				}
			}
		}
	}
}

function initMapControllerBAN(map, project, geoData, onUpdate) {
	GeocoderBAN({ collapsed: false, style: 'searchBar', className: statusToColorClass(project.status), geoData, onUpdate }).addTo(map)
	const controller = document.getElementsByClassName('leaflet-control-geocoder-ban-form');
	controller[0].classList.add('leaflet-control-geocoder-expanded');
	const inputController = controller[0].querySelector('input')
	inputController.addEventListener('blur', async (e) => {
			controller[0].classList.add('leaflet-control-geocoder-expanded');
	})
}

function addLayerMarkerProjectCoordinates(map, project) {
	if(!project.location_x || !project.location_x) {
		throw Error(`Coordonnées de localisation du projet indisponibles pour "${project.name}"`)
	}
	const coordinates = [project.location_x, project.location_y]
	const marker = L.marker(coordinates, { icon: createMarkerIcon(project) }).addTo(map);
	marker.bindPopup(markerPopupTemplate(project))
}

function addLayerMarkerProjectLocation(map, project, geoData) {
	if(geoData.code && geoData.code === 400 || geoData.features.length === 0) {
		throw Error(`Données API Adresse indisponibles pour "${geoData.location}"`)
	}
	const coordinates = geoData.features[0].geometry.coordinates
	const marker = L.marker(coordinates, { icon: createMarkerIcon(project) }).addTo(map);
	marker.bindPopup(markerPopupTemplate(project))
}

function addLayerAreaCommune(map, geoData) {
	if(geoData.code && geoData.code === 400 || geoData.features.length === 0) {
		throw Error(`Données IGN indisponibles pour la commune "${geoData.commune.name}"`)
	}

	L.geoJSON(geoData.features[0].geometry).addTo(map);
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
	return L.divIcon({ className: `map-marker ${statusToColorClass(project.status)}` });
}

function markerPopupTemplate(project) {
	return `
		<div class="marker-popup">
			<header><h6><a href="/project/${project.id}/presentation">${project.name}</a></h6></header>
			<main class="d-flex flex-column">
				<p class="m-0 fs-7 text-capitalize">${project?.commune?.name} (${project?.commune?.postal})</p>
				<p class="m-0 fs-7 text-capitalize">Coordonnées géographiques (X) (${project?.location_x})</p>
				<p class="m-0 fs-7 text-capitalize">Coordonnées géographiques (y) (${project?.location_y})</p>
			</main>
		</div>
	`
}

function mapOptions({interactive, zoom}) {
	return {
		dragging: interactive,
		touchZoom: interactive,
		doubleClickZoom: interactive,
		scrollWheelZoom: false,
		boxZoom: interactive,
		keyboard: interactive,
		zoomControl: zoom,
	}
}

export default {
	initMap,
	initMapLayers,
	initMapControllerBAN,
	addLayerAreaCommune,
	addLayerAreaCircle,
	addLayerMarkerProjectLocation,
	mapOptions,
	getDefaultLatLngForMap
}