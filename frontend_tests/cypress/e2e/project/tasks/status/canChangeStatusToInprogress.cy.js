import projects from '../../../../fixtures/projects/projects.json'
import tasks from '../../../../fixtures/projects/tasks.json'

const currentProject = projects[6];
const currentTask = tasks[4]


describe('I can go tasks tab', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('changes the status to in progress', () => {
        cy.visit(`/project/${currentProject.pk}`)
        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.contains("Liste").should('have.class', 'active')
        cy.contains(currentTask.fields.intent)

        cy.get(`#${currentTask.pk}`).contains('en cours').click({ force: true });
        cy.get(`#${currentTask.pk}`).contains('en cours').should('have.class', 'bg-blue')

        cy.contains(currentTask.fields.intent).click({ force: true })
        cy.contains(currentTask.fields.intent)

        const now = new Date();
        cy.contains(`a changé le statut de la recommandation en en cours le ${now.toLocaleDateString()}`)

    })
})
