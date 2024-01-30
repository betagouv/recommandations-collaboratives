import * as L from 'leaflet';
import 'leaflet-control-geocoder';
import 'leaflet-providers';

import GeocoderBAN from './geocoderBAN';
import geolocUtils from './geolocation/';

function mapLayerStyles(className) {
	return {
		className,
		color: '#F6F6F6',
		fillColor: '#929292',
		stroke: true,
		weight: 1.25,
		fillOpacity: 0.25,
	};
}

function ignServiceURL(
	layer,
	env = 'decouverte',
	format = 'image/png'
) {
	const url = `https://wxs.ign.fr/${env}/geoportail/wmts`;
	const query =
		'service=WMTS&request=GetTile&version=1.0.0&tilematrixset=PM&tilematrix={z}&tilecol={x}&tilerow={y}&style=normal';

	return `${url}?${query}&layer=${layer}&format=${format}`;
}

function getDefaultLatLngForLayers(project, geoData) {
	const longitude = project.location_x ? project.location_x
		: geoData.location.longitude ? geoData.location.longitude
			: undefined;
	const latitude = project.location_y ? project.location_y
		: geoData.location.latitude ? geoData.location.latitude
			: undefined;

	return [latitude, longitude];
}

function getDefaultLatLngForMap(project) {
	const longitude = project.location_x ? project.location_x
		: project.commune.longitude ? project.commune.longitude
			: geolocUtils.LAT_LNG_FRANCE[1];
	const latitude = project.location_y ? project.location_y
		: project.commune.latitude ? project.commune.latitude
			: geolocUtils.LAT_LNG_FRANCE[0];

	return [latitude, longitude];
}

// Map creation shortcuts
function makeMap(idMap, project, options, zoom) {
    const [latitude, longitude] = getDefaultLatLngForMap(project);

    var map = new L.map(idMap, {...options});


    /* If Satellite isn't available, add OSM tiles as backup */
    var osmLayer = initMapLayer(latitude, longitude, zoom);
    if (osmLayer)
        map.addLayer(osmLayer);

    var satelliteLayer = initSatelliteLayer(latitude, longitude, zoom);
    if (satelliteLayer)
        map.addLayer(satelliteLayer);

    map.setView(new L.LatLng(latitude, longitude), zoom);

    // geolocUtils.createPolygonFromBounds(map, geolocUtils.IGN_BBOX).addTo(map);


    return map;

}

// Map base layer
function initMapLayer(lat, lng, zoom) {
    console.debug("initializing OSM layer...");
	return L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
		maxZoom: 20,
		attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
	});

}

function initSatelliteLayer(lat, lng, zoom) {

  if (!geolocUtils.IGN_BBOX.contains(new L.LatLng(lat, lng))) {
    console.warn("Coordinates outside of IGN Tiles range, stopping initialization");
    return null;
  }

    console.debug("initializing Satellite layer...");
	return L.tileLayer(
		ignServiceURL('ORTHOIMAGERY.ORTHOPHOTOS', 'essentiels', 'image/jpeg'), {
			minZoom : 0,
			maxZoom : 20,
			tileSize: 256,
			attribution : 'IGN-F/Géoportail'
		});

}


// Create layers composed with markers
function initMarkerLayer(map, project, geoData) {
	let markers = [];
	let marker;
	try {
		marker = addLayerMarkerProjectCoordinates(map, project);
		markers[0] = marker;
		let markerLayer = L.layerGroup(markers).addTo(map);
		return [markerLayer];
	} catch (e) {
		try {
			marker = addLayerMarkerProjectLocation(map, project, geoData);
			markers[0] = marker;
			let markerLayer = L.layerGroup(markers).addTo(map);
			return [markerLayer];
		} catch(e) {
			return markers;
		}
	}
}

// Create layers composed with area coordinates
function initMapLayers(map, project, geoData) {
	try {
		let commune = geoData.commune ? geoData.commune
			: project.commune ?  project.commune
				: null;
		if(commune) {
			addLayerAreaCommune(map, commune);
		}
	} catch(e) {
		if(project.commune.latitude && project.commune.longitude) {
			addLayerAreaCircle(map, project);
		}
	}
}

function initMapControllerBAN(map,  geoData, onUpdate, project, markers) {
	const className = 'marker-onclick';;
	const popupOptions = {...project, title: project.title};
	const geocoderOptions = {
		collapsed: false,
		style: 'searchBar',
		className,
		geoData,
		onUpdate,
		markerIcon: createMarkerIcon(className),
		markerPopupTemplate,
		commune: project.commune,
		popupOptions,
		markers
	};
	const geocodeBAN = GeocoderBAN(geocoderOptions).addTo(map);
	const controller = document.getElementsByClassName('leaflet-control-geocoder-ban-form');
	controller[0].classList.add('leaflet-control-geocoder-expanded');
	const inputController = controller[0].querySelector('input');
	inputController.addEventListener('blur', async (e) => {
		controller[0].classList.add('leaflet-control-geocoder-expanded');
	});

	return geocodeBAN;
}


function addLayerMarkerProjectCoordinates(map, project) {
	if(!project.location_x || !project.location_x) {
		throw Error(`Coordonnées de localisation du projet indisponibles pour "${project.name}"`);
	}
	const coordinates = [project.location_y, project.location_x];
	const marker = L.marker(coordinates, { icon: createMarkerIcon('project-coordinates-marker') }).addTo(map);
	const popupOptions = {...project, title: project.name};
	marker.bindPopup(markerPopupTemplate(popupOptions));
	L.layerGroup([marker]).addTo(map);
	map.panTo(new L.LatLng(...coordinates));
	return marker;
}

function addLayerMarkerProjectLocation(map, project, geoData) {
	if(geoData.code && geoData.code === 400 ) {
		throw Error(`Données API Adresse indisponibles pour "${project.name}"`)
	}
	const locationData =  geoData.location?.features ?  geoData.location : geoData
	if(locationData.features?.length !== 1) {
		throw Error(`Données API Adresse indisponibles pour "${project.name}"`)
	}
	const popupOptions = {...project, title: project.name}
	const coordinates = geoData.location.features[0].geometry.coordinates.reverse()
	const marker = L.marker(coordinates, { icon: createMarkerIcon('project-location-marker') }).addTo(map);
	marker.bindPopup(markerPopupTemplate(popupOptions))
	map.panTo(new L.LatLng(...coordinates));
	return marker
}

function addLayerAreaCommune(map, geoData) {
	if(geoData.code && geoData.code === 400 || geoData.features.length === 0) {
		throw Error(`Données IGN indisponibles pour la commune "${geoData.commune.name}"`)
	}

	L.geoJSON(geoData.features[0].geometry, mapLayerStyles('area-commune')).addTo(map);
}

// Create layers composed with markers
function addLayerAreaCircle(map, project) {
	const { latitude, longitude } = project.commune;
	L.circle([latitude, longitude], {
		... mapLayerStyles('area-circle'),
			radius: 5000,
	}).addTo(map);
}

// Create layers composed with markers
function addLayerParcels(map,  geoData) {
	if(geoData.code && geoData.code === 400 || geoData.features?.length === 0) {
		throw Error(`Données parcelaires indisponibles pour la commune "${geoData.commune.name}"`)
	}
	const parcelLayer = L.geoJSON(geoData.parcels, mapLayerStyles('area-parcels'));
	const overlayMap = {
    "Parcelles": parcelLayer
	};
	L.control.layers(null, overlayMap).addTo(map);
}

function createMarkerIcon(className, title) {
	return L.divIcon({ className: `map-marker ${className}`,title });
}

function markerPopupTemplate({location_x, location_y, name, location, commune, address, title}) {
	const lat = location_x ? `<p data-test-id="project-coord-x-latitude" class="m-0 fs-7 text-capitalize">Lat: ${Number.parseFloat(location_x).toFixed(2)}</p>` : '';
	const lng = location_y ? `<p data-test-id="project-coord-y-longitude" class="m-0 fs-7 text-capitalize">Lng: ${Number.parseFloat(location_y).toFixed(2)}</p>` : '';

	let popupAddress = '';
	if(address){
		popupAddress = `<p class="m-0 fs-7">${address}</p>`;
	}
	else if(location){
		popupAddress = `<p class="m-0 fs-7">${location}</p>`;
	}

	if (commune){
		popupAddress =`${popupAddress}<p class="m-0 fs-7 text-capitalize">${commune.name} (${commune.postal})</p>`;
	}

	const popupTitle = title ? title : name;
	return `
		<div class="marker-popup">
			<header><h6>${popupTitle}</a></h6></header>
			<main class="d-flex flex-column">
				${popupAddress}
				${lat}
				${lng}
			</main>
		</div>
	`;
}

function mapOptions({interactive, zoom}) {
	return {
		dragging: interactive,
		touchZoom: interactive,
		doubleClickZoom: interactive,
		scrollWheelZoom: interactive,
		boxZoom: interactive,
		keyboard: interactive,
		zoomControl: zoom,
	};
}

export default {
  makeMap,
	initMapLayer,
	initSatelliteLayer,
	initMarkerLayer,
	initMapLayers,
	initMapControllerBAN,
	addLayerParcels,
	addLayerAreaCommune,
	addLayerAreaCircle,
	addLayerMarkerProjectLocation,
	mapOptions,
	getDefaultLatLngForMap,
	getDefaultLatLngForLayers,
	createMarkerIcon,
	markerPopupTemplate,
};
