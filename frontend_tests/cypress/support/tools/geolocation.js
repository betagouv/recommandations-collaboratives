/**
 * Common actions in the projects page
 */

const domElements = {
	// Project Location
	PROJECT_LOCATION: '[data-test-id="project-location"]',
	LINK_PROJECT_LOCATION_EDIT: '[data-test-id="link-project-location-edit"]',
	MESSAGE_LOCATION_UNKNOWN: '[data-test-id="message-project-location-unknown"]',

	// Map Selectors
	LEAFLET_LOCATION_OVERLAY_PANE: '.leaflet-overlay-pane',
	LEAFLET_LOCATION_CONTROL_PANE: '.leaflet-control-pane',
	LEAFLET_LOCATION_MARKER_PANE: '.leaflet-marker-pane',
	LEAFLET_AREA_CIRCLE: '.area-circle',
	LEAFLET_AREA_COMMUNE: '.area-commune',
	LEAFLET_MARKER_PROJECT_LOCATION: '.project-location-marker',
	LEAFLET_MARKER_PROJECT_COORDINATES: '.project-coordinates-marker',
	LEAFLET_POPUP_LATITUDE: '[data-test-id="project-coord-x-latitude"]',
	LEAFLET_POPUP_LONGITUDE: '[data-test-id="project-coord-y-longitude"]',
	LEAFLET_CONTROL_ZOOM: '.leaflet-control-zoom',

	// Map - Project Overview
	BUTTON_OPEN_MAP_MODAL: '[data-test-id="toggle-open-map-modal"]',
	PROJECT_LOCATION_OVERVIEW:'[data-test-id="project-overview-map"]',
	PROJECT_LOCATION_MODAL:'[data-test-id="project-location-modal"]',
	PROJECT_MAP_STATIC:'[data-test-id="map-static"]',
	PROJECT_MAP_INTERACTIVE:'[data-test-id="map-interactive"]',
	PROJECT_MAP_EDIT: '[data-test-id="map-edit"]',
	INPUT_ADDRESS_LOCATION_EDIT: '.leaflet-control-geocoder-ban-form input',
	SELECT_ADDRESS_LOCATION_EDIT: '.leaflet-control-geocoder-ban-alternatives li:first-child',
	BUTTON_SAVE_PROJECT_LOCATION: '[data-test-id="button-save-project-location"]'
}

class ProjectLocation {
	dom

	constructor(dom) {
		this.dom = dom
	}

	getSelector(map) {
			let selector
			switch(map) {
				case 'map-static':
					selector = this.dom.PROJECT_MAP_STATIC;
					break;
				case 'map-interactive':
					selector = this.dom.PROJECT_MAP_INTERACTIVE
					break;
				case 'map-edit':
					selector = this.dom.PROJECT_MAP_EDIT
					break;
			}
			return selector
	}

	// Navigation

	navigateToLocationEditPage() {
		cy.get(this.dom.LINK_PROJECT_LOCATION_EDIT).click({force:true}).then(() => {
			cy.wait(600); // TODO: fix by testing loading state (+ add loading spinner)
			cy.get(this.dom.PROJECT_MAP_EDIT).should('be.visible')
		});
	}

	navigateToLocationEditPageFromOverview() {
		cy.get(this.dom.PROJECT_LOCATION_OVERVIEW).find(this.dom.LINK_PROJECT_LOCATION_EDIT).click({force:true})
		cy.get(this.dom.PROJECT_MAP_EDIT).should('be.visible')
	}

	// Actions

	openMapModal() {
		cy.get(this.dom.BUTTON_OPEN_MAP_MODAL).click({force:true})
		cy.get(this.dom.PROJECT_LOCATION_MODAL).should('be.visible')
		cy.get(this.dom.PROJECT_MAP_INTERACTIVE).find(this.dom.LEAFLET_CONTROL_ZOOM)
	}

	editProjectLocationUsingAddressField(address) {
		cy.get(this.dom.INPUT_ADDRESS_LOCATION_EDIT).focus().type(address)
		cy.get(this.dom.SELECT_ADDRESS_LOCATION_EDIT).click({force:true}).then(() => {
			cy.get(this.dom.SELECT_ADDRESS_LOCATION_EDIT).click({force:true})
		})
	}

	editProjectLocationUsingInteractiveMap() {
		// TODO: fix this test
		cy.get(this.dom.PROJECT_MAP_EDIT).click({force:true})
	}

	saveProjectLocation() {
		cy.get(this.dom.BUTTON_SAVE_PROJECT_LOCATION).click({force:true})
	}

	// Verifications

	checkMissingCoordinatesMessage(condition='not.exist') {
		cy.get(this.dom.MESSAGE_LOCATION_UNKNOWN).should(condition)
	}

	checkMapLayerProjectCoordinates(map='map-static') {
		cy.get(this.getSelector(map)).get(this.dom.LEAFLET_LOCATION_MARKER_PANE).then(() => {
			cy.get(this.dom.LEAFLET_MARKER_PROJECT_COORDINATES).should('exist');
			cy.get(this.dom.LEAFLET_POPUP_LATITUDE).should('not.exist')
		});
	}

	checkMapLayerProjectLocation(map='map-static') {
		cy.get(this.getSelector(map)).get(this.dom.LEAFLET_LOCATION_MARKER_PANE).then(() => {
			cy.get(this.dom.LEAFLET_MARKER_PROJECT_LOCATION).click({force: true})
			cy.get(this.dom.LEAFLET_POPUP_LATITUDE).should('exist')
			cy.get(this.dom.LEAFLET_POPUP_LONGITUDE).should('exist')
		});
	}

	checkMapLayerAreaCommune(map='map-static') {
		cy.get(this.getSelector(map)).get(this.dom.LEAFLET_LOCATION_OVERLAY_PANE).then(() => {
			cy.get(this.dom.LEAFLET_AREA_COMMUNE).should('exist');
		});
	}

	checkMapLayerCircle(condition='exist', map='map-static') {
		let selector
		switch(map) {
			case 'map-static':
				selector = this.dom.PROJECT_MAP_STATIC
			case 'map-interactive':
				selector = this.dom.PROJECT_MAP_INTERACTIVE
			case 'map-edit':
				selector = this.dom.PROJECT_MAP_EDIT
		}
		cy.get(this.getSelector(map)).find(this.dom.LEAFLET_LOCATION_OVERLAY_PANE).then(() => {
			cy.get(this.dom.LEAFLET_AREA_CIRCLE).should(condition);
		});
	}

	checkProjectAddressInput(address) {
		cy.get(this.dom.LEAFLET_POPUP_LATITUDE).should('not.exist')
		cy.get(this.dom.LEAFLET_POPUP_LONGITUDE).should('not.exist')
		cy.contains(address).should('exist')
	}
}

const projectLocation = new ProjectLocation(domElements)

export default projectLocation
