/**
 * Port Playwright de cypress/support/tools/geolocation.js — actions communes
 * sur la localisation projet (cartes Leaflet).
 */

import { Page, expect } from '@playwright/test';

const domElements = {
  // Project Location
  PROJECT_LOCATION: '[data-test-id="project-location"]',
  LINK_PROJECT_LOCATION_EDIT: '[data-test-id="link-project-location-edit"]',
  LINK_PROJECT_LOCATION_EDIT_KNOWLEDGE:
    '[data-test-id="link-project-location-edit-knowledge"]',
  MESSAGE_LOCATION_UNKNOWN: '[data-test-id="message-project-location-unknown"]',

  // Map Selectors
  LEAFLET_LOCATION_OVERLAY_PANE: '.leaflet-overlay-pane',
  LEAFLET_LOCATION_CONTROL_PANE: '.leaflet-control-pane',
  LEAFLET_LOCATION_MARKER_PANE: '.leaflet-marker-pane',
  LEAFLET_AREA_CIRCLE: '.area-circle',
  LEAFLET_AREA_COMMUNE: '.area-commune',
  LEAFLET_MARKER_PROJECT_LOCATION: '.project-coordinates-marker',
  LEAFLET_MARKER_PROJECT_COORDINATES: '.project-coordinates-marker',
  LEAFLET_POPUP_LATITUDE: '[data-test-id="project-coord-x-latitude"]',
  LEAFLET_POPUP_LONGITUDE: '[data-test-id="project-coord-y-longitude"]',
  LEAFLET_CONTROL_ZOOM: '.leaflet-control-zoom',

  // Map - Project Overview
  BUTTON_OPEN_MAP_MODAL: '[data-test-id="toggle-open-map-modal"]',
  PROJECT_LOCATION_OVERVIEW: '[data-test-id="project-overview-map"]',
  PROJECT_LOCATION_MODAL: '[data-test-id="project-location-modal"]',
  PROJECT_MAP_STATIC: '[data-test-id="map-static"]',
  PROJECT_MAP_INTERACTIVE: '[data-test-id="map-interactive"]',
  PROJECT_MAP_EDIT: '[data-test-id="map-edit"]',
  INPUT_ADDRESS_LOCATION_EDIT: '.leaflet-control-geocoder-ban-form input',
  SELECT_ADDRESS_LOCATION_EDIT:
    '.leaflet-control-geocoder-ban-alternatives li:first-child',
  BUTTON_SAVE_PROJECT_LOCATION: '[data-test-id="button-save-project-location"]',
};

type MapKind = 'map-static' | 'map-interactive' | 'map-edit';

export class ProjectLocation {
  dom = domElements;
  page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  getSelector(map: MapKind): string {
    switch (map) {
      case 'map-static':
        return this.dom.PROJECT_MAP_STATIC;
      case 'map-interactive':
        return this.dom.PROJECT_MAP_INTERACTIVE;
      case 'map-edit':
        return this.dom.PROJECT_MAP_EDIT;
    }
  }

  // Navigation

  async navigateToLocationEditPage() {
    await this.page
      .locator(this.dom.LINK_PROJECT_LOCATION_EDIT_KNOWLEDGE)
      .click({ force: true });
    await this.page.waitForTimeout(600);
    await expect(this.page.locator(this.dom.PROJECT_MAP_EDIT)).toBeVisible();
  }

  async navigateToLocationEditPageFromOverview() {
    await this.page
      .locator(this.dom.LINK_PROJECT_LOCATION_EDIT)
      .first()
      .click({ force: true });
    await expect(this.page.locator(this.dom.PROJECT_MAP_EDIT)).toBeVisible();
  }

  // Actions

  async openMapModal() {
    await this.page
      .locator(this.dom.BUTTON_OPEN_MAP_MODAL)
      .click({ force: true });
    await expect(
      this.page.locator(this.dom.PROJECT_LOCATION_MODAL)
    ).toBeVisible();
    await expect(
      this.page
        .locator(this.dom.PROJECT_MAP_INTERACTIVE)
        .locator(this.dom.LEAFLET_CONTROL_ZOOM)
    ).toBeAttached();
  }

  async editProjectLocationUsingAddressField(address: string) {
    const input = this.page.locator(this.dom.INPUT_ADDRESS_LOCATION_EDIT);
    await input.focus();
    await input.pressSequentially(address);
    await this.page
      .locator(this.dom.SELECT_ADDRESS_LOCATION_EDIT)
      .click({ force: true });
  }

  async editProjectLocationUsingInteractiveMap() {
    // Le clic peut partir avant l'initialisation de Leaflet : on re-clique
    // jusqu'à ce que le marqueur apparaisse.
    await expect(async () => {
      await this.page.locator(this.dom.PROJECT_MAP_EDIT).click();
      await expect(
        this.page.locator(this.dom.LEAFLET_MARKER_PROJECT_COORDINATES).first()
      ).toBeAttached({ timeout: 1_500 });
    }).toPass({ timeout: 15_000 });
  }

  async saveProjectLocation() {
    await this.page
      .locator(this.dom.BUTTON_SAVE_PROJECT_LOCATION)
      .click({ force: true });
  }

  // Verifications

  async checkMissingCoordinatesMessage(exists = false) {
    const link = this.page.locator(this.dom.LINK_PROJECT_LOCATION_EDIT);
    if (exists) {
      await expect(link.first()).toBeAttached();
    } else {
      await expect(link).toHaveCount(0);
    }
  }

  async checkMapLayerProjectCoordinates(map: MapKind = 'map-static') {
    await expect(this.page.locator(this.getSelector(map))).toBeAttached();
    await expect(
      this.page.locator(this.dom.LEAFLET_MARKER_PROJECT_COORDINATES).first()
    ).toBeAttached();
    await expect(
      this.page.locator(this.dom.LEAFLET_POPUP_LATITUDE)
    ).toHaveCount(0);
  }

  async checkMapLayerProjectLocation(map: MapKind = 'map-static') {
    await expect(this.page.locator(this.getSelector(map))).toBeAttached();
    await this.page
      .locator(this.dom.LEAFLET_MARKER_PROJECT_LOCATION)
      .first()
      .click({ force: true });
    await expect(
      this.page.locator(this.dom.LEAFLET_POPUP_LATITUDE).first()
    ).toBeAttached();
    await expect(
      this.page.locator(this.dom.LEAFLET_POPUP_LONGITUDE).first()
    ).toBeAttached();
  }

  async checkMapLayerAreaCommune(map: MapKind = 'map-static') {
    await expect(this.page.locator(this.getSelector(map))).toBeAttached();
    await expect(
      this.page.locator(this.dom.LEAFLET_AREA_COMMUNE).first()
    ).toBeAttached();
  }

  async checkMapLayerCircle(exists = true, map: MapKind = 'map-static') {
    await expect(this.page.locator(this.getSelector(map))).toBeAttached();
    const circle = this.page.locator(this.dom.LEAFLET_AREA_CIRCLE);
    if (exists) {
      await expect(circle.first()).toBeAttached();
    } else {
      await expect(circle).toHaveCount(0);
    }
  }

  async checkProjectAddressInput(address: string) {
    await expect(
      this.page.locator(this.dom.LEAFLET_POPUP_LATITUDE)
    ).toHaveCount(0);
    await expect(
      this.page.locator(this.dom.LEAFLET_POPUP_LONGITUDE)
    ).toHaveCount(0);
    await expect(this.page.getByText(address).first()).toBeAttached();
  }
}
