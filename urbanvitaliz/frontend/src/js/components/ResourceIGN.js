import Alpine from 'alpinejs'
import axios from 'axios'

import geolocUtils from '../utils/geolocation/'

const API_IGN_DOWNLOAD = 'https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities'

const API_IGN_DOWNLOAD_2023 = 'https://wxs.ign.fr/essentiels/geoportail/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities'

const API_IGN_TUILES = `https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities`

const API_IGN_TEST_LAYER = `ORTHOIMAGERY.ORTHOPHOTOS`

function ResourceIGN(projectOptions) {
	return {
		mapIsSmall: true,
		project: null,
			staticMap: null,
			interactiveMap: null,
			zoom: 12,
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
				this.initMapIgn()
			} catch(e) {
				console.log(e)
			}
		},

		async getCapabilities() {
			try {
					await axios.get(API_IGN_DOWNLOAD_2023)
			} catch (err) {
					console.error('Error : ', err)
			}
		},

		async initMapIgn() {

			// const options = mapUtils.mapOptions({interactive: false});
        // Documentation : https://geoservices.ign.fr/documentation/services/utilisation-web/extension-pour-leaflet

        // TODO: INtégration IGN mise en pause pour migrtation d'API Geoplateforme : https://geoservices.ign.fr/bascule-vers-la-geoplateforme
        // Next: test APIS https://geoservices.sogefi-sig.com
        // Création de la carte
			const { location_x, location_y  } = this.project;

				const map = L.map('map-static', {
					dragging:false,
					touchZoom:false,
					doubleClickZoom: true,
					scrollWheelZoom: false,
					boxZoom: false,
					keyboard: false,
					zoomControl: false,
					crs : L.geoportalCRS.EPSG2154
			}).setView([location_x, location_y], 5);

			L.tileLayer(
				API_IGN_TUILES,
				{
						minZoom : 0,
						maxZoom : 18,
						tileSize : 256,
						attribution : "IGN-F/Géoportail"
				}).addTo(map)

			// Création de la couche
			const layerTuiles = L.geoportalLayer.WMTS({
					layer: API_IGN_TEST_LAYER,
					minZoom : 0,
					maxZoom : 18,
					tileSize : 256,
			}) ;

			layerTuiles.addTo(map); // ou map.addLayer(lyr);

			// Création et ajout du LayerSwitcher
			// map.addControl(
			// 		L.geoportalControl.LayerSwitcher()
			// );

			this.staticMap = map
		}
	}
}

Alpine.data("ResourceIGN", ResourceIGN)