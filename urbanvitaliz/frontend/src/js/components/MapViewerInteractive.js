import Alpine from 'alpinejs';
import mapUtils from '../utils/map/';

function MapViewerInteractive(projectOptions) {
	return {
		mapIsSmall: false,
		project: null,
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
			await this.$store.geolocation.initGeolocationData(this.project);
			const { latitude, longitude } = this.project.commune;
			this.zoom = latitude && longitude ? this.zoom + 5 : this.zoom;
			const geoData = this.$store.geolocation.getGeoData();
			this.map = await this.initMap(this.project, geoData);
		},
		async initMap(project, geoData) {
			// Init Interactive Map
			const options = mapUtils.mapOptions({interactive: true});
			const [latitude, longitude] = mapUtils.getDefaultLatLngForMap(project, geoData);

			const Map = mapUtils.initSatelliteMap('map-interactive', project, options, this.zoom + 3);
			let markers = mapUtils.initMarkerLayer(this.map, project, geoData);
			if(!markers || markers.length === 0) 	{
				mapUtils.initMapLayers(Map, project, geoData);
			}
			if(geoData.parcels) {
				await  mapUtils.addLayerParcels(Map, geoData.parcels);
			}
			Map.setMinZoom(this.zoom - 7);
			Map.setMaxZoom(this.zoom + 6);
			L.control.zoom({
				position: 'topright',
				color: '#335B7E',
			}).addTo(Map);
			Map.panTo(new L.LatLng(latitude, longitude));

			// Init Modal
			const element = document.getElementById('project-map-modal');
			this.mapModal = new bootstrap.Modal(element);
			element.addEventListener('shown.bs.modal', function (event) {
				 // forces map redraw to fit container
				setTimeout(function(){Map.invalidateSize();}, 0);
			});
			return Map;
		},
	};
}

Alpine.data('MapViewerInteractive', MapViewerInteractive);