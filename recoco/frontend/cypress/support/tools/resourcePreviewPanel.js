/**
 * Page object for the "resource preview" panel of the conversation page.
 *
 * This overlay shows the detail of a single recommendation (its resource,
 * advisor comment and status buttons). It is opened by consulting a
 * recommendation card and is managed by the Alpine store
 * `$store.resourcePreviewPanel`.
 */

const domElements = {
  PANEL: '[data-test-id="resource-preview-panel"]',
  BACK: '[data-test-id="resource-preview-back"]',
  CLOSE: '[data-test-id="resource-preview-close"]',
  TITLE: '[data-test-id="resource-preview-title"]',

  // Status buttons (shared with the recommendation status switcher)
  STATUS_IN_PROGRESS: '[data-test-id="in-progress-status-task-button"]',
  STATUS_DONE: '[data-test-id="done-status-task-button"]',
  STATUS_NOT_INTERESTED: '[data-test-id="not-interested-status-task-button"]',
};

class ResourcePreviewPanel {
  dom;

  constructor(dom) {
    this.dom = dom;
  }

  // Verifications -----------------------------------------------------------

  expectOpen() {
    return cy.get(this.dom.PANEL).should('be.visible');
  }

  expectClosed() {
    cy.get(this.dom.PANEL).should('not.exist');
  }

  expectTitle(text) {
    cy.get(this.dom.TITLE).should('contain.text', text);
  }

  // Navigation --------------------------------------------------------------

  /**
   * Go back to the shared contents panel (recommendations list).
   */
  back() {
    cy.get(this.dom.BACK).click({ force: true });
    this.expectClosed();
  }

  close() {
    cy.get(this.dom.CLOSE).click({ force: true });
    this.expectClosed();
  }

  // Status actions ----------------------------------------------------------

  setStatusInProgress() {
    cy.get(this.dom.STATUS_IN_PROGRESS).click({ force: true });
  }

  setStatusDone() {
    cy.get(this.dom.STATUS_DONE).click({ force: true });
  }

  setStatusNotInterested() {
    cy.get(this.dom.STATUS_NOT_INTERESTED).click({ force: true });
  }
}

const resourcePreviewPanel = new ResourcePreviewPanel(domElements);

export default resourcePreviewPanel;
