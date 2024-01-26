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
			this.zoom = latitude && longitude ? this.zoom + 8 : this.zoom;
			const geoData = this.$store.geolocation.getGeoData();
			await this.initMap(this.project, geoData);
		},
		updateProjectLocation(coordinates)  {
			this.project.location_x = coordinates.lng;
			this.project.location_y = coordinates.lat;
		},
		async initMap(project, geoData) {
			if(this.map) {
				return;
			}
			// Init map with base layer
			const options = mapUtils.mapOptions({interactive: true});
			const Map =  await mapUtils.initSatelliteMap('map-edit', project, options, this.zoom);
			this.map = Map;

			// Add onclick behaviour for address input field (geocoderBAN)
			const onClick = (coordinates) => this.updateProjectLocation(coordinates);

			// Add overlay layers (vector maps, controls and markers)
			this.markers  =	mapUtils.initMarkerLayer(this.map, project, geoData);
			const geocoderBAN =	mapUtils.initMapControllerBAN(this.map, geoData, onClick, project, this.markers);
			if(geoData.parcels) {
				await  mapUtils.addLayerParcels(Map, geoData.parcels);
			}

			// Add zoom controls
			this.map.setMinZoom(this.zoom - 7);
			this.map.setMaxZoom(this.zoom + 6);

			L.control.zoom({
				position: 'topright'
			}).addTo(this.map);

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
		},
	};
}

Alpine.data('MapEditor', MapEditor);