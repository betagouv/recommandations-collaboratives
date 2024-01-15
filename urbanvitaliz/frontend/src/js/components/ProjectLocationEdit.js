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
					longitude: projectOptions.commune.longitude,
				}
			}
			const { latitude, longitude, insee, name, postal } = this.project.commune;
			this.zoom = latitude && longitude ? this.zoom + 8 : this.zoom;
			const geoData = {}
			try {
				geoData.parcels = await geolocUtils.fetchParcelsIgn(insee);
				geoData.commune = await geolocUtils.fetchCommuneIgn(insee);
				geoData.location = await geolocUtils.fetchGeolocationByAddress(this.project.location, {name, insee, postal});
			} catch(e) {
				console.log(e)
			}
			await this.initInteractiveMap(this.project, geoData);

			this.isLoading = false;
		},

		updateProjectLocation(coordinates)  {
			this.project.location_x = coordinates.lng
			this.project.location_y = coordinates.lat
		},

		async initInteractiveMap(project, geoData) {
			const options = mapUtils.mapOptions({interactive: true});
			if(this.map) {
				return
			}

			const Map =  mapUtils.initSatelliteMap('map-edit', project, options, this.zoom);
			this.map = Map;
			const popupOptions = {...project, title: project.name}

			//Center Map
			const onClick = (coordinates) => this.updateProjectLocation(coordinates)


			this.markers  =	mapUtils.initMarkerLayer(this.map, project, geoData);
			let markers = this.markers

			Map.on('click', function(e) {
				if(markers[0]) {
					markers[0].clearLayers()
				}
				onClick(e.latlng)
				const marker = L.marker(e.latlng, { icon: mapUtils.createMarkerIcon('marker-onclick') }).addTo(Map);
				marker.bindPopup(mapUtils.markerPopupTemplate({...popupOptions,location_x: e.latlng.lng, location_y: e.latlng.lat }))
				let markerLayer = L.layerGroup([marker]).addTo(Map);
				markers[0] = markerLayer
				Map.panTo(new L.LatLng(e.latlng.lat, e.latlng.lng));
			});

			mapUtils.initMapControllerBAN(this.map, geoData, onClick, project, this.markers);

			if(geoData.parcels) {
				await  mapUtils.addLayerParcels(Map, geoData.parcels);
			}

			this.map.setMinZoom(this.zoom - 7);
			this.map.setMaxZoom(this.zoom + 6);
			L.control.zoom({
				position: 'topright'
			}).addTo(this.map);

			setTimeout(function(){Map.invalidateSize()}, 0);
		},
	}
}


Alpine.data("ProjectLocationEdit", ProjectLocationEdit)