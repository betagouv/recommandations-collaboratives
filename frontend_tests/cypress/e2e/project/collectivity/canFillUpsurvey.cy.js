import projects from '../../../fixtures/projects/projects.json'

const currentProject = projects[3];

describe('I can fill a project survey', () => {

    beforeEach(() => {
        cy.login("bob");
        cy.visit(`/project/${currentProject.pk}`)
        cy.get('[data-test-id="fr-consent-banner"]').find('[data-test-id="button-consent-decline-all"]').click()

        const challengeCode = 'survey'
        cy.intercept(`/api/challenges/definitions/${challengeCode}`, {fixture: 'settings/challengeDefinition'})
        cy.intercept(`/api/challenges/${challengeCode}`, {fixture: 'settings/challenge'})
    })

    it('displays the tutorial on a pristine survey', () => {
        cy.visit(`/project/${currentProject.pk}`);

        cy.get('[data-test-id="project-navigation-knowledge"]').click({ force: true });
        cy.get('[data-test-id="link-fill-survey"]').first().click({ force: true });
        
        cy.get('[data-test-id="survey-tutorial"]').should.exist;
    })

    it('does not display the tutorial on a survey that already has answers', () => {
        cy.visit(`/project/${currentProject.pk}`)

        // Start the survey and answer 1 question
        cy.get('[data-test-id="project-navigation-knowledge"]').click({ force: true })
        cy.get('[data-test-id="link-fill-survey"]').first().click({ force: true })
        cy.get('.introjs-skipbutton').click()
        cy.get('#form_answer-1')
            .check({ force: true })

        // Reload the survey: it should load 
        cy.get('[data-test-id="button-submit-survey-questionset"]').click({ force: true }).then(() => {
            cy.visit(`/project/${currentProject.pk}`)
            cy.get('[data-test-id="project-navigation-knowledge"]').click({ force: true })
            cy.get('[data-test-id="link-fill-survey"]').first().click({ force: true })
            cy.get('[data-test-id="survey-tutorial"]').should('not.exist')
        });
    })

    it('fills up the survey', () => {

        cy.visit(`/project/${currentProject.pk}`)

        cy.get('[data-test-id="project-navigation-knowledge"]').click({ force: true })
        cy.get('[data-test-id="link-fill-survey"]').first().click({ force: true })

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
