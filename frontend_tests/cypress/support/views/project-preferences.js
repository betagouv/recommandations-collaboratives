/**
 * Common actions in the projects page
 */

const domElements = {
	ADMIN_PATH:'/administration',
	ADMIN_TAB:'[data-test-id="navigation-administration-tab"]',
	ADMIN_BANNER_DEACTIVATE_PROJECT:'[data-test-id="admin-banner-deactivate-project"]',
	ADMIN_BANNER_ACTIVATE_PROJECT:'[data-test-id="admin-banner-activate-project"]',
	HEADER_BANNER_PROJECT_INACTIVE:'[data-test-id="header-banner-project-inactive"]',
	BUTTON_MODAL_DEACTIVATE_PROJECT:'[data-test-id="button-open-modal-deactivate-project"]',
	FORM_PAUSE_PROJECT: '[data-test-id="form-pause-project"]',
	BUTTON_DEACTIVATE_PROJECT:'[data-test-id="button-deactivate-project"]',
	BUTTON_ACTIVATE_PROJECT:'[data-test-id="button-activate-project"]',
	BUTTON_ACTIVATE_PROJECT:'[data-test-id="button-activate-project"]',
}

class ProjectPreferences {
	dom

	constructor(dom) {
		this.dom = dom
	}

	navigateToTab(tabName, path) {
		cy.get(tabName).click({force:true})
		cy.url().should('include', path)
	}

	navigateToPreferencesTab() {
		this.navigateToTab(this.dom.ADMIN_TAB, this.dom.ADMIN_PATH)
	}

	/**
	 * @param {*} callToAction 'exist' if user has rights to pause a Project, 'not.exists' if not
	 */
	checkProjectStatusBanner(callToAction='not.exist') {
		cy.get(this.dom.HEADER_BANNER_PROJECT_INACTIVE).then(() => {
			cy.get(this.dom.BUTTON_ACTIVATE_PROJECT).should(callToAction)
		})
	}

	/**
	 * @param {*} callToAction 'exist' if user has rights to pause a Project, 'not.exists' if not
	 */
	checkDeactivateAction(callToAction='not.exist') {
		cy.get(this.dom.ADMIN_BANNER_DEACTIVATE_PROJECT).should(callToAction)
	}

	deactivateProject() {
		cy.get(this.dom.ADMIN_BANNER_DEACTIVATE_PROJECT).get(this.dom.BUTTON_MODAL_DEACTIVATE_PROJECT).click({force:true})
		cy.get(this.dom.FORM_PAUSE_PROJECT).get(this.dom.BUTTON_DEACTIVATE_PROJECT).click({force:true})
		cy.get(this.dom.ADMIN_BANNER_DEACTIVATE_PROJECT).should('not.exist')
	}

	activateProjectFromPreferences() {
		cy.get(this.dom.HEADER_BANNER_PROJECT_INACTIVE).find(this.dom.BUTTON_ACTIVATE_PROJECT).click({force:true})
		cy.get(this.dom.HEADER_BANNER_PROJECT_INACTIVE).should('not.exist')
	}

	activateProjectFromHeaderBanner() {
		cy.get(this.dom.ADMIN_BANNER_ACTIVATE_PROJECT).find(this.dom.BUTTON_ACTIVATE_PROJECT).click({force:true})
		cy.get(this.dom.ADMIN_BANNER_ACTIVATE_PROJECT).should('not.exist')
	}
}

const projectPreferences = new ProjectPreferences(domElements)

export default projectPreferences
