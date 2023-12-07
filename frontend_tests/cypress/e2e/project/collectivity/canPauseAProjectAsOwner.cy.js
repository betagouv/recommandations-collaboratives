import projects from '../../../fixtures/projects/projects.json'
import projectView from '../../../support/views/project'

const currentProject = projects[17];

describe('As project owner, I can pause a project', () => {

	beforeEach(() => {
			cy.login("bob");
			cy.visit(`/project/${currentProject.pk}`)
	})

	it('Pauses a project from the project preferences', () => {
		projectView.navigateToPreferencesTab()
		projectView.deactivateProject()
	})

	it('Reactivates a project from the project preferences', () => {
		projectView.navigateToPreferencesTab()
		projectView.activateProjectFromPreferences()
	})

	it('Reactivates a project from the header banner', () => {
		projectView.navigateToPreferencesTab()
		projectView.deactivateProject()
		projectView.activateProjectFromHeaderBanner()
	})
})
