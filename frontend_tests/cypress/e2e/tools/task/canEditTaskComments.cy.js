import projects from '../../../fixtures/projects/projects.json'
import projectView from '../../../support/views/project'
import editor from '../../../support/tools/editor'

const currentProject = projects[2];
const message = 'Message - Test comment on task'

describe('As advisor, I can make a comment on a task', () => {
    beforeEach(() => {
        cy.login("jean");
        cy.visit(`/project/${currentProject.pk}`)
        projectView.joinAsAdvisor()
        projectView.navigateToActionsTab()
    })

    it('adds a new comment, and stops from submitting the comment more than once', () => {
			projectView.openTask()
			// 1. Write a message
			editor.writeMessage(message)
			editor.writeMessage(message)
			editor.checkSubmitComment()

			// 2. Check that button becomes disabled after submitting
			editor.checkSubmitComment('be.disabled')

			// 3. Make sure you can submit a new message (button becomes enabled on dirty editor)
			editor.writeMessage(message)
			editor.checkSubmitComment()
    })
})
