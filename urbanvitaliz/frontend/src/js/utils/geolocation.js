
const COMMUNES_LYON = ['69381','69382','69383','69384','69385','69386','69387','69388','69389']
const COMMUNES_MARSEILLE = ['13201','13202','13203','13204','13205','13206','13207','13208','13209','13210','13211','13212','13213','13214','13215','13216']
const COMMUNES_PARIS = ['75101','75102','75103','75104','75105','75106','75107','75108','75109','75110','75111','75112','75113','75114','75115','75116','75117','75118','75119','75120']


// Doc: https://apicarto.ign.fr/api/doc/cadastre#/Commune/get_cadastre_commune
const API_CADASTRE = 'https://apicarto.ign.fr/api/cadastre'
const API_ADRESSE = 'https://api-adresse.data.gouv.fr'
const LAT_LNG_FRANCE = [46.5,1.20] // latitude and longitude of }centroid of France

function getGlobalCityCodeFromCodeInsee(codeInsee) {
	if (COMMUNES_PARIS.includes(codeInsee)) {
		return '75056'
	}
	if (COMMUNES_LYON.includes(codeInsee)) {
		return '69123'
	}
	if (COMMUNES_MARSEILLE.includes(codeInsee)) {
		return '13055'
	}
}

function getCodeArrFromCodeInsee(codeInsee) {
	return codeInsee.slice(-3)
}

async function fetchCommuneIgn(insee) {
	if (insee.length !== 5) {
		return
	}
	const apiEndpoint = `${API_CADASTRE}/commune?`;
	const searchParams = {}

	if (!getGlobalCityCodeFromCodeInsee(codeInsee)) {
        searchParams['code_insee'] = insee;
    } else {
        var codeArr = getCodeArrFromCodeInsee(codeInsee);
        var codeInsee = getGlobalCityCodeFromCodeInsee(codeInsee);
        searchParams['code_arr'] = codeArr;
        searchParams['code_insee'] = codeInsee;
    }

	const communeGeo = await fetch(apiEndpoint + new URLSearchParams(searchParams)).then(response => response.json());

	return communeGeo;
}

async function fetchGeolocationByAddress(address) {
	if (address.length < 3) {
		return
	}
	const apiEndpoint = `${API_ADRESSE}/search?`;
	const searchParams = { q: address, limit: 10 } // TODO
	const geoJSON = await fetch(apiEndpoint + new URLSearchParams(searchParams)).then(response => response.json());
	return geoJSON;
}

export default {
	getCodeArrFromCodeInsee,
	getGlobalCityCodeFromCodeInsee,
	fetchCommuneIgn,
	fetchGeolocationByAddress,
	LAT_LNG_FRANCE
}