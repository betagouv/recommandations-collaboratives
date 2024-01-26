import Alpine from 'alpinejs';
import mapUtils from '../utils/map/';

function MapViewerStatic(projectOptions) {
	return {
		mapIsSmall: true,
		project: null,
		mapModal: null,
		map: null,
		zoom: 8,
		get isLoading() {
			return this.$store.geolocation.isLoading;
		},
		async init() {
			const project = {
				...projectOptions,
				commune: {
					...projectOptions.commune,
					latitude: projectOptions.commune.latitude,
					longitude: projectOptions.commune.longitude,
				}
			};
			this.project = await this.$store.geolocation.initGeolocationData(project);
			const { latitude, longitude } = project.commune;
			this.zoom = latitude && longitude ? this.zoom + 5 : this.zoom;
			this.map = await this.initMap(project);
			this.mapModal = this.$store.geolocation.getModal();
		},
		async initMap(project) {
			const options = mapUtils.mapOptions({interactive: false});
			const geoData = this.$store.geolocation.getGeoData();

			const Map = await mapUtils.initSatelliteMap('map-static', project, options, this.zoom);
			let markers = mapUtils.initMarkerLayer(Map, project, geoData);
			if(!markers || markers.length === 0) 	{
				mapUtils.initMapLayers(Map, project, geoData);
			}
			setTimeout(function(){Map.invalidateSize();}, 10);
			return Map;
		},
		openProjectMapModal() {
			this.mapModal = this.$store.geolocation.getModal();
			this.mapModal.show();
		},
	};
}

Alpine.data('MapViewerStatic', MapViewerStatic);