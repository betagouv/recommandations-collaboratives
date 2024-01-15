import Alpine from 'alpinejs'

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
		isLoading: false,

		get isBusy() {
				return this.isLoading
		},

		async init() {
			this.isLoading = true;
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
				geoData.parcels = await geolocUtils.fetchParcelsIgn(insee);
				geoData.commune = await geolocUtils.fetchCommuneIgn(insee);
				geoData.location = await geolocUtils.fetchGeolocationByAddress(`${this.project.location} ${name} ${insee}`);
			} catch(e) {
				console.log(e)
			}
			await this.initStaticMap(this.project, geoData);
			if(modal) {
				await this.initInteractiveMap(this.project, geoData);
			}

			this.isLoading = false;
		},

		async initStaticMap(project, geoData) {
			const options = mapUtils.mapOptions({interactive: false});

			const Map = await mapUtils.initSatelliteMap('map-static', project, options, this.zoom);
			this.staticMap = Map;
			mapUtils.initMarkerLayer(this.staticMap, project, geoData);
			mapUtils.initMapLayers(this.staticMap, project, geoData);
			setTimeout(function(){Map.invalidateSize()}, 0);
		},

		async initInteractiveMap(project, geoData) {
			// Init Interactive Map
			const options = mapUtils.mapOptions({interactive: true});
			const [latitude, longitude] = mapUtils.getDefaultLatLngForMap(project, geoData)

			const Map  =  mapUtils.initSatelliteMap('map-interactive', project, options, this.zoom + 3);
			this.interactiveMap = Map;
			this.markers = mapUtils.initMarkerLayer(this.interactiveMap, project, geoData);
			if(this.markers.length === 0) 	{
				mapUtils.initMapLayers(this.interactiveMap, project, geoData);
			}
			if(geoData.parcels) {
				await  mapUtils.addLayerParcels(Map, geoData.parcels);
			}
			this.interactiveMap.setMinZoom(this.zoom - 7);
			this.interactiveMap.setMaxZoom(this.zoom + 6);
			L.control.zoom({
				position: 'topright',
				color: '#335B7E',
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