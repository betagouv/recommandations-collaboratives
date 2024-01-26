import Alpine from 'alpinejs';
import mapUtils from '../utils/map/';

function MapEditor(projectOptions) {
	return {
		mapIsSmall: true,
		project: null,
		map: null,
		zoom: 8,
		markers: null,
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
			const { latitude, longitude } = this.project.commune;
			this.zoom = latitude && longitude ? this.zoom + 8 : this.zoom;
			const geoData = this.$store.geolocation.getGeoData();
			this.map = await this.initMap(this.project, geoData);
		},
		updateProjectLocation(coordinates)  {
			this.$store.geolocation.updateProjectLocation(coordinates);
			this.project.location_x = this.$store.geolocation.project.location_x;
			this.project.location_y = this.$store.geolocation.project.location_y;
		},
		async initMap(project, geoData) {
			// Init map with base layer
			const options = mapUtils.mapOptions({interactive: true});
			const Map =  await mapUtils.initSatelliteMap('map-edit', project, options, this.zoom);

			// Add onclick behaviour for address input field (geocoderBAN)
			const onClick = (coordinates) => this.updateProjectLocation(coordinates);

			// Add overlay layers (vector maps, controls and markers)
			this.markers  =	mapUtils.initMarkerLayer(Map, project, geoData);

			const geocoderBAN =	mapUtils.initMapControllerBAN(Map, geoData, onClick, project, this.markers);
			if(geoData.parcels) {
				await  mapUtils.addLayerParcels(Map, geoData.parcels);
			}

			// Add zoom controls
			Map.setMinZoom(this.zoom - 7);
			Map.setMaxZoom(this.zoom + 6);

			L.control.zoom({
				position: 'topright'
			}).addTo(Map);

			// Add onclick behaviour for map
			const popupOptions = {...project, title: project.name};
			let markers = this.markers;
			Map.on('click', function(e) {
				if(markers && markers[0]) {
					markers[0].clearLayers();
				} else {
					markers = [];
				}
				geocoderBAN.setValue('');
				onClick(e.latlng);
				const marker = L.marker(e.latlng, { icon: mapUtils.createMarkerIcon('marker-onclick') }).addTo(Map);
				marker.bindPopup(mapUtils.markerPopupTemplate({...popupOptions,location_x: e.latlng.lng, location_y: e.latlng.lat }));
				let markerLayer = L.layerGroup([marker]).addTo(Map);
				markers[0] = markerLayer;
				Map.panTo(new L.LatLng(e.latlng.lat, e.latlng.lng));
			});
			setTimeout(function(){Map.invalidateSize();}, 0);

			return Map;
		},
	};
}

Alpine.data('MapEditor', MapEditor);