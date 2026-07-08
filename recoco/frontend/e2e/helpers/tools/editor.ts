/**
 * Port Playwright de cypress/support/tools/editor.js — actions communes sur
 * l'éditeur TipTap.
 */

import { Page, expect } from '@playwright/test';

import { typeInTiptapEditor } from '../commands';

const domElements = {
  // TipTap Editor
  EDITOR: '[data-test-id="tiptap-editor"]',
  EDITOR_CONTENT: '[data-test-id="tiptap-editor-content"] .ProseMirror',
  EDITOR_BUTTON_SUBMIT: '[data-test-id="send-message-conversation"]',
  EDITOR_BUTTON_SUBMIT_NEW_COMMENT: '[data-test-id="button-submit-new"]',
};

export class Editor {
  dom = domElements;
  page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async clear() {
    // Focus programmatique : un overlay peut intercepter le clic
    const content = this.page.locator(this.dom.EDITOR_CONTENT).first();
    await content.evaluate((el) => (el as HTMLElement).focus());
    await this.page.keyboard.press('ControlOrMeta+A');
    await this.page.keyboard.press('Delete');
  }

  // Actions

  async writeMessage(message: string) {
    await typeInTiptapEditor(this.page, message);
  }

  async submitMessage() {
    await this.page
      .locator(this.dom.EDITOR_BUTTON_SUBMIT_NEW_COMMENT)
      .click({ force: true });
  }

  // Verifications

  async checkSubmitButton(disabled = false) {
    const button = this.page.locator(this.dom.EDITOR_BUTTON_SUBMIT);
    if (disabled) {
      await expect(button).toBeDisabled();
    } else {
      await expect(button).toBeEnabled();
    }
  }
}
