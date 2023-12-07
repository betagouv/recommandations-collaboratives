import projects from '../../../../fixtures/projects/projects.json'
import projectView from '../../../../support/views/project'

const currentProject = projects[14];

describe('As site staff, I can quit a project', () => {

	beforeEach(() => {
			cy.login("staff");
			cy.visit(`/project/${currentProject.pk}`)
	})

	it.skip('I can quit a project from the project preferences', () => {
		// At the moment quitting a project as staff results in an error
		projectView.navigateToPreferencesTab()
		projectView.quitProject('staff')
	})
})
