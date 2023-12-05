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
	LEAFLET_LOCATION_MARKER_PANE: '.leaflet-marker-pane',
	LEAFLET_AREA_CIRCLE: '.area-circle',
	LEAFLET_AREA_COMMUNE: '.area-commune',
	LEAFLET_MARKER_PROJECT_LOCATION: '.project-location-marker',
	LEAFLET_POPUP_LATITUDE: '[data-test-id="project-coord-x-latitude"]',
	LEAFLET_POPUP_LONGITUDE: '[data-test-id="project-coord-y-longitude"]',
	LEAFLET_CONTROL_ZOOM: '.leaflet-control-zoom',

	// Map - Project Overview
	BUTTON_OPEN_MAP_MODAL: '[data-test-id="toggle-open-map-modal"]',
	PROJECT_LOCATION_MODAL:'[data-test-id="project-location-modal"]',
	PROJECT_MAP_STATIC:'[data-test-id="map-static"]',
	PROJECT_MAP_INTERACTIVE:'[data-test-id="map-interactive"]',
	PROJECT_MAP_LOCATION_EDIT: '[data-test-id="map-edit"]'
}

class ProjectLocation {
	dom

	constructor(dom) {
		this.dom = dom
	}

	// Actions

	openMapModal() {
		cy.get(this.dom.BUTTON_OPEN_MAP_MODAL).click({force:true})
		cy.get(this.dom.PROJECT_LOCATION_MODAL).should('be.visible')
		cy.get(this.dom.PROJECT_MAP_INTERACTIVE).find(this.dom.LEAFLET_CONTROL_ZOOM)
	}

	// Verifications

	checkMapLayerProjectCoordinates() {
		cy.get(this.dom.PROJECT_MAP_STATIC).find(this.dom.LEAFLET_LOCATION_MARKER_PANE).then(() => {
			cy.get(this.dom.LEAFLET_MARKER_PROJECT_LOCATION).should('exist');
			cy.get(this.dom.LEAFLET_POPUP_LATITUDE).should('not.exist')
		});
	}

	checkMapLayerProjectLocation() {
		cy.get(this.dom.PROJECT_MAP_STATIC).find(this.dom.LEAFLET_LOCATION_MARKER_PANE).then(() => {
			cy.get(this.dom.LEAFLET_MARKER_PROJECT_LOCATION).click({force: true})
			cy.get(this.dom.LEAFLET_POPUP_LATITUDE).should('exist')
			cy.get(this.dom.LEAFLET_POPUP_LONGITUDE).should('exist')
		});
	}

	checkMapLayerAreaCommune() {
		cy.get(this.dom.PROJECT_MAP_STATIC).find(this.dom.LEAFLET_LOCATION_OVERLAY_PANE).then(() => {
			cy.get(this.dom.LEAFLET_AREA_COMMUNE).should('exist');
		});
	}

	checkMapLayerCircle(condition='exist') {
		cy.get(this.dom.PROJECT_MAP_STATIC).find(this.dom.LEAFLET_LOCATION_OVERLAY_PANE).then(() => {
			cy.get(this.dom.LEAFLET_AREA_CIRCLE).should(condition);
		});
	}
}

const projectLocation = new ProjectLocation(domElements)

export default projectLocation
