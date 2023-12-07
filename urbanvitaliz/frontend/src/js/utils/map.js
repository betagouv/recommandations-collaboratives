
import GeocoderBAN from './geocoderBAN'
import geolocUtils from './geolocation/'


function getDefaultLatLngForLayers(project, geoData) {
	const longitude = project.location_x ? project.location_x
	: geoData.location.longitude ? geoData.location.longitude
		: undefined;
	const latitude = project.location_y ? project.location_y
	: geoData.location.latitude ? geoData.location.latitude
		: undefined;

	return [latitude, longitude]
}

function getDefaultLatLngForMap(project) {
	const longitude = project.location_x ? project.location_x
		: project.commune.longitude ? project.commune.longitude
		: geolocUtils.LAT_LNG_FRANCE[0];
	const latitude = project.location_y ? project.location_y
		: project.commune.latitude ? project.commune.latitude
		: geolocUtils.LAT_LNG_FRANCE[0];

	return [latitude, longitude]
}

// Map base layer
function initMap(idMap, project, options, zoom) {
	const [latitude, longitude] = getDefaultLatLngForMap(project)
	L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
		maxZoom: 20,
		attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
	});

	const osm = L.tileLayer.provider('OpenStreetMap.France')

	return L.map(idMap, {...options, layers:[osm]}).setView(new L.LatLng(latitude, longitude), zoom);
}

// Create layers composed with markers
function initMapLayers(map, project, geoData) {
	try {
		addLayerMarkerProjectCoordinates(map, project);
	} catch (e) {
		try {
			addLayerMarkerProjectLocation(map, project, geoData);
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
}

function initMapControllerBAN(map, project, geoData, onUpdate) {
	const geocoderOptions = {
		collapsed: false,
		style: 'searchBar',
		className: 'location-edit-marker',
		geoData,
		onUpdate,
		markerIcon: createMarkerIcon(project),
		markerPopupTemplate
	}
	GeocoderBAN(geocoderOptions).addTo(map)
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
	const coordinates = [project.location_y, project.location_x]
	const marker = L.marker(coordinates, { icon: createMarkerIcon('project-coordinates-marker') }).addTo(map);
	marker.bindPopup(markerPopupTemplate(project))
	L.layerGroup([marker]).addTo(map);
	map.panTo(new L.LatLng(...coordinates));
}

function addLayerMarkerProjectLocation(map, project, geoData) {
	if(geoData.code && geoData.code === 400 || geoData.features.length !== 1) {
		throw Error(`Données API Adresse indisponibles pour "${project.name}"`)
	}
	const coordinates = geoData.features[0].coordinates
	const marker = L.marker(coordinates, { icon: createMarkerIcon('project-location-marker') }).addTo(map);
	marker.bindPopup(markerPopupTemplate(project))
	map.panTo(new L.LatLng(...coordinates));
}

function addLayerAreaCommune(map, geoData) {
	if(geoData.code && geoData.code === 400 || geoData.features.length === 0) {
		throw Error(`Données IGN indisponibles pour la commune "${geoData.commune.name}"`)
	}

	L.geoJSON(geoData.features[0].geometry, {className: 'area-commune'}).addTo(map);
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

function createMarkerIcon(className) {
	return L.divIcon({ className: `map-marker ${className}` });
}

function markerPopupTemplate(project) {
	const lat = project?.location_x ? `<p data-test-id="project-coord-x-latitude" class="m-0 fs-7 text-capitalize">Lat: ${Number.parseFloat(project?.location_x).toFixed(2)}</p>` : ''
	const lng = project?.location_x ? `<p data-test-id="project-coord-y-longitude" class="m-0 fs-7 text-capitalize">Lng: ${Number.parseFloat(project?.location_y).toFixed(2)}</p>` : ''
	const address = project?.location?.commune  ?`<p class="m-0 fs-7 text-capitalize">${project?.commune?.name} (${project?.commune?.postal})</p>` : ''
	return `
		<div class="marker-popup">
			<header><h6>${project.name}</a></h6></header>
			<main class="d-flex flex-column">
				${address}
				${lat}
				${lng}
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
	getDefaultLatLngForMap,
	getDefaultLatLngForLayers,
	createMarkerIcon,
	markerPopupTemplate
}