import Alpine from 'alpinejs'
import axios from 'axios'

import geolocUtils from '../utils/geolocation/'
import mapUtils from '../utils/map/'

const API_IGN_DOWNLOAD = 'https://data.geopf.fr/telechargement/capabilities'
function ResourceIGN(projectOptions) {
	return {
		mapIsSmall: true,
		project: null,
			staticMap: null,
			interactiveMap: null,
			zoom: 6,
			markers: [],
			capabilities: null,
			async init() {
					this.capabilities = await this.getCapabilities()

					console.log('this.capabilities ');
					console.log(this.capabilities );

			this.project = {
				...projectOptions,
				commune: {
					...projectOptions.commune,
					latitude: projectOptions.commune.latitude,
					longitude: projectOptions.commune.longitude
				}
			}
			const { latitude, longitude, insee, name } = this.project.commune;
			this.zoom = latitude && longitude ? this.zoom + 5 : this.zoom;
			const geoData = {}
			try {
				geoData.commune = await geolocUtils.fetchCommuneIgn(insee);
				geoData.location = await geolocUtils.fetchGeolocationByAddress(`${this.project.location} ${name} ${insee}`);
			} catch(e) {
				console.log(e)
			}
		},
		async getCapabilities() {
			try {
					await axios.get(API_IGN_DOWNLOAD)
			} catch (err) {
					console.error('Error : ', err)
			}
		},
	}
}

Alpine.data("ResourceIGN", ResourceIGN)