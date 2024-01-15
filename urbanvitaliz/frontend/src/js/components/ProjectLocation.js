import Alpine from 'alpinejs'

import * as L from 'leaflet';
import 'leaflet-control-geocoder';
import 'leaflet-providers'

import geolocUtils from '../utils/geolocation/'
import mapUtils from '../utils/map/'

function ProjectLocation(projectOptions, modal=true) {
	return {
		mapIsSmall: true,
		project: null,
		mapModal: null,
		staticMap: null,
		interactiveMap: null,
		zoom: 8,
		markers: [],

		async init() {
			this.project = {
				...projectOptions,
				commune: {
					...projectOptions.commune,
					latitude: projectOptions.commune.latitude,
					longitude: projectOptions.commune.longitude
				}
			}
			const { latitude, longitude, insee, name } = this.project.commune;
			this.zoom = latitude && longitude ? this.zoom + 5 : this.zoom;
			const geoData = {}
			try {
				geoData.commune = await geolocUtils.fetchCommuneIgn(insee);
				geoData.location = await geolocUtils.fetchGeolocationByAddress(`${this.project.location} ${name} ${insee}`);
			} catch(e) {
				console.log(e)
			}
			this.initStaticMap(this.project, geoData);
			if(modal) {
				this.initInteractiveMap(this.project, geoData);
			}
		},

		initStaticMap(project, geoData) {
			const options = mapUtils.mapOptions({interactive: false});

			const Map = mapUtils.initMap('map-static', project, options, this.zoom);
			this.staticMap = Map;
			mapUtils.initMapLayers(this.staticMap, project, geoData);
		},

		initInteractiveMap(project, geoData) {
			// Init Interactive Map
			const options = mapUtils.mapOptions({interactive: true});
			const [latitude, longitude] = mapUtils.getDefaultLatLngForMap(project, geoData)

			const Map  = mapUtils.initMap('map-interactive', project, options, this.zoom + 3);
			this.interactiveMap = Map;
			mapUtils.initMapLayers(this.interactiveMap, project, geoData);
			this.interactiveMap.setMinZoom(this.zoom - 7);
			this.interactiveMap.setMaxZoom(this.zoom + 6);
			L.control.zoom({
				position: 'topright'
			}).addTo(this.interactiveMap);
			this.interactiveMap.panTo(new L.LatLng(latitude, longitude));

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