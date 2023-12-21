

function getDefaultLatLngForMap(project) {
	const longitude = project.location_x ? project.location_x
		: project.commune.longitude ? project.commune.longitude
		: geolocUtils.LAT_LNG_FRANCE[0];
	const latitude = project.location_y ? project.location_y
		: project.commune.latitude ? project.commune.latitude
		: geolocUtils.LAT_LNG_FRANCE[0];

	return [latitude, longitude]
}

// Map base layer
function initMapIGN(idMap, project, options, zoom) {
	const [latitude, longitude] = getDefaultLatLngForMap(project)

	// Documentation : https://geoservices.ign.fr/documentation/services/utilisation-web/extension-pour-leaflet
	// Création de la carte
	const map  = L.map(idMap, {
		...options,
		crs : L.geoportalCRS.EPSG2154
	});

	// Création de la couche
	const layerTuiles = L.geoportalLayer.WMTS({
		layer  : `ORTHOIMAGERY.ORTHOPHOTOS`
	}) ;
	// Création de la couche
	const layerParcellaire = L.geoportalLayer.WMTS({
		layer  : "CADASTRALPARCELS.PARCELS"
	}) ;

	layerTuiles.addTo(map); // ou map.addLayer(lyr);
	layerParcellaire.addTo(map)

	return map.setView(new L.LatLng(latitude, longitude), zoom);
}

export default {
	initMapIGN,
}