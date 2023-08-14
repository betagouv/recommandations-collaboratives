import projects from '../../../../fixtures/projects/projects.json'
import tasks from '../../../../fixtures/projects/tasks.json'

const currentProject = projects[1];
const task1 = tasks[0]
const task2 = tasks[1]
const task3 = tasks[2]
const task4 = tasks[3]


describe('I can go tasks tab', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('changes the status to done', () => {
        cy.visit(`/project/${currentProject.pk}`)
        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.contains("Thématique").should('have.class', 'active')
        cy.contains(task4.fields.intent)

        cy.get(`#${task4.pk}`).contains('Fait').click({force:true});
        cy.get('.modal-footer').contains('Archiver').click({force:true});
        cy.get(`#${task4.pk}`).contains('Fait').should('have.class', 'bg-green-dark')
    })
})
