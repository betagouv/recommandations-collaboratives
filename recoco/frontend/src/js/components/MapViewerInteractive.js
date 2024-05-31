import Alpine from 'alpinejs';
import mapUtils from '../utils/map/';

function MapViewerInteractive(projectOptions) {
  return {
    mapIsSmall: false,
    project: null,
    mapModal: null,
    map: null,
    zoom: 11,
    get isLoading() {
      return this.$store.geolocation.isLoading;
    },
    async init() {
      this.project = {
        ...projectOptions,
        commune: {
          ...projectOptions.commune,
          latitude: projectOptions.commune.latitude,
          longitude: projectOptions.commune.longitude,
        },
      };
      const latitude = this.project.location_x;
      const longitude = this.project.location_y;
      this.zoom = latitude && longitude ? this.zoom + 7 : this.zoom;

      const geoData = await this.$store.geolocation.initGeolocationData(
        this.project
      );

      this.map = await this.initMap(this.project, geoData);
    },
    async initMap(project, geoData) {
      // Init Interactive Map
      const options = mapUtils.mapOptions({
        interactive: true,
        minZoom: 8,
        maxZoom: 20,
      });

      var map = mapUtils.makeMap(
        'map-interactive',
        project,
        options,
        this.zoom
      );

      let markers = mapUtils.initMarkerLayer(map, project, geoData);

      if (!markers || markers.length === 0) {
        mapUtils.initMapLayers(map, project, geoData);
      }
      if (geoData?.parcels) {
        await mapUtils.addLayerParcels(map, geoData);
      }

      L.control
        .zoom({
          position: 'topright',
          color: '#335B7E',
        })
        .addTo(map);

      const [latitude, longitude] = mapUtils.getDefaultLatLngForMap(
        project,
        geoData
      );
      map.panTo(new L.LatLng(latitude, longitude));
      this.$store.geolocation.initMapModal(map);

      return map;
    },
  };
}

Alpine.data('MapViewerInteractive', MapViewerInteractive);
