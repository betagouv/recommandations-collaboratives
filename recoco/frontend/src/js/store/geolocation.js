import Alpine from 'alpinejs';
import { Modal } from 'bootstrap';
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
    mapModal: null,
    async initGeolocationData(project) {
      this.isLoading = true;
      this.project = project;
      const { insee } = this.project.commune;
      try {
        [this.parcels, this.commune, this.location] = await Promise.all([
          null, // geolocUtils.fetchParcelsIgn(insee),
          geolocUtils.fetchCommuneIgn(insee),
          geolocUtils.fetchGeolocationByAddress(`${this.project.location}`),
        ]);

        [this.latitude, this.longitude] = mapUtils.getDefaultLatLngForMap(
          this.project
        );

        return {
          parcels: this.parcels,
          commune: this.commune,
          location: this.location,
          latitude: this.latitude,
          longitude: this.longitude,
        };
      } catch (e) {
        console.log(e);
      } finally {
        this.isLoading = false;
      }
    },
    getLatLng() {
      return [this.latitude, this.longitude];
    },
    updateProjectLocation(coordinates) {
      this.longitude = coordinates.lng;
      this.latitude = coordinates.lat;
      this.project.location_x = this.longitude;
      this.project.location_y = this.latitude;
    },
    initMapModal(Map) {
      // Init Modal
      const element = document.getElementById('project-map-modal');
      this.mapModal = new Modal(element);

      element.addEventListener('shown.bs.modal', function (event) {
        setTimeout(function () {
          Map.invalidateSize();
        }, 0);
      });
    },
    getModal() {
      return this.mapModal;
    },
    getProject() {
      return this.project;
    },
  });
});

export default Alpine.store('geolocation');
