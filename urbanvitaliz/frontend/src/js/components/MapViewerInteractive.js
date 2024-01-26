import Alpine from 'alpinejs';
import mapUtils from '../utils/map/';

function MapViewerInteractive(projectOptions) {
	return {
		mapIsSmall: false,
		project: null,
		mapModal: null,
		map: null,
		zoom: 8,
		get isLoading() {
			return this.$store.geolocation.isLoading;
		},
		async init() {
			this.project = {
				...projectOptions,
				commune: {
					...projectOptions.commune,
					latitude: projectOptions.commune.latitude,
					longitude: projectOptions.commune.longitude,
				}
			};
			const { latitude, longitude } = this.project.commune;
			this.zoom = latitude && longitude ? this.zoom + 5 : this.zoom;
			const geoData = await this.$store.geolocation.initGeolocationData(this.project);
			this.map = await this.initMap(this.project, geoData);
		},
		async initMap(project, geoData) {
			// Init Interactive Map
			const options = mapUtils.mapOptions({interactive: true});
			const Map = mapUtils.initSatelliteMap('map-interactive', project, options, this.zoom);
			let markers = mapUtils.initMarkerLayer(Map, project, geoData);

			if(!markers || markers.length === 0) 	{
				mapUtils.initMapLayers(Map, project, geoData);
			}
			if(geoData?.parcels) {
				await  mapUtils.addLayerParcels(Map, geoData.parcels);
			}
			Map.setMinZoom(this.zoom - 7);
			Map.setMaxZoom(this.zoom + 6);
			L.control.zoom({
				position: 'topright',
				color: '#335B7E',
			}).addTo(Map);
			const [latitude, longitude] = mapUtils.getDefaultLatLngForMap(project, geoData);
			Map.panTo(new L.LatLng(latitude, longitude));
			this.$store.geolocation.initMapModal(Map);
			return Map;
		},
	};
}

Alpine.data('MapViewerInteractive', MapViewerInteractive);