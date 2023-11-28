import projects from '../../../fixtures/projects/projects.json'
import projectView from '../../../support/views/project'

const ownerEmail = 'bob@test.fr'
describe('As project owner, I can manage project email communication settings', () => {

	it('Displays no reminder message on projects with no scheduled emails', () => {
		const currentProject = projects[16];
		cy.login("bob");
		cy.visit(`/project/${currentProject.pk}`)
		projectView.checkNextEmailReminder()
	})

	it('Displays a reminder message when an email is scheduled to be sent', () => {
		const currentProject = projects[17];
		cy.login("bob");
		cy.visit(`/project/${currentProject.pk}`)
		projectView.checkNextEmailReminder(ownerEmail)
	})

	it('Reminders settings popup is accessible and provides access to preferences panel', () => {
		const currentProject = projects[17];
		cy.login("bob");
		cy.visit(`/project/${currentProject.pk}`)
		projectView.openEmailReminderTooltip('exist', ownerEmail)
	})
})
