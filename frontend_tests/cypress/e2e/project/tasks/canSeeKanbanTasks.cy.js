import projects from '../../../fixtures/projects/projects.json'
import tasks from '../../../fixtures/projects/tasks.json'

const currentProject = projects[1];
const task1 = tasks[0]
const task2 = tasks[1]
const task3 = tasks[2]
const task4 = tasks[3]


describe('I can go tasks tab', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('list all kanban tasks', () => {
        cy.visit(`/project/${currentProject.pk}`)
        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.contains("Statut d’avancement").click({ force: true })
        cy.contains("Statut d’avancement").should('have.class', 'active')

        cy.contains(task1.fields.intent)
        cy.contains(task2.fields.intent)
        cy.contains(task3.fields.intent)
        cy.contains(task4.fields.intent)
    })
})
