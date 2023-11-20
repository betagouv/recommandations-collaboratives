import projects from '../../../fixtures/projects/projects.json'
import projectView from '../../../support/views/project'

const currentProject = projects[14];

describe(`As non referent project member, I can a project's active status`, () => {

		before(() => {
			// First: login as owner and deactivate project
			cy.login("bob");
			cy.visit(`/project/${currentProject.pk}`)

			projectView.navigateToPreferencesTab()
			projectView.deactivateProject()
			cy.logout()
		})

    it('Displays a header banner when a project is paused', () => {

			// Then: login as non referent project member and check banner
			cy.login("boba");
			cy.visit(`/project/${currentProject.pk}`)
			projectView.navigateToPreferencesTab()
			projectView.checkProjectStatusBanner()
		})
})
