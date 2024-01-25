import Alpine from 'alpinejs'

import geolocUtils from '../utils/geolocation/'
import mapUtils from '../utils/map/'

function MapViewerStatic(projectOptions) {
	return {
		mapIsSmall: true,
		project: null,
		mapModal: null,
		map: null,
		zoom: 8,
		isLoading: false,

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
			const { latitude, longitude, insee } = this.project.commune;
			this.zoom = latitude && longitude ? this.zoom + 5 : this.zoom;
			const geoData = {}


			try {
				[geoData.parcels, geoData.commune, geoData.location] = await Promise.all([
					geolocUtils.fetchParcelsIgn(insee),
					geolocUtils.fetchCommuneIgn(insee),
					geolocUtils.fetchGeolocationByAddress(`${this.project.location}`)
				]);
			} catch(e) {
				// console.log(e)
			} finally {
				this.isLoading = false;
			}
			await this.initStaticMap(this.project, geoData);
			let map = this.map
			setTimeout(function(){map.invalidateSize()}, 0);
		},

		async initStaticMap(project, geoData) {
			const options = mapUtils.mapOptions({interactive: false});

			const Map = await mapUtils.initSatelliteMap('map-static', project, options, this.zoom);
			this.map = Map;
			let markers = mapUtils.initMarkerLayer(this.map, project, geoData);
			if(!markers || markers.length === 0) 	{
				mapUtils.initMapLayers(this.map, project, geoData);
			}
		},


		initMapModal() {
			// Init Modal
			const element = document.getElementById("project-map-modal");
			this.mapModal = new bootstrap.Modal(element);
		},

		openProjectMapModal() {
			this.mapModal.show();
		},
	}
}


Alpine.data("MapViewerStatic", MapViewerStatic)