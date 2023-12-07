import projects from '../../../../fixtures/projects/projects.json'
import projectView from '../../../../support/views/project'

const currentProject = projects[14];

describe('As site staff, I can quit a project', () => {

	beforeEach(() => {
			cy.login("staff");
			cy.visit(`/project/${currentProject.pk}`)
			projectView.joinAsAdvisor()
	})

	it('I can quit a project from the project preferences', () => {
		projectView.navigateToPreferencesTab()
		projectView.quitProject('staff')
	})
})
