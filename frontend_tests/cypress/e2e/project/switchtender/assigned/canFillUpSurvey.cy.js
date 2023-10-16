import projects from '../../../../fixtures/projects/projects.json'

const currentProject = projects[1];

describe('I can fill a project survey', () => {

    beforeEach(() => {
        cy.login("jean");
    })

    it('fills up the survey', () => {

        cy.visit(`/project/${currentProject.pk}`)

        cy.get('[data-test-id="project-navigation-knowledge"]').click({ force: true })
        cy.get('[data-test-id="link-fill-survey"]').click({ force: true })

        // cy.url().should('include', '/projects/survey/')

        cy.get('#form_answer-1')
            .check({ force: true })

        cy.get('#input-project-comment')
            .type('Fake comment on first survey question', { force: true })
            .should('have.value', 'Fake comment on first survey question')

        cy.get('[data-test-id="button-submit-survey-questionset"]').click({ force: true });

        cy.get('[data-test-id="project-navigation-knowledge"]').click({ force: true })
        cy.url().should('include', '/connaissance')
        cy.contains('Propriété du site')
        cy.contains('100%')
        cy.contains('Fake comment on first survey question')
    })
})
