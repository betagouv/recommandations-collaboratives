import projects from '../../../fixtures/projects/projects.json'
import projectView from '../../../support/views/project'

const currentProject = projects[14];

describe('As collectivity project member, I can quit a project if I am not the owner', () => {

	beforeEach(() => {
			cy.login("boba");
			cy.visit(`/project/${currentProject.pk}`)
	})

	it('I can quit a project from the project preferences', () => {
		projectView.navigateToPreferencesTab()
		projectView.quitProject('member')
	})
})
