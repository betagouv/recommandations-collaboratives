import * as L from 'leaflet';
/**
 * Source: https://github.com/entrepreneur-interet-general/leaflet-geocoder-ban/blob/master/src/leaflet-geocoder-ban.js
 */

const LExtendedBAN = L
LExtendedBAN.GeocoderBAN = L.Control.extend({
	options: {
		position: 'topleft',
		style: 'control',
		placeholder: 'Rechercher une adresse ou des coordonnées',
		resultsNumber: 10,
		collapsed: true,
		serviceUrl: 'https://api-adresse.data.gouv.fr/search/',
		minIntervalBetweenRequests: 250,
		defaultMarkgeocode: true,
		autofocus: true,
		onUpdate: null,
		markerIcon:null,
		markerPopupTemplate: null,
		commune: null,
		popupOptions: null
	},
	includes: L.Evented.prototype || L.Mixin.Events,
	initialize: function (options) {
		L.Util.setOptions(this, options)
	},
	onRemove: function (map) {
		map.off('click', this.collapseHack, this)
	},
	onAdd: function (map) {
		var className = 'leaflet-control-geocoder-ban'
		var container = this.container = L.DomUtil.create('div', className + ' leaflet-bar')
		var icon = this.icon = L.DomUtil.create('span', className + '-icon', container)
		var form = this.form = L.DomUtil.create('div', className + '-form', container)
		var input
		
		map.on('click', this.collapseHack, this)
		
		icon.innerHTML = `<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
		<path d="M8.76683 8.50069L11.0866 10.8205L10.3206 11.5865L8.00081 9.26671C7.1667 9.93404 6.10887 10.3333 4.95837 10.3333C2.26737 10.3333 0.083374 8.14925 0.083374 5.45825C0.083374 2.76725 2.26737 0.583252 4.95837 0.583252C7.64937 0.583252 9.83337 2.76725 9.83337 5.45825C9.83337 6.60875 9.43417 7.66657 8.76683 8.50069ZM7.68009 8.09877C8.34244 7.41616 8.75004 6.48504 8.75004 5.45825C8.75004 3.36336 7.05327 1.66659 4.95837 1.66659C2.86348 1.66659 1.16671 3.36336 1.16671 5.45825C1.16671 7.55315 2.86348 9.24992 4.95837 9.24992C5.98516 9.24992 6.91628 8.84231 7.59889 8.17997L7.68009 8.09877Z" fill="#666666"/>
		</svg>
		
`
		
		input = this.input = L.DomUtil.create('input', '', form)
		input.type = 'text'
		input.placeholder = this.options.placeholder
		
		this.alts = L.DomUtil.create('ul',
		className + '-alternatives ' + className + '-alternatives-minimized',
		container)
		
		L.DomEvent.addListener(input, 'keyup', this.keyup, this)
		
		L.DomEvent.disableScrollPropagation(container)
		L.DomEvent.disableClickPropagation(container)
		
		if (!this.options.collapsed) {
			this.expand()
			if (this.options.autofocus) {
				setTimeout(function () { input.focus() }, 250)
			}
		}
		L.DomUtil.addClass(container, 'searchBar')
			var rootEl = document.getElementsByClassName('leaflet-control-container')[0]
			rootEl.appendChild(container)
			return L.DomUtil.create('div', 'hidden')
	},
	minimizeControl() {
			// for the searchBar: only hide results, not the bar
			L.DomUtil.addClass(this.alts, 'leaflet-control-geocoder-ban-alternatives-minimized')
	},
	expand: function () {
		L.DomUtil.addClass(this.container, 'leaflet-control-geocoder-ban-expanded')
		if (this.geocodeMarker) {
			this._map.removeLayer(this.geocodeMarker)
		}
		this.input.select()
	},
	collapse: function () {
		L.DomUtil.removeClass(this.container, 'leaflet-control-geocoder-ban-expanded')
		L.DomUtil.addClass(this.alts, 'leaflet-control-geocoder-ban-alternatives-minimized')
		this.input.blur()
	},
	collapseHack: function (e) {
		// leaflet bug (see #5507) before v1.1.0 that converted enter keypress to click.
		if (e.originalEvent instanceof MouseEvent) {
			this.minimizeControl()
		}
	},
	moveSelection: function (direction) {
		var s = document.getElementsByClassName('leaflet-control-geocoder-ban-selected')
		var el
		if (!s.length) {
			el = this.alts[direction < 0 ? 'firstChild' : 'lastChild']
			L.DomUtil.addClass(el, 'leaflet-control-geocoder-ban-selected')
		} else {
			var currentSelection = s[0]
			L.DomUtil.removeClass(currentSelection, 'leaflet-control-geocoder-ban-selected')
			if (direction > 0) {
				el = currentSelection.previousElementSibling ? currentSelection.previousElementSibling : this.alts['lastChild']
			} else {
				el = currentSelection.nextElementSibling ? currentSelection.nextElementSibling : this.alts['firstChild']
			}
		}
		if (el) {
			L.DomUtil.addClass(el, 'leaflet-control-geocoder-ban-selected')
		}
	},
	keyup: function (e) {
		switch (e.keyCode) {
			case 27:
				// escape
				this.minimizeControl()
				L.DomEvent.preventDefault(e)
				break
			case 38:
				// down
				this.moveSelection(1)
				L.DomEvent.preventDefault(e)
				break
			case 40:
				// up
				this.moveSelection(-1)
				L.DomEvent.preventDefault(e)
				break
			case 13:
				// enter
				var s = document.getElementsByClassName('leaflet-control-geocoder-ban-selected')
				if (s.length) {
					this.geocodeResult(s[0].geocodedFeatures)
				}
				L.DomEvent.preventDefault(e)
				break
			default:
				if (this.input.value && this.input.value.length > 3) {
					var params = {q: this.input.value, limit: this.options.resultsNumber}
					if(this.options.commune?.filters)  {
						const {citycode, postcode} = this.options.commune.filters
						params['citycode'] = citycode ?? undefined
						params['postcode'] = postcode ?? undefined
					}
					var t = this
					if (this.setTimeout) {
						clearTimeout(this.setTimeout)
					}
					// avoid responses collision if typing quickly
					this.setTimeout = setTimeout(function () {
						getJSON(t.options.serviceUrl, params, t.displayResults(t))
					}, this.options.minIntervalBetweenRequests)
				} else {
					this.clearResults()
				}
				L.DomEvent.preventDefault(e)
		}
	},
	clearResults: function () {
		while (this.alts.firstChild) {
			this.alts.removeChild(this.alts.firstChild)
		}
	},
	displayResults: function (t) {
		t.clearResults()
		return function (res) {
			if (res && res.features) {
				var features = res.features
				L.DomUtil.removeClass(t.alts, 'leaflet-control-geocoder-ban-alternatives-minimized')
				for (var i = 0; i < Math.min(features.length, t.options.resultsNumber); i++) {
					t.alts.appendChild(t.createAlt(features[i], i))
				}
			}
		}
	},
	createAlt: function (feature, index) {
		var li = L.DomUtil.create('li', '')
		var a = L.DomUtil.create('a', '', li)
		li.setAttribute('data-result-index', index)
		a.innerHTML = '<strong>' + feature.properties.label + '</strong>, ' + feature.properties.context
		li.geocodedFeatures = feature
		var clickHandler = function (e) {
			this.minimizeControl()
			this.geocodeResult(feature)
			this.options.onUpdate({
				lng: feature.geometry.coordinates[0],
				lat: feature.geometry.coordinates[1]
			})
		}
		var mouseOverHandler = function (e) {
			var s = document.getElementsByClassName('leaflet-control-geocoder-ban-selected')
			if (s.length) {
				L.DomUtil.removeClass(s[0], 'leaflet-control-geocoder-ban-selected')
			}
			L.DomUtil.addClass(li, 'leaflet-control-geocoder-ban-selected')
		}
		var mouseOutHandler = function (e) {
			L.DomUtil.removeClass(li, 'leaflet-control-geocoder-ban-selected')
		}
		L.DomEvent.on(li, 'click', clickHandler, this)
		L.DomEvent.on(li, 'mouseover', mouseOverHandler, this)
		L.DomEvent.on(li, 'mouseout', mouseOutHandler, this)
		return li
	},
	geocodeResult: function (feature) {
		this.minimizeControl()
		this.markGeocode(feature)
	},
	markGeocode: function (feature) {
		var latlng = [feature.geometry.coordinates[1], feature.geometry.coordinates[0]]
		this._map.setView(latlng, 14)
		this.geocodeMarker = new L.Marker(latlng, {icon: this.options.markerIcon})
			.bindPopup(this.options.markerPopupTemplate({...this.options.popupOptions, address: this.input.value }))
			.addTo(this._map)
			.openPopup()
	}
})

const getJSON = function (url, params, callback) {

	var xmlHttp = new XMLHttpRequest()
	xmlHttp.onreadystatechange = function () {
		if (xmlHttp.readyState !== 4) {
			return
		}
		if (xmlHttp.status !== 200 && xmlHttp.status !== 304) {
			return
		}
		callback(JSON.parse(xmlHttp.response))
	}
	xmlHttp.open('GET', url + L.Util.getParamString(params), true)
	xmlHttp.setRequestHeader('Accept', 'application/json')
	xmlHttp.send(null)
}

LExtendedBAN.geocoderBAN = function (options) {
	return new LExtendedBAN.GeocoderBAN(options)
}
export default LExtendedBAN.geocoderBAN