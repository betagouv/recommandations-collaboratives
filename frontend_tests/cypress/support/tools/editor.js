/**
 * Common actions in the projects page
 */

const domElements = {
  // TipTap Editor
  EDITOR: '[data-test-id="tiptap-editor"]',
  EDITOR_CONTENT: '[data-test-id="tiptap-editor-content"] .ProseMirror',
  EDITOR_BUTTON_SUBMIT_EDIT: '[data-test-id="button-submit-edit"]',
  EDITOR_BUTTON_SUBMIT_NEW_COMMENT: '[data-test-id="button-submit-new"]',
};

class Editor {
  dom;

  constructor(dom) {
    this.dom = dom;
  }

  clear() {
    cy.get(this.dom.EDITOR_CONTENT).clear();
  }

  // Actions

  writeMessage(message) {
    cy.get(this.dom.EDITOR_CONTENT).type(message, { force: true, delay: 0 });
  }

  submitMessage() {
    cy.get(this.dom.EDITOR_BUTTON_SUBMIT_NEW_COMMENT).click({ force: true });
  }

  // Verifications

  /**
   * @param {*} disabled = 'be.disabled' if the submit button should be disabled
   */
  checkSubmitComment(disabled = 'not.be.disabled') {
    cy.get(this.dom.EDITOR_BUTTON_SUBMIT_NEW_COMMENT).should(disabled);
  }

  /**
   * @param {*} disabled = 'be.disabled' if the submit button should be disabled
   */
  checkSubmitComment(disabled = 'not.be.disabled') {
    cy.get(this.dom.EDITOR_BUTTON_SUBMIT_EDIT).click(disabled);
  }
}

const markdownEditor = new Editor(domElements);

export default markdownEditor;
