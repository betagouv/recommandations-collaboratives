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
				location_x: projectOptions.location_x ? parseFloat(projectOptions.location_x) : null,
				location_y: projectOptions.location_y ? parseFloat(projectOptions.location_y) : null,
				commune: {
					...projectOptions.commune,
					latitude: projectOptions.commune.latitude ? parseFloat(projectOptions.commune.latitude) : null,
					longitude: projectOptions.commune.longitude ? parseFloat(projectOptions.commune.longitude) : null,
				}
			}
			const { latitude, longitude, insee } = this.project.commune;
			this.zoom = latitude && longitude ? 11 : this.zoom;

			const geoData = {}

			geoData.commune = await geolocUtils.fetchCommuneIgn(insee);
			geoData.location = await geolocUtils.fetchGeolocationByAddress(this.project.location);
			this.initInteractiveMap(this.project, geoData);
		},

		updateProjectLocation(coordinates)  {
			// TODO: fix Save coordinates for project (depends on backend model update)
			this.project.location_x = coordinates[0]
			this.project.location_y = coordinates[1]
			console.log('updateProjectLocation(coordinates)');
			console.log(this.project.location_x );
			console.log(this.project.location_y );
			console.log('updateProjectLocation(coordinates)');
			console.log(coordinates);
		},

		initInteractiveMap(project, geoData) {
			const options = mapUtils.mapOptions({interactive: true, zoom:true});
			const [latitude, longitude] = mapUtils.getDefaultLatLngForMap(project)

			const Map = mapUtils.initMap('map-location-edit', project, options, this.zoom);
			mapUtils.initMapLayers(Map, project, geoData);

			//Center Map
			const onClick = (coordinates) => this.updateProjectLocation(coordinates)
			mapUtils.initMapLayers(Map, project, geoData);
			mapUtils.initMapControllerBAN(Map, project, geoData, onClick);

			Map.on('click', function(e) {
				onClick(e.latlng)
			});
			Map.panTo(new L.LatLng(latitude, longitude));
			setTimeout(function(){Map.invalidateSize()}, 0);
			this.map = Map;
		},
	}
}


Alpine.data("ProjectLocationEdit", ProjectLocationEdit)