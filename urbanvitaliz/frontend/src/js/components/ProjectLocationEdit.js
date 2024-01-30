import Alpine from 'alpinejs'
import geolocUtils from '../utils/geolocation/'
import mapUtils from '../utils/map/'

function ProjectLocationEdit(projectOptions) {
	return {
		mapIsSmall: true,
		project: null,
		map: null,
		zoom: 8,
		markers: null,
		isLoading: false,

		async init() {
			this.isLoading = true;
			this.project = {
				...projectOptions,
				commune: {
					...projectOptions.commune,
					latitude: projectOptions.commune.latitude,
					longitude: projectOptions.commune.longitude,
				}
			}
			const { latitude, longitude, insee } = this.project.commune;
			this.zoom = latitude && longitude ? this.zoom + 8 : this.zoom;
			const geoData = {}
			try {
				[geoData.parcels, geoData.commune, geoData.location] = await Promise.all([
					geolocUtils.fetchParcelsIgn(insee),
					geolocUtils.fetchCommuneIgn(insee),
					geolocUtils.fetchGeolocationByAddress(`${this.project.location}`)
				]);
				await this.initInteractiveMap(this.project, geoData);
			} catch(e) {
				// console.log(e)
			} finally {
				this.isLoading = false;
			}
		},

		updateProjectLocation(coordinates)  {
			this.project.location_x = coordinates.lng
			this.project.location_y = coordinates.lat
		},

		async initInteractiveMap(project, geoData) {
			if(this.map) {
				return
			}
			// Init map with base layer
			const options = mapUtils.mapOptions({interactive: true});
			const Map =  await mapUtils.initSatelliteMap('map-edit', project, options, this.zoom);
			this.map = Map;

			// Add onclick behaviour for address input field (geocoderBAN)
			const onClick = (coordinates) => this.updateProjectLocation(coordinates)

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
			const popupOptions = {...project, title: project.name}
			let markers = this.markers
			Map.on('click', function(e) {
				if(markers[0]) {
					markers[0].clearLayers()
				}
				geocoderBAN.setValue('');
				onClick(e.latlng)
				const marker = L.marker(e.latlng, { icon: mapUtils.createMarkerIcon('marker-onclick') }).addTo(Map);
				marker.bindPopup(mapUtils.markerPopupTemplate({...popupOptions,location_x: e.latlng.lng, location_y: e.latlng.lat }))
				let markerLayer = L.layerGroup([marker]).addTo(Map);
				markers[0] = markerLayer
				Map.panTo(new L.LatLng(e.latlng.lat, e.latlng.lng));
			});

			setTimeout(function(){Map.invalidateSize()}, 0);
		},
	}
}


Alpine.data("ProjectLocationEdit", ProjectLocationEdit)