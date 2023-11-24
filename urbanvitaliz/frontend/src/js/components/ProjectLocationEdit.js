import Alpine from 'alpinejs'

import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css'
import 'leaflet-control-geocoder';
import 'leaflet-providers'

import geolocUtils from '../utils/geolocation/'
import mapUtils from '../utils/map/'

function ProjectLocationEdit(projectOptions) {
	return {
		mapIsSmall: true,
		project: null,
		map: null,
		zoom: 5,

		async init() {
			this.project = {
				...projectOptions,
				commune: {
					...projectOptions.commune,
					latitude: projectOptions.commune.latitude,
					longitude: projectOptions.commune.longitude,
				}
			}
			const { latitude, longitude, insee } = this.project.commune;
			this.zoom = latitude && longitude ? this.zoom + 6 : this.zoom;
			
			const geoData = {}

			geoData.commune = await geolocUtils.fetchCommuneIgn(insee);
			geoData.location = await geolocUtils.fetchGeolocationByAddress(this.project.location);
			this.initInteractiveMap(this.project, geoData);
		},

		updateProjectLocation(coordinates)  {
			this.project.location_x = coordinates.lng
			this.project.location_y = coordinates.lat
		},

		initInteractiveMap(project, geoData) {
			const options = mapUtils.mapOptions({interactive: true});

			const Map = mapUtils.initMap('map-location-edit', project, options, this.zoom);
			//Center Map
			const onClick = (coordinates) => this.updateProjectLocation(coordinates)
			Map.on('click', function(e) {
				onClick(e.latlng)
			});
			this.map = Map;
			
			mapUtils.initMapLayers(this.map, project, geoData);
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