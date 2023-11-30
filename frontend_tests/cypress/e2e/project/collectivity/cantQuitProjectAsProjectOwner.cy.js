import projects from '../../../fixtures/projects/projects.json'
import projectView from '../../../support/views/project'

const currentProject = projects[14];

describe('As project owner, I cannot quit a project', () => {

	beforeEach(() => {
			cy.login("bob");
			cy.visit(`/project/${currentProject.pk}`)
	})

	it(`I can't quit a project that I own`, () => {
		projectView.navigateToPreferencesTab()
		projectView.quitProject('owner')
	})
})
