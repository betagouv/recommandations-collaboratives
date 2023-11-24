import Alpine from 'alpinejs'

import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css'
import 'leaflet-control-geocoder';
import 'leaflet-providers'

import geolocUtils from '../utils/geolocation/'
import mapUtils from '../utils/map/'

function ProjectLocation(projectOptions) {
	return {
		mapIsSmall: true,
		project: null,
		mapModal: null,
		staticMap: null,
		interactiveMap: null,
		zoom: 5,

		async init() {
			this.project = {
				...projectOptions,
				location_x: projectOptions.location_x ? parseFloat(projectOptions.location_x) : null,
				location_y: projectOptions.location_y ? parseFloat(projectOptions.location_y) : null,
				commune: {
					...projectOptions.commune,
					latitude: projectOptions.commune.latitude ? parseFloat(projectOptions.commune.latitude) : null,
					longitude: projectOptions.commune.longitude ? parseFloat(projectOptions.commune.longitude) : null,
				}
			}
			const { latitude, longitude, insee } = this.project.commune;
			this.zoom = latitude && longitude ? 11 : this.zoom;

			const geoData = {}
			geoData.commune = await geolocUtils.fetchCommuneIgn(insee);
			geoData.location = await geolocUtils.fetchGeolocationByAddress(this.project.location);
			this.initStaticMap(this.project, geoData);
			this.initInteractiveMap(this.project, geoData);
		},

		initStaticMap(project, geoData) {
			const options = mapUtils.mapOptions({interactive: false});
			const [latitude, longitude] = mapUtils.getDefaultLatLngForMap(project)

			const Map  = mapUtils.initMap('map-static', project, options, this.zoom);
			mapUtils.initMapLayers(Map, project, geoData);

			// forces map redraw to fit container
			Map.panTo(new L.LatLng(latitude, longitude));
			setTimeout(function(){Map.invalidateSize()}, 0);
			this.staticMap = Map;
		},

		initInteractiveMap(project, geoData) {
			// Init Interactive Map
			const options = mapUtils.mapOptions({interactive: true});
			const zoom = this.zoom + 1;
			const [latitude, longitude] = mapUtils.getDefaultLatLngForMap(project)

			const Map  = mapUtils.initMap('map-modal', project, options, zoom);
			mapUtils.initMapLayers(Map, project, geoData);
			Map.setMinZoom(zoom - 7);
			Map.setMaxZoom(zoom + 6);
			Map.panTo(new L.LatLng(latitude, longitude));
			Map.setView([latitude, longitude]);
			this.interactiveMap = Map;

			// Init Modal
			const element = document.getElementById("project-map-modal");
			this.mapModal = new bootstrap.Modal(element);
			element.addEventListener('shown.bs.modal', function (event) {
				 // forces map redraw to fit container
				setTimeout(function(){Map.invalidateSize()}, 0);
			})
		},

		openProjectMapModal() {
			this.mapIsSmall = false;
			this.mapModal.show();
		},
	}
}


Alpine.data("ProjectLocation", ProjectLocation)