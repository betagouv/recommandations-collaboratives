import projects from '../../../../fixtures/projects/projects.json'

const currentProject = projects[1];

describe('I can fill a project survey', () => {

    beforeEach(() => {
        cy.login("jean");
    })

    it('fills up the survey', () => {

        cy.visit(`/project/${currentProject.pk}`)

        cy.get('a').should('have.class', 'text-nowrap').contains('État des lieux').click({ force: true })
        cy.contains("Compléter cette section").click({ force: true })

        // cy.url().should('include', '/projects/survey/')

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
