import projects from '../../../fixtures/projects/projects.json'
import projectPreferences from '../../../support/views/project-preferences'

const currentProject = projects[14];

describe('As project owner, I can pause a project', () => {

		beforeEach(() => {
				cy.login("bob");
				cy.visit(`/project/${currentProject.pk}`)
		})

	it('Pauses a project from the admin area', () => {
		projectPreferences.navigateToPreferencesTab()
		projectPreferences.deactivateProject()
	})

	it('Reactivates a project from the project  preferences', () => {
		projectPreferences.navigateToPreferencesTab()
		projectPreferences.activateProjectFromPreferences()
	})

	it('Reactivates a project from the header banner', () => {
		projectPreferences.navigateToPreferencesTab()
		projectPreferences.deactivateProject()
		projectPreferences.activateProjectFromHeaderBanner()
	})
})
