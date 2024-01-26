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
		async initGeolocationData(project) {
			if(!this.project || this.project?.id !== project.id) {
				this.isLoading = true;
				this.project = project;
				const { insee } = this.project.commune;
				try {
					[this.parcels, this.commune, this.location] = await Promise.all([
						geolocUtils.fetchParcelsIgn(insee),
						geolocUtils.fetchCommuneIgn(insee),
						geolocUtils.fetchGeolocationByAddress(`${this.project.location}`)
					]);
					[this.latitude, this.longitude] = mapUtils.getDefaultLatLngForMap(this.project);
				} catch(e) {
					console.log(e);
				} finally {
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
			};
		},
		updateProjectLocation(coordinates)  {
			this.longitude = coordinates.lng;
			this.latitude = coordinates.lat;
			this.project.location_x = this.longitude;
			this.project.location_y = this.latitude;
		},
	});
});

export default Alpine.store('geolocation');
