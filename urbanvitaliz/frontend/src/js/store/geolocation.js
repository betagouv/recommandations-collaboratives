import Alpine from 'alpinejs';

import geolocUtils from '../utils/geolocation/';
import mapUtils from '../utils/map/';

document.addEventListener('alpine:init', () => {

	Alpine.store('geolocation', {
		project: null,
		parcels: null,
		commune: null,
		location: null,
		latitude: null,
		longitude: null,
		isLoading: false,
		mapStatic: null,
		mapViewer: null,
		mapEditor: null,
		zoom: 8,
		modal: null,

		async initGeolocationData(project) {
			if(this.project?.id !== project.id) {
				this.isLoading = true;
				this.project = project;
				const { insee } = this.project.commune;
				try {
					this.parcels = await geolocUtils.fetchParcelsIgn(insee);
					this.commune = await geolocUtils.fetchCommuneIgn(insee);
					this.location = await geolocUtils.fetchGeolocationByAddress(this.project.location);
					[this.latitude, this.longitude] = mapUtils.getDefaultLatLngForMap(this.project);
				} catch(e) {
					console.log(e);
				}
				finally{
					this.isLoading = false;
				}
			}
		},
		getLatLng() {
			return [this.latitude, this.longitude];
		},
		getGeoData() {
			return {  
				parcels: this.parcels,
				commune: this.commune,
				location: this.location,
				latitude: this.latitude,
				longitude: this.longitude,
			}
		},
		updateProjectLocation(coordinates)  {
			this.longitude = coordinates.lng;
			this.latitude = coordinates.lat;
		},
	})
})

export default Alpine.store('geolocation');
