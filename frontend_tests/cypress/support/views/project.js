/**
 * Common actions in the projects page
 */

const domElements = {
	// Project dashboard tabs
	ADMIN_PATH:'/administration',
	ADMIN_TAB:'[data-test-id="navigation-administration-tab"]',
	ACTIONS_PATH:'/actions',
	ACTIONS_TAB:'[data-test-id="navigation-actions-tab"]',

	// Pause / Reactivate project
	ADMIN_BANNER_DEACTIVATE_PROJECT:'[data-test-id="admin-banner-deactivate-project"]',
	ADMIN_BANNER_ACTIVATE_PROJECT:'[data-test-id="admin-banner-activate-project"]',
	HEADER_BANNER_PROJECT_INACTIVE:'[data-test-id="header-banner-project-inactive"]',
	BUTTON_MODAL_DEACTIVATE_PROJECT:'[data-test-id="button-open-modal-deactivate-project"]',
	FORM_PAUSE_PROJECT: '[data-test-id="form-pause-project"]',
	BUTTON_DEACTIVATE_PROJECT:'[data-test-id="button-deactivate-project"]',
	BUTTON_ACTIVATE_PROJECT:'[data-test-id="button-activate-project"]',

	// Quit project
	ADMIN_BANNER_QUIT_PROJECT:'[data-test-id="admin-banner-quit-project"]',
	BUTTON_QUIT_PROJECT:'[data-test-id="button-quit-project"]',

	// Email Reminder Settings
	BUTTON_OPEN_REMINDER_SETTINGS:'[data-test-id="button-open-reminder-settings"]',
	TOOLTIP_REMINDER_SETTINGS:'[data-test-id="tooltip-reminder-settings"]',
	BUTTON_CLOSE_REMINDER_SETTINGS:'[data-test-id="button-close-reminder-settings"]',
	MESSAGE_REMINDER_SETTINGS:'[data-test-id="message-reminder-settings"]',
	REMINDER_EMAIL_RECIPIENT:'[data-test-id="email-recipient"]',
	REMINDER_EMAIL_DATE:'[data-test-id="email-date"]',
	MESSAGE_NO_REMINDER:'[data-test-id="no-reminders"]',
	REMINDER_ACCESS: '[data-test-id="reminder-settings-access"]',
	ACTIONS_PATH:'/actions',
	ACTIONS_TAB:'[data-test-id="project-navigation-actions"]',

	// Project dashboard tabs
	OVERVIEW_PATH:'/presentation',
	OVERVIEW_TAB:'[data-test-id="project-navigation-overview"]',

	// Project dashboard tabs
	KNOWLEDGE_PATH:'/connaissance',
	KNOWLEDGE_TAB:'[data-test-id="project-navigation-knowledge"]',

	// Actions Tab - Tasks List
	TASK_CARD:'[data-test-id="task-kanban-topic"]',

	// Positioning Banner
	HEADER_BANNER_ADVISING_POSITION:'[data-test-id="header-banner-advising-position"]',
	BUTTON_JOIN_AS_ADVISOR:'[data-test-id="button-join-as-advisor"]',
	BUTTON_JOIN_AS_OBSERVER:'[data-test-id="button-join-as-observer"]',
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

	navigateToActionsTab() {
		this.navigateToTab(this.dom.ACTIONS_TAB, this.dom.ACTIONS_PATH)
	}

	navigateToOverviewTab() {
		this.navigateToTab(this.dom.OVERVIEW_TAB, this.dom.OVERVIEW_PATH)
	}

	navigateToKnowledgeTab() {
		this.navigateToTab(this.dom.KNOWLEDGE_TAB, this.dom.KNOWLEDGE_PATH)
	}

	// Actions

	joinAsAdvisor() {
		cy.get(this.dom.BUTTON_JOIN_AS_ADVISOR).click({force:true}).then(() => {
			cy.get(this.dom.HEADER_BANNER_ADVISING_POSITION).should('not.exist')
		})
	}

	joinAsObserver() {
		cy.get(this.dom.BUTTON_JOIN_AS_OBSERVER).click({force:true}).then(() => {
			cy.get(this.dom.HEADER_BANNER_ADVISING_POSITION).should('not.exist')
		})
	}

	deactivateProject() {
		cy.get(this.dom.ADMIN_BANNER_DEACTIVATE_PROJECT).get(this.dom.BUTTON_MODAL_DEACTIVATE_PROJECT).click({force:true})
		cy.get(this.dom.FORM_PAUSE_PROJECT).get(this.dom.BUTTON_DEACTIVATE_PROJECT).click({force:true})
		cy.get(this.dom.ADMIN_BANNER_DEACTIVATE_PROJECT).should('not.exist')
		cy.get(this.dom.BUTTON_OPEN_REMINDER_SETTINGS).should('not.exist')
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

	quitProject(role) {
		switch(role) {
			case 'advisor':
				cy.get(this.dom.ADMIN_BANNER_QUIT_PROJECT).get(this.dom.BUTTON_QUIT_PROJECT).click({force:true})
				cy.get(this.dom.BUTTON_JOIN_AS_OBSERVER).should('exist')
				break;
			case 'staff':
				cy.get(this.dom.ADMIN_BANNER_QUIT_PROJECT).get(this.dom.BUTTON_QUIT_PROJECT).click({force:true})
				break;
			case 'member':
				cy.get(this.dom.ADMIN_BANNER_QUIT_PROJECT).get(this.dom.BUTTON_QUIT_PROJECT).click({force:true})
				cy.url().should('equal', 'http://example.localhost:8000/')
				break;
			default:
				cy.get(this.dom.ADMIN_BANNER_QUIT_PROJECT).should('not.exist')
		}
	}


	/**
	 * @param {*} email recipient email if a reminder is expected, null otherwise
	 */
	openEmailReminderTooltip (condition='exist', email=null) {
		cy.get(this.dom.BUTTON_OPEN_REMINDER_SETTINGS).click({force:true})
		cy.get(this.dom.TOOLTIP_REMINDER_SETTINGS).should(condition)
		if(email) {
			cy.get(this.dom.MESSAGE_REMINDER_SETTINGS).should(condition)
		}
	}

	closeEmailReminderTooltip (condition='not.exist') {
		cy.get(this.dom.BUTTON_CLOSE_REMINDER_SETTINGS).click({force:true}).then(() => {
			cy.find(this.dom.TOOLTIP_REMINDER_SETTINGS).should(condition)
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
	 * @param {*} condition 'exist' if the project is active and the user has access to notifications, 'not.exists' if not
	 */
	checkEmailReminderTooltip (condition='exist') {
		cy.get(this.dom.BUTTON_OPEN_REMINDER_SETTINGS).should(condition)
	}

	/**
	 * @param {*} email recipient email if a reminder is expected, null otherwise
	 * @param {*} role to test what message is accessible to which user role
	 */
	checkNextEmailReminder({email, role}) {
		if(email) {
			cy.get(this.dom.REMINDER_EMAIL_RECIPIENT).should('contain', email)
			cy.get(this.dom.REMINDER_EMAIL_DATE).should('not.contain', 'Aucun')
		} else if (role === 'staff') {
			cy.get(this.dom.MESSAGE_NO_REMINDER).should('exist')
		} else if (role === 'advisor') {
			cy.get(this.dom.MESSAGE_NO_REMINDER).should('not.exist')
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


	openTask() {
		cy.get(this.dom.TASK_CARD).click({force:true})
	}
}

const projectView = new Project(domElements)

export default projectView
