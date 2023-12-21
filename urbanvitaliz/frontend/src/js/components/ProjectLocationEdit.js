import Alpine from 'alpinejs'
import geolocUtils from '../utils/geolocation/'
import mapUtils from '../utils/map/'

function ProjectLocationEdit(projectOptions) {
	return {
		mapIsSmall: true,
		project: null,
		map: null,
		zoom: 5,
		markers: [],

		async init() {
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
				geoData.commune = await geolocUtils.fetchCommuneIgn(insee);
				geoData.location = await geolocUtils.fetchGeolocationByAddress(`${this.project.location} ${name ?? ''} ${postal ?? ''}`);
			} catch(e) {
				console.log(e)
			}
			this.initInteractiveMap(this.project, geoData, this.markers);
		},

		updateProjectLocation(coordinates)  {
			this.project.location_x = coordinates.lng
			this.project.location_y = coordinates.lat
		},

		initInteractiveMap(project, geoData, markers) {
			const options = mapUtils.mapOptions({interactive: true});
			if(this.map) {
				return
			}
			const Map = mapUtils.initMap('map-edit', project, options, this.zoom);
			//Center Map
			const onClick = (coordinates) => this.updateProjectLocation(coordinates)
			Map.on('click', function(e) {
				if(markers[0]) {
					markers[0].clearLayers()
				}
				onClick(e.latlng)
				const marker = L.marker(e.latlng, { icon: mapUtils.createMarkerIcon('marker-onclick') }).addTo(Map);
				marker.bindPopup(mapUtils.markerPopupTemplate(project))
				let markerLayer = L.layerGroup([marker]).addTo(Map);
				markers[0] = markerLayer
				Map.panTo(new L.LatLng(e.latlng.lat, e.latlng.lng));
			});
			this.map = Map;
			
			mapUtils.initEditLayers(this.map, project, geoData);
			mapUtils.initMapControllerBAN(this.map, project, geoData, onClick);
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