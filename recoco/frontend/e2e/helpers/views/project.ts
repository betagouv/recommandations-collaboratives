/**
 * Port Playwright de cypress/support/views/project.js — actions communes sur
 * la page projet.
 */

import { Page, expect } from '@playwright/test';

const domElements = {
  // Project dashboard tabs
  ADMIN_PATH: '/administration',
  ADMIN_TAB: '[data-test-id="navigation-administration-tab"]',

  // Pause / Reactivate project
  ADMIN_BANNER_DEACTIVATE_PROJECT:
    '[data-test-id="admin-banner-deactivate-project"]',
  ADMIN_BANNER_ACTIVATE_PROJECT:
    '[data-test-id="admin-banner-activate-project"]',
  BANNER_PROJECT_INACTIVE: '[data-test-id="banner-project-inactive"]',
  BUTTON_MODAL_DEACTIVATE_PROJECT:
    '[data-test-id="button-open-modal-deactivate-project"]',
  FORM_PAUSE_PROJECT: '[data-test-id="form-pause-project"]',
  BUTTON_DEACTIVATE_PROJECT: '[data-test-id="button-deactivate-project"]',
  BUTTON_ACTIVATE_PROJECT: '[data-test-id="button-activate-project"]',

  // Quit project
  ADMIN_BANNER_QUIT_PROJECT: '[data-test-id="admin-banner-quit-project"]',
  BUTTON_QUIT_PROJECT: '[data-test-id="button-quit-project"]',

  // Email Reminder Settings
  BUTTON_OPEN_REMINDER_SETTINGS:
    '[data-test-id="button-open-reminder-settings"]',
  TOOLTIP_REMINDER_SETTINGS: '[data-test-id="tooltip-reminder-settings"]',
  BUTTON_CLOSE_REMINDER_SETTINGS:
    '[data-test-id="button-close-reminder-settings"]',
  MESSAGE_REMINDER_SETTINGS: '[data-test-id="message-reminder-settings"]',
  REMINDER_EMAIL_DATE: '[data-test-id="email-date"]',
  MESSAGE_NO_REMINDER: '[data-test-id="no-reminders"]',
  REMINDER_ACCESS: '[data-test-id="reminder-settings-access"]',

  // Project dashboard tabs
  OVERVIEW_PATH: '/presentation',
  OVERVIEW_TAB: '[data-test-id="project-navigation-overview"]',

  // Project dashboard tabs
  KNOWLEDGE_PATH: '/connaissance',
  KNOWLEDGE_TAB: '[data-test-id="project-navigation-knowledge"]',

  // Positioning Banner
  SHOW_BANNER: '[data-test-id="select-observer-or-advisor-button"]',
  HEADER_BANNER_ADVISING_POSITION:
    '[data-test-id="header-banner-advising-position"]',
  SELECTOR_JOIN_AS_ADVISOR: '[data-test-id="button-become-advisor"]',
  BUTTON_VALIDATE_ROLE: '[data-test-id="button-validate-role"]',
  BUTTON_QUIT_ROLE: '[data-test-id="button-quit-role"]',
};

export class ProjectView {
  dom = domElements;
  page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  // Navigation

  async navigateToTab(tabName: string, path: string) {
    await this.page.locator(tabName).click({ force: true });
    await expect(this.page).toHaveURL(new RegExp(path));
  }

  async navigateToPreferencesTab() {
    await this.navigateToTab(this.dom.ADMIN_TAB, this.dom.ADMIN_PATH);
  }

  async navigateToOverviewTab() {
    await this.navigateToTab(this.dom.OVERVIEW_TAB, this.dom.OVERVIEW_PATH);
  }

  async navigateToKnowledgeTab() {
    await this.navigateToTab(this.dom.KNOWLEDGE_TAB, this.dom.KNOWLEDGE_PATH);
  }

  // Actions

  async joinAsAdvisorWithSelector() {
    // Le clic d'ouverture peut partir avant l'hydratation Alpine : on re-clique
    // jusqu'à ce que le sélecteur de rôle apparaisse.
    const joinButton = this.page
      .locator(this.dom.SELECTOR_JOIN_AS_ADVISOR)
      .first();
    await expect(async () => {
      await this.page.locator(this.dom.SHOW_BANNER).click({ force: true });
      await expect(joinButton).toBeAttached({ timeout: 2_000 });
    }).toPass({ timeout: 15_000 });
    await joinButton.dispatchEvent('click');
  }

  async quitProjectRole() {
    // Bouton dans le sélecteur de rôle replié : équivalent du force:true Cypress
    await this.page
      .locator(this.dom.BUTTON_QUIT_ROLE)
      .first()
      .dispatchEvent('click');
  }

  async deactivateProject() {
    // L'ouverture de la modale peut partir avant l'hydratation Alpine : on
    // re-clique jusqu'à ce que le bouton de confirmation soit visible.
    const deactivateButton = this.page.locator(
      this.dom.BUTTON_DEACTIVATE_PROJECT
    );
    await expect(async () => {
      await this.page
        .locator(this.dom.BUTTON_MODAL_DEACTIVATE_PROJECT)
        .click({ force: true });
      await expect(deactivateButton).toBeVisible({ timeout: 2_000 });
    }).toPass({ timeout: 15_000 });
    await deactivateButton.click({ force: true });
    await expect(
      this.page.locator(this.dom.ADMIN_BANNER_DEACTIVATE_PROJECT)
    ).toHaveCount(0);
    await expect(
      this.page.locator(this.dom.BUTTON_OPEN_REMINDER_SETTINGS)
    ).toHaveCount(0);
  }

  async activateProjectFromPreferences() {
    await this.page
      .locator(this.dom.ADMIN_BANNER_ACTIVATE_PROJECT)
      .locator(this.dom.BUTTON_ACTIVATE_PROJECT)
      .click({ force: true });
    await expect(
      this.page.locator(this.dom.ADMIN_BANNER_ACTIVATE_PROJECT)
    ).toHaveCount(0);
  }

  async quitProject(role?: 'advisor' | 'staff' | 'member') {
    switch (role) {
      case 'advisor':
      case 'staff':
        await this.page
          .locator(this.dom.BUTTON_QUIT_PROJECT)
          .click({ force: true });
        break;
      case 'member':
        await this.page
          .locator(this.dom.BUTTON_QUIT_PROJECT)
          .click({ force: true });
        await expect(this.page).toHaveURL(
          /^http:\/\/example\.localhost:\d+\/$/
        );
        break;
      default:
        await expect(
          this.page.locator(this.dom.ADMIN_BANNER_QUIT_PROJECT)
        ).toHaveCount(0);
    }
  }

  /**
   * @param exists true si le tooltip doit apparaître
   * @param email email du destinataire si une relance est attendue, null sinon
   */
  async openEmailReminderTooltip(exists = true, email: string | null = null) {
    await this.page
      .locator(this.dom.BUTTON_OPEN_REMINDER_SETTINGS)
      .click({ force: true });
    const tooltip = this.page.locator(this.dom.TOOLTIP_REMINDER_SETTINGS);
    if (exists) {
      await expect(tooltip).toBeVisible();
    } else {
      await expect(tooltip).toHaveCount(0);
    }
    if (email) {
      const message = this.page.locator(this.dom.MESSAGE_REMINDER_SETTINGS);
      if (exists) {
        await expect(message).toBeVisible();
      } else {
        await expect(message).toHaveCount(0);
      }
    }
  }

  async closeEmailReminderTooltip() {
    await this.page
      .locator(this.dom.BUTTON_CLOSE_REMINDER_SETTINGS)
      .click({ force: true });
    await expect(
      this.page.locator(this.dom.TOOLTIP_REMINDER_SETTINGS)
    ).toHaveCount(0);
  }

  // Verifications

  /** @param exists true si le projet est en pause (bandeau visible) */
  async checkProjectStatusBanner(exists = false) {
    const banner = this.page.locator(this.dom.BANNER_PROJECT_INACTIVE);
    if (exists) {
      await expect(banner).toBeVisible();
    } else {
      await expect(banner).toHaveCount(0);
    }
  }

  /** @param exists true si l'utilisateur a le droit de mettre le projet en pause */
  async checkDeactivateAction(exists = false) {
    const banner = this.page.locator(this.dom.ADMIN_BANNER_DEACTIVATE_PROJECT);
    if (exists) {
      await expect(banner).toBeVisible();
    } else {
      await expect(banner).toHaveCount(0);
    }
  }

  /** @param exists true si le projet est actif et l'utilisateur a accès aux relances */
  async checkEmailReminderTooltip(exists = true) {
    const button = this.page.locator(this.dom.BUTTON_OPEN_REMINDER_SETTINGS);
    if (exists) {
      await expect(button).toBeVisible();
    } else {
      await expect(button).toHaveCount(0);
    }
  }

  /**
   * @param email email du destinataire si une relance est attendue, null sinon
   * @param role rôle pour tester quel message est accessible à qui
   */
  async checkNextEmailReminder({
    email,
    role,
  }: {
    email?: string | null;
    role?: string;
  }) {
    if (email) {
      await expect(
        this.page.locator(this.dom.REMINDER_EMAIL_DATE)
      ).not.toContainText('Aucun');
      await expect(
        this.page.locator(this.dom.MESSAGE_NO_REMINDER)
      ).toHaveCount(0);
    } else if (role === 'staff' || role === 'advisor') {
      await expect(
        this.page.locator(this.dom.MESSAGE_NO_REMINDER)
      ).toBeAttached();
    }
  }

  /**
   * @param role rôle de l'utilisateur qui détermine l'affichage
   * @param email si non null : l'email doit apparaître dans les réglages
   */
  async checkEmailReminderSettings(role: string, email: string | null = null) {
    const message = this.page.locator(this.dom.MESSAGE_REMINDER_SETTINGS);
    switch (role) {
      case 'owner':
        await expect(message).toContainText(email ?? '');
        break;
      case 'member':
      case 'advisor':
        await expect(message).toHaveCount(0);
        break;
    }
    await this.page
      .locator(this.dom.REMINDER_ACCESS)
      .locator('a')
      .click({ force: true });
    await expect(this.page).toHaveURL(new RegExp(this.dom.ADMIN_PATH));
  }
}
