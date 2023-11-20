/**
 * Common actions in the projects page
 */

const domElements = {
	// Project dashboard tabs
	ADMIN_PATH:'/administration',
	ADMIN_TAB:'[data-test-id="navigation-administration-tab"]',

	// Pause / Reactivate project
	ADMIN_BANNER_DEACTIVATE_PROJECT:'[data-test-id="admin-banner-deactivate-project"]',
	ADMIN_BANNER_ACTIVATE_PROJECT:'[data-test-id="admin-banner-activate-project"]',
	HEADER_BANNER_PROJECT_INACTIVE:'[data-test-id="header-banner-project-inactive"]',
	BUTTON_MODAL_DEACTIVATE_PROJECT:'[data-test-id="button-open-modal-deactivate-project"]',
	FORM_PAUSE_PROJECT: '[data-test-id="form-pause-project"]',
	BUTTON_DEACTIVATE_PROJECT:'[data-test-id="button-deactivate-project"]',
	BUTTON_ACTIVATE_PROJECT:'[data-test-id="button-activate-project"]',

	// Email Reminder Settings
	BUTTON_OPEN_REMINDER_SETTINGS:'data-test-id="button-open-reminder-settings"',
	TOOLTIP_REMINDER_SETTINGS:'[ data-test-id="tooltip-reminder-settings"]',
	BUTTON_CLOSE_REMINDER_SETTINGS:'[data-test-id="button-close-reminder-settings"]',
	MESSAGE_REMINDER_SETTINGS:'[data-test-id="message-reminder-settings"]',
	REMINDER_EMAIL_RECIPIENT:'[data-test-id="email-recipient"]',
	REMINDER_EMAIL_DATE:'[data-test-id="email-date"]',
	MESSAGE_NO_REMINDER:'[data-test-id="no-reminders"]',
	REMINDER_ACCESS: '[data-test-id="reminder-settings-access"]'
}

class Project {
	dom

	constructor(dom) {
		this.dom = dom
	}

	// Navigation
	navigateToTab(tabName, path) {
		cy.get(tabName).click({force:true})
		cy.url().should('include', path)
	}

	navigateToPreferencesTab() {
		this.navigateToTab(this.dom.ADMIN_TAB, this.dom.ADMIN_PATH)
	}

	// Actions
	deactivateProject() {
		cy.get(this.dom.ADMIN_BANNER_DEACTIVATE_PROJECT).get(this.dom.BUTTON_MODAL_DEACTIVATE_PROJECT).click({force:true})
		cy.get(this.dom.FORM_PAUSE_PROJECT).get(this.dom.BUTTON_DEACTIVATE_PROJECT).click({force:true})
		cy.get(this.dom.ADMIN_BANNER_DEACTIVATE_PROJECT).should('not.exist')
	}

	activateProjectFromPreferences() {
		cy.get(this.dom.ADMIN_BANNER_ACTIVATE_PROJECT).find(this.dom.BUTTON_ACTIVATE_PROJECT).click({force:true}).then(() => {
			cy.get(this.dom.ADMIN_BANNER_ACTIVATE_PROJECT).should('not.exist')
		})
	}

	activateProjectFromHeaderBanner() {
		cy.get(this.dom.HEADER_BANNER_PROJECT_INACTIVE).find(this.dom.BUTTON_ACTIVATE_PROJECT).click({force:true}).then(() => {
			cy.get(this.dom.HEADER_BANNER_PROJECT_INACTIVE).should('not.exist')
		})
	}

	openEmailReminderTooltip () {
		cy.get(this.dom.BUTTON_OPEN_REMINDER_SETTINGS).click({force:true}).then(() => {
			cy.find(this.dom.TOOLTIP_REMINDER_SETTINGS).should('exist')
		})
	}

	closeEmailReminderTooltip () {
		cy.get(this.dom.BUTTON_CLOSE_REMINDER_SETTINGS).click({force:true}).then(() => {
			cy.find(this.dom.TOOLTIP_REMINDER_SETTINGS).should('not.exist')
		})
	}

	// Verifications
	/**
	 * @param {*} condition 'exist' if user has rights to pause a Project, 'not.exists' if not
	 */
	checkProjectStatusBanner(condition='not.exist') {
		cy.get(this.dom.HEADER_BANNER_PROJECT_INACTIVE).then(() => {
			cy.get(this.dom.BUTTON_ACTIVATE_PROJECT).should(condition)
		})
	}

	/**
	 * @param {*} condition 'exist' if user has rights to pause a Project, 'not.exists' if not
	 */
	checkDeactivateAction(condition='not.exist') {
		cy.get(this.dom.ADMIN_BANNER_DEACTIVATE_PROJECT).should(condition)
	}

	/**
	 * @param {*} email recipient email if a reminder is expected, null otherwise
	 */
	checkNextEmailReminder(email=null) {
		if(email) {
			cy.get(this.dom.REMINDER_EMAIL_RECIPIENT).should('contain', email)
			cy.get(this.dom.REMINDER_EMAIL_DATE).should('not.contain', 'Aucun')
		} else {
			cy.get(this.dom.MESSAGE_NO_REMINDER).should('exist')
		}
	}

	/**
	 * @param {*} role of user that determines display
	 * @param {*} email if not null: user email should appear in settings
	 */
	checkEmailReminderSettings(role, email=null) {
		switch(role) {
			case 'owner' :
				cy.get(this.dom.MESSAGE_REMINDER_SETTINGS).should('contain', email)
				break
			case 'member' :
				cy.get(this.dom.MESSAGE_REMINDER_SETTINGS).should('not.exist')
				break
			case 'advisor' :
				cy.get(this.dom.MESSAGE_REMINDER_SETTINGS).should('not.exist')
				break
		}
		cy.get(this.dom.REMINDER_ACCESS).get('a').click({force:true})
    cy.url().should('include', this.dom.ADMIN_PATH)
	}
}

const projectPreferences = new Project(domElements)

export default projectPreferences
