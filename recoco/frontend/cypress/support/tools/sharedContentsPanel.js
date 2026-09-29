/**
 * Page object for the "shared contents" panel of the conversation page.
 *
 * This overlay lists the recommendations, files and draft recommendations
 * shared in a project conversation. It is opened from the topic counters on
 * the left of the conversation and managed by the Alpine store
 * `$store.sharedContentsPanel`.
 */

const domElements = {
  // Buttons (topic counters) that open the panel on a given tab
  OPEN_RECOMMENDATIONS: '[data-test-id="open-shared-recommendations"]',
  OPEN_FILES: '[data-test-id="open-shared-files"]',
  OPEN_DRAFTS: '[data-test-id="open-shared-drafts"]',

  // Panel container / header
  PANEL: '[data-test-id="shared-contents-panel"]',
  CLOSE: '[data-test-id="shared-contents-panel-close"]',

  // Segmented control tabs
  TAB_RECOMMENDATIONS: '[data-test-id="shared-contents-tab-recommendations"]',
  TAB_FILES: '[data-test-id="shared-contents-tab-files"]',
  TAB_DRAFTS: '[data-test-id="shared-contents-tab-draft-recommendations"]',

  // Empty states
  EMPTY_RECOMMENDATIONS:
    '[data-test-id="shared-contents-empty-recommendations"]',
  EMPTY_FILES: '[data-test-id="shared-contents-empty-files"]',
  EMPTY_DRAFTS: '[data-test-id="shared-contents-empty-draft-recommendations"]',

  // Recommendation cards
  RECO_CARD: '[data-test-id="shared-contents-reco-card"]',
  RECO_CARD_TITLE: '[data-test-id="recommendation-card-title"]',
  RECO_CARD_CONSULT: '[data-test-id="recommendation-card-consult"]',

  // Draft recommendation cards
  DRAFT_CARD: '[data-test-id="draft-reco-card"]',
  DRAFT_POSITION: '[data-test-id="draft-reco-position"]',
  DRAFT_MOVE_UP: '[data-test-id="draft-reco-move-up"]',
  DRAFT_MOVE_DOWN: '[data-test-id="draft-reco-move-down"]',
  DRAFT_EDIT: '[data-test-id="draft-reco-edit"]',
  DRAFT_DELETE: '[data-test-id="draft-reco-delete"]',
  DRAFT_PUBLISH: '[data-test-id="draft-reco-publish"]',

  // Delete confirmation modal (shared with the legacy task modal)
  DELETE_MODAL_CONFIRM: '[data-test-id="delete-task-modal-button"]',
};

class SharedContentsPanel {
  dom;

  constructor(dom) {
    this.dom = dom;
  }

  // Navigation --------------------------------------------------------------

  /**
   * Open the panel by clicking the matching topic counter.
   * @param {'recommendations'|'files'|'drafts'} tab
   */
  openFromTopic(tab = 'recommendations') {
    const selectors = {
      recommendations: this.dom.OPEN_RECOMMENDATIONS,
      files: this.dom.OPEN_FILES,
      drafts: this.dom.OPEN_DRAFTS,
    };
    cy.get(selectors[tab]).first().click({ force: true });
    return this.expectOpen();
  }

  /**
   * Switch the active tab from within the open panel.
   * @param {'recommendations'|'files'|'drafts'} tab
   */
  switchTab(tab = 'recommendations') {
    const selectors = {
      recommendations: this.dom.TAB_RECOMMENDATIONS,
      files: this.dom.TAB_FILES,
      drafts: this.dom.TAB_DRAFTS,
    };
    cy.get(selectors[tab]).click({ force: true });
  }

  close() {
    cy.get(this.dom.CLOSE).click({ force: true });
    cy.get(this.dom.PANEL).should('not.exist');
  }

  // Getters -----------------------------------------------------------------

  expectOpen() {
    return cy.get(this.dom.PANEL).should('be.visible');
  }

  getRecommendationCards() {
    return cy.get(this.dom.RECO_CARD);
  }

  getDraftCards() {
    return cy.get(this.dom.DRAFT_CARD);
  }

  // Verifications -----------------------------------------------------------

  expectRecommendationCount(count) {
    if (count === 0) {
      cy.get(this.dom.EMPTY_RECOMMENDATIONS).should('be.visible');
    } else {
      this.getRecommendationCards().should('have.length', count);
    }
  }

  expectDraftCount(count) {
    if (count === 0) {
      cy.get(this.dom.EMPTY_DRAFTS).should('be.visible');
    } else {
      this.getDraftCards().should('have.length', count);
    }
  }

  /**
   * Assert the draft at a given index displays the expected position number.
   */
  expectDraftPosition(index, position) {
    this.getDraftCards()
      .eq(index)
      .find(this.dom.DRAFT_POSITION)
      .should('have.text', `${position}`);
  }

  // Actions -----------------------------------------------------------------

  /**
   * Open the detail (resource preview) panel from a recommendation card.
   */
  consultRecommendation(index = 0) {
    this.getRecommendationCards()
      .eq(index)
      .find(this.dom.RECO_CARD_CONSULT)
      .click({ force: true });
  }

  moveDraftUp(index) {
    this.getDraftCards()
      .eq(index)
      .find(this.dom.DRAFT_MOVE_UP)
      .click({ force: true });
  }

  moveDraftDown(index) {
    this.getDraftCards()
      .eq(index)
      .find(this.dom.DRAFT_MOVE_DOWN)
      .click({ force: true });
  }

  publishDraft(index = 0) {
    this.getDraftCards()
      .eq(index)
      .find(this.dom.DRAFT_PUBLISH)
      .click({ force: true });
  }

  editDraft(index = 0) {
    this.getDraftCards()
      .eq(index)
      .find(this.dom.DRAFT_EDIT)
      .click({ force: true });
  }

  /**
   * Delete the draft at a given index and confirm in the modal.
   */
  deleteDraft(index = 0) {
    this.getDraftCards()
      .eq(index)
      .find(this.dom.DRAFT_DELETE)
      .click({ force: true });
    cy.get(this.dom.DELETE_MODAL_CONFIRM).click({ force: true });
  }
}

const sharedContentsPanel = new SharedContentsPanel(domElements);

export default sharedContentsPanel;
