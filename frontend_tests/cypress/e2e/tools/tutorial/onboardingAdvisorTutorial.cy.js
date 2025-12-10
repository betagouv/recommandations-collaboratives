describe('I can follow the onboarding advisor tutorial as an advisor or staff', () => {

    it('should not display the tutorial when a collectivity is on a project presentation page', () => {
        cy.login('collectivité1');
        cy.visit('/project/2');
        cy.get('[data-test-id="opening-onboarding-tutorial"]').should('not.exist');
    });

    it('follows the tutorial steps correctly if not already advising the project', () => {
        cy.login('conseiller2');
        cy.visit('/project/2');

        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-1"]').click({ force: true });
        cy.get('[data-test-id="select-observer-or-advisor-button"]').click({ force: true });
        cy.get('[data-test-id="button-become-advisor"]').click({ force: true });
        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-1"]').should('not.exist');

        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-2"]').click({ force: true });
        cy.get('[data-test-id="project-navigation-knowledge"]').click({ force: true });
        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-2"]').should('not.exist');

        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-3"]').click({ force: true });
        cy.get('[data-test-id="project-navigation-conversations-new"]').click({ force: true });
        cy.get('[data-test-id="tiptap-editor-content"]').click({ force: true });
        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-3"]').should('not.exist');

        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-4"]').click({ force: true });
        cy.get('[data-test-id="button-invite-collaborators"]').click({ force: true });
        cy.get('[data-test-id="link-invite-collaborators"]').click({ force: true });
        cy.get('[data-test-id="button-invite-collaborators"]').click({ force: true });
        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-4"]').should('not.exist');

        cy.get('[data-test-id="project-navigation-overview"]').click({ force: true });
        cy.get('[data-test-id="opening-onboarding-tutorial"]').should('not.exist');
    });

    it('follows the tutorial steps correctly if already advising the project', () => {
        cy.login('conseiller1');
        cy.visit('/project/2');

        cy.get('[data-test-id="onboarding-tutorial__popup-content"]').should('exist');
        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-1"]').click({ force: true });
        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-1"]').should('not.exist');

        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-2"]').click({ force: true });
        cy.get('[data-test-id="project-navigation-knowledge"]').click({ force: true });
        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-2"]').should('not.exist');

        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-3"]').click({ force: true });
        cy.get('[data-test-id="project-navigation-conversations-new"]').click({ force: true });
        cy.get('[data-test-id="tiptap-editor-content"]').click({ force: true });
        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-3"]').should('not.exist');

        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-4"]').click({ force: true });
        cy.get('[data-test-id="button-invite-collaborators"]').click({ force: true });
        cy.get('[data-test-id="link-invite-collaborators"]').click({ force: true });
        cy.get('[data-test-id="button-invite-collaborators"]').click({ force: true });
        cy.get('[data-test-id="onboarding-tutorial__popup-challenge-4"]').should('not.exist');

        cy.get('[data-test-id="project-navigation-overview"]').click({ force: true });
        cy.get('[data-test-id="opening-onboarding-tutorial"]').should('not.exist');
    });

});
