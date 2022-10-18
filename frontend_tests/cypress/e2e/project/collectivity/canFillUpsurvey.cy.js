describe('I can fill a project survey', () => {

    beforeEach(() => {
        cy.login("bob");
    })

    it('fills up the survey', () => {

        cy.visit('/project/4')

        cy.contains("État des lieux").click({ force: true })
        cy.contains("Démarrer le parcours").click({ force: true })

        cy.url().should('include', '/projects/survey/')

        cy.get('#form_answer-1')
            .check({ force: true })

        cy.get('#input-project-comment')
            .type('Fake comment on first survey question', { force: true })
            .should('have.value', 'Fake comment on first survey question')

        cy.contains('Valider ma réponse').click({ force: true });

        cy.contains("État des lieux").click({ force: true })
        cy.url().should('include', '/connaissance')
        cy.contains('Propriété du site')
        cy.contains('100%')
        cy.contains('Fake comment on first survey question')
    })
})
