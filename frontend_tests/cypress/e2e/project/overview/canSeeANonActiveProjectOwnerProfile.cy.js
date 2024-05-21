import projects from '../../../fixtures/projects/projects.json';

let currentProject = projects[9];

describe('I can go to overview tab', () => {
    beforeEach(() => {
        cy.login('staff');
        cy.visit(`/project/${currentProject.pk}`);
    });

    it('show the profile of a non active project owner with the correct class', () => {
        cy.get('[data-test-id="project-owner-name-details"]').should(
            'have.class',
            'inactive-status'
        );
    });

    it('show the tooltip of a non active user with the date of last connection', () => {
        cy.get(
            '[data-test-id="project-information-card-context"] [data-test-id="button-open-tooltip-user-card"]'
        )
            .click({ force: true })
            .then(() => {
                cy.get(
                    '[data-test-id="project-information-card-context"] [data-test-id="user-card-intro"]'
                )
                    .invoke('text')
                    .should((text) => {
                        expect(text.length).to.be.greaterThan(0);
                    });
                cy.get('[data-test-id="deactivated-user-details"]').should(
                    'exist'
                );
            });
    });

    it('show an anonymous user card if the user does not exist', () => {
        currentProject = projects[13]; // submitted_by: deleted.user@test.fr

        // First: delete the user that submitted the project to test
        cy.visit('/nimda/auth/user/');
        cy.contains('deleted.user@test.fr').click({ force: true });
        cy.get('.deletelink').click({ force: true });
        cy.contains('deleted.user@test.fr').should('exist');
        cy.get('input[type=submit]').click({ force: true });

        // Second: Visit the project to test and check the display of the deleted user card
        cy.visit(`/project/${currentProject.pk}/presentation`);
        cy.get(
            '[data-test-id="project-information-card-context"] [data-test-id="button-open-tooltip-user-card"]'
        )
            .click({ force: true })
            .then(() => {
                cy.get(
                    '[data-test-id="project-information-card-context"] [data-test-id="user-card-intro"]'
                ).should('not.exist');
                cy.get('[data-test-id="deleted-user-details"]').should('exist');
            });
    });
});
