import projects from '../../../../fixtures/projects/projects.json'
import tasks from '../../../../fixtures/projects/tasks.json'

const currentProject = projects[8];
const currentTask = tasks[6]


describe('I can go tasks tab', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('changes the status to non applicable', () => {
        cy.visit(`/project/${currentProject.pk}`)
        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.contains("Liste").should('have.class', 'active')
        cy.contains(currentTask.fields.intent)

        cy.get(`#${currentTask.pk}`).contains('non applicable').click({ force: true });
        cy.contains("Ça n'était pas applicable")

        cy.document().then((doc) => {
            doc.getElementById(`${currentTask.pk}-4-button`).click();
        })

        cy.get(`#${currentTask.pk}`).contains('non applicable').should('have.class', 'bg-grey-dark')

        cy.contains(currentTask.fields.intent).click({ force: true })
        cy.contains(currentTask.fields.intent)

        const now = new Date();
        cy.contains(`a changé le statut de la recommandation en non applicable le ${now.toLocaleDateString()}`)
    })
})
