import projects from '../../../fixtures/projects/projects.json'

const currentProject = projects[1];

describe('I can go tasks tab', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('switch between inline & kanban view', () => {
        cy.visit(`/project/${currentProject.pk}`)
        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.contains("Thématique").should('have.class', 'active')
        cy.contains("Statut d’avancement").click({ force: true })
        cy.contains("Statut d’avancement").should('have.class', 'active')

        cy.contains("Thématique").click({ force: true })
        cy.contains("Thématique").should('have.class', 'active')

       
    })
})
