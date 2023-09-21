import projects from '../../../../fixtures/projects/projects.json'
import tasks from '../../../../fixtures/projects/tasks.json'

const currentProject = projects[7];
const currentTask = tasks[5]


describe('I can go tasks tab', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('changes the status to done', () => {
        cy.visit(`/project/${currentProject.pk}`)
        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.contains("Liste").should('have.class', 'active')
        cy.contains(currentTask.fields.intent)

        cy.get(`#${currentTask.pk}`).contains('faite').click({force:true});

        cy.document().then((doc) => {
            doc.getElementById(`${currentTask.pk}-3-button`).click();
          })

        
        cy.get(`#${currentTask.pk}`).contains('faite').should('have.class', 'bg-green-dark')

        cy.contains(currentTask.fields.intent).click({ force: true })
        cy.contains(currentTask.fields.intent)

        const now = new Date();
        cy.contains(`a changé le statut de la recommandation en faite le ${now.toLocaleDateString()}`)
    })
})
