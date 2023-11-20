import projects from '../../../../fixtures/projects/projects.json'
import projectView from '../../../../support/views/project'

const currentProject = projects[15];

describe('As site staff, I can pause and reactivate a project', () => {
    beforeEach(() => {
        cy.login("staff");
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
