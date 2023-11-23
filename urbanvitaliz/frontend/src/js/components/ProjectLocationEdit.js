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
		editLocationModal: null,
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
			const options = mapUtils.mapOptions({interactive: true, zoom:false});
			const { latitude, longitude, insee } = this.project.commune;


			this.zoom = latitude && longitude ? 11 : this.zoom;

			const geoData = {}

			geoData.commune = await geolocUtils.fetchCommuneIgn(insee);
			geoData.location = await geolocUtils.fetchGeolocationByAddress(this.project.location);

			const Map = mapUtils.initMap('map-location-edit', this.project, options, this.zoom);
			mapUtils.initMapLayers(Map, this.project, geoData);

			// forces map redraw to fit container
			setTimeout(function(){Map.invalidateSize()}, 0);

			//Center Map
			Map.panTo(new L.LatLng(latitude, longitude));
			this.map = Map;
			this.initLocationEditMap(this.project, geoData);
		},

		openEditLocationModal() {
			this.mapIsSmall = false;
			this.editLocationModal.show();
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

		initLocationEditMap(project, geoData) {
			const onClick = (coordinates) => this.updateProjectLocation(coordinates)
			mapUtils.initMapLayers(this.map, project, geoData);
			mapUtils.initMapControllerBAN(this.map, project, geoData, onClick);

			this.map.on('click', function(e) {
				onClick(e.latlng)
			});
			const map = this.map;

			setTimeout(function(){map.invalidateSize()}, 0);
		},
	}
}


Alpine.data("ProjectLocationEdit", ProjectLocationEdit)