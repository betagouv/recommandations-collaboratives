/**
 * Page object for the recommendation creation / edition page (ActionPusher).
 *
 * Since the migration to the conversation interface, recommendations are no
 * longer created from an `/actions` modal. The "Créer une recommandation" >
 * "Recommandation vierge" button of the conversation editor navigates to the
 * standalone page `/projects/action/?project_id=<id>`, which can also be
 * visited directly.
 *
 * Publishing redirects to `/project/<id>/conversations`; saving a draft
 * redirects to `/project/<id>/conversations#drafts`. Publishing fires the
 * `action_created` signal server-side, which creates the conversation message
 * + RecommendationNode that makes the recommendation appear in the feed and in
 * the shared contents panel.
 *
 * Only use this page object in tests whose subject is the creation form
 * itself. For everything else, prepare the recommendation upfront: published
 * fixture recos live in `fixtures/projects/tasks.json` +
 * `fixtures/conversations/conversations.json` (the Message/RecommendationNode
 * pair the signal would have created), and data a test mutates is seeded per
 * attempt with `cy.createTaskViaApi` (see support/commands.js).
 */

const domElements = {
  RADIO_NO_RESOURCE: '[data-cy="radio-push-reco-no-resource"]',
  RADIO_SINGLE_RESOURCE: '[data-cy="radio-push-reco-single-resource"]',
  INTENT: '[data-cy="input-title-task"]',
  TOPIC: '#topic_name',
  SEARCH_RESOURCE: '[data-test-id="search-resource-input"]',
  RESOURCE_RADIO: '[data-cy="radio-resource-list-task"]',
  RESOURCE_WARNING_DRAFT: '[data-cy="resource-warning-status-draft"]',
  EDITOR_CONTENT: '[data-test-id="tiptap-editor-content"] .ProseMirror',
  SUBMIT: '[data-cy="button-submit-task"]',
  SAVE_DRAFT: '[data-test-id="publish-draft-task-button"]',
};

class ActionPusher {
  dom;

  constructor(dom) {
    this.dom = dom;
  }

  // Navigation --------------------------------------------------------------

  /**
   * Visit the creation page for a project (optionally pre-selecting a resource).
   * @param {number|string} projectId
   * @param {{resourceId?: number|string}} [options]
   */
  visit(projectId, { resourceId } = {}) {
    const query = resourceId
      ? `?project_id=${projectId}&resource_id=${resourceId}`
      : `?project_id=${projectId}`;
    cy.visit(`/projects/action/${query}`);
    return this;
  }

  // Form filling ------------------------------------------------------------

  /**
   * Fill a recommendation without an associated resource.
   * @param {string} intent - Recommendation title.
   * @param {{content?: string, topic?: string}} [options]
   */
  fillWithoutResource(intent, { content, topic } = {}) {
    cy.get(this.dom.RADIO_NO_RESOURCE).check({ force: true });
    cy.get(this.dom.INTENT)
      .type(intent, { force: true, delay: 0 })
      .should('have.value', intent);
    if (topic) {
      cy.get(this.dom.TOPIC).type(topic, { force: true, delay: 0 });
    }
    if (content) {
      cy.get(this.dom.EDITOR_CONTENT).type(content, { force: true, delay: 0 });
    }
    return this;
  }

  /**
   * Fill a recommendation with an existing resource (first search result).
   * @param {string} search - Text to search resources with.
   * @param {{content?: string}} [options]
   */
  fillWithResource(search, { content } = {}) {
    cy.get(this.dom.RADIO_SINGLE_RESOURCE).check({ force: true });
    cy.get(this.dom.SEARCH_RESOURCE).type(search, { force: true, delay: 0 });
    cy.get(this.dom.RESOURCE_RADIO).first().check({ force: true });
    if (content) {
      cy.get(this.dom.EDITOR_CONTENT).type(content, { force: true, delay: 0 });
    }
    return this;
  }

  // Submission --------------------------------------------------------------

  /**
   * Publish the recommendation and wait for the redirect to the conversation.
   */
  publish() {
    cy.get(this.dom.SUBMIT).should('be.enabled').click({ force: true });
    cy.url().should('include', '/conversations');
    return this;
  }

  /**
   * Save the recommendation as a draft and wait for the redirect to the
   * conversation drafts tab.
   */
  saveDraft() {
    cy.get(this.dom.SAVE_DRAFT).should('be.enabled').click({ force: true });
    cy.url().should('include', '/conversations');
    return this;
  }

  // Convenience shortcuts ---------------------------------------------------

  /**
   * Create and publish a resource-less recommendation for a project.
   */
  createPublished(projectId, intent, options = {}) {
    this.visit(projectId).fillWithoutResource(intent, options).publish();
    return this;
  }

  /**
   * Create and save a resource-less draft recommendation for a project.
   */
  createDraft(projectId, intent, options = {}) {
    this.visit(projectId).fillWithoutResource(intent, options).saveDraft();
    return this;
  }
}

const actionPusher = new ActionPusher(domElements);

export default actionPusher;
