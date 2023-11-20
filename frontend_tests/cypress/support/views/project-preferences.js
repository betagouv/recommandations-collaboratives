/**
 * Common actions in the projects page
 */

const ADMIN_PATH = '/administration'
const ADMIN_TAB = '[data-test-id="navigation-administration-tab"]'
const ADMIN_BANNER_DEACTIVATE_PROJECT = '[data-test-id="admin-banner-deactivate-project"]'
const ADMIN_BANNER_ACTIVATE_PROJECT ='[data-test-id="admin-banner-activate-project"]'
const HEADER_BANNER_PROJECT_INACTIVE = '[data-test-id="header-banner-project-inactive"]'
const BUTTON_MODAL_DEACTIVATE_PROJECT = '[data-test-id="button-open-modal-deactivate-project"]'
const BUTTON_DEACTIVATE_PROJECT = '[data-test-id="button-deactivate-project"'
const BUTTON_ACTIVATE_PROJECT = '[data-test-id="button-activate-project"]'

function navigateToTab(tabName, path) {
	cy.get(tabName).click({force:true})
	cy.url().should('include', path)
}

function navigateToPreferencesTab() {
	navigateToTab(ADMIN_TAB, ADMIN_PATH)
}

/**
 * @param {*} callToAction 'exist' if user has rights to pause a Project, 'not.exists' if not
 */
function checkProjectStatusBanner(callToAction='not.exist') {
	cy.get(HEADER_BANNER_PROJECT_INACTIVE).then(() => {
		cy.get(BUTTON_ACTIVATE_PROJECT).should(callToAction)
	})
}

/**
 * @param {*} callToAction 'exist' if user has rights to pause a Project, 'not.exists' if not
 */
function checkDeactivateAction(callToAction='not.exist') {
	cy.get(ADMIN_BANNER_DEACTIVATE_PROJECT).should(callToAction)
}

function deactivateProject() {
	cy.find(ADMIN_BANNER_DEACTIVATE_PROJECT).get(BUTTON_MODAL_DEACTIVATE_PROJECT).click({force:true})
	cy.get(BUTTON_DEACTIVATE_PROJECT).click({force:true})
	cy.get(ADMIN_BANNER_DEACTIVATE_PROJECT).should('not.exist')
}

function activateProjectFromHeaderBanner(tabName) {
	cy.get(HEADER_BANNER_PROJECT_INACTIVE).get(BUTTON_ACTIVATE_PROJECT).click({force:true})
	cy.get(HEADER_BANNER_PROJECT_INACTIVE).should('not.exist')
}

function activateProjectFromPreferences(tabName) {
	cy.get(ADMIN_BANNER_ACTIVATE_PROJECT).get(BUTTON_ACTIVATE_PROJECT).click({force:true})
	cy.get(ADMIN_BANNER_ACTIVATE_PROJECT).should('not.exist')
}

export default {
	navigateToPreferencesTab,
	deactivateProject,
	activateProjectFromHeaderBanner,
	activateProjectFromPreferences,
	checkProjectStatusBanner,
	checkDeactivateAction
}