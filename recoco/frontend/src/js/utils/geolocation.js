import * as L from 'leaflet';

const COMMUNES_LYON = ['69381','69382','69383','69384','69385','69386','69387','69388','69389'];
const COMMUNES_MARSEILLE = ['13201','13202','13203','13204','13205','13206','13207','13208','13209','13210','13211','13212','13213','13214','13215','13216'];
const COMMUNES_PARIS = ['75101','75102','75103','75104','75105','75106','75107','75108','75109','75110','75111','75112','75113','75114','75115','75116','75117','75118','75119','75120'];


// Doc: https://apicarto.ign.fr/api/doc/cadastre#/Commune/get_cadastre_commune
const API_GEO_GOUV = 'https://geo.api.gouv.fr';
const API_CADASTRE = 'https://apicarto.ign.fr/api/cadastre';
const API_ADRESSE = 'https://api-adresse.data.gouv.fr';

const LAT_LNG_FRANCE = [46.5,1.20]; // latitude and longitude of centroid of France
const IGN_BBOX = new L.LatLngBounds(
    new L.LatLng(-63.3725, -21.4756),
    new L.LatLng(51.3121, 55.9259));


function createPolygonFromBounds(map, latLngBounds) {
    var center = latLngBounds.getCenter();
    var latlngs = [];

    latlngs.push(latLngBounds.getSouthWest());//bottom left
    latlngs.push({ lat: latLngBounds.getSouth(), lng: center.lng });//bottom center
    latlngs.push(latLngBounds.getSouthEast());//bottom right
    latlngs.push({ lat: center.lat, lng: latLngBounds.getEast() });// center right
    latlngs.push(latLngBounds.getNorthEast());//top right
    latlngs.push({ lat: latLngBounds.getNorth(), lng: map.getCenter().lng });//top center
    latlngs.push(latLngBounds.getNorthWest());//top left
    latlngs.push({ lat: map.getCenter().lat, lng: latLngBounds.getWest() });//center left

    return new L.polygon(latlngs);
}

function getGlobalCityCodeFromCodeInsee(codeInsee) {
	if (COMMUNES_PARIS.includes(codeInsee)) {
		return '75056';
	}
	if (COMMUNES_LYON.includes(codeInsee)) {
		return '69123';
	}
	if (COMMUNES_MARSEILLE.includes(codeInsee)) {
		return '13055';
	}
}

function getCodeArrFromCodeInsee(codeInsee) {
	return codeInsee.slice(-3);
}

async function fetchCommuneIgn(insee) {
	if (insee.length !== 5) {
		return;
	}

  const apiEndpoint = `${API_GEO_GOUV}/communes/${insee}?format=geojson&geometry=contour`;

	  const response = await fetch(apiEndpoint);

    const geodata = await response.json();

	  return geodata;
}

async function fetchParcelsIgn(insee) {
	if (insee.length !== 5) {
		return;
	}
	  const apiEndpoint = `${API_CADASTRE}/parcelle?_limit=100&`;
	const searchParams = {};

	if (!getGlobalCityCodeFromCodeInsee(codeInsee)) {
		searchParams['code_insee'] = insee;
	} else {
		var codeArr = getCodeArrFromCodeInsee(codeInsee);
		var codeInsee = getGlobalCityCodeFromCodeInsee(codeInsee);
		searchParams['code_arr'] = codeArr;
		searchParams['code_insee'] = codeInsee;
	}

	const parcels = await fetch(apiEndpoint + new URLSearchParams(searchParams)).then(response => response.json());

	return parcels;
}

async function fetchGeolocationByAddress(address, commune) {
	if (address.length < 3) {
		return;
	}
	const apiEndpoint = `${API_ADRESSE}/search?`;
	const searchParams = { q: address, limit: 10 }; // TODO
	if(commune)  {
		const {name, insee, postal} = commune;
		searchParams['city'] = name ?? undefined;
		searchParams['citycode'] = insee ?? undefined;
		searchParams['postcode'] = postal ?? undefined;
	}
	const geoJSON = await fetch(apiEndpoint + new URLSearchParams(searchParams)).then(response => response.json());
	return geoJSON;
}

export default {
	getCodeArrFromCodeInsee,
	getGlobalCityCodeFromCodeInsee,
	fetchCommuneIgn,
	fetchParcelsIgn,
	fetchGeolocationByAddress,
    createPolygonFromBounds,
	LAT_LNG_FRANCE,
  IGN_BBOX
};
