import projects from '../../../../../fixtures/projects/projects.json';

const currentProject = projects[1];

describe('I can go to administration area of a project and revoke an invite for a member', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('goes to the administration tab of a project and revoke the member invitation', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.get("[data-test-id='navigation-administration-tab']").click({
      force: true,
    });
    cy.url().should('include', '/administration');

    cy.get('[data-cy="button-invite-project-member"]').click();

    cy.get('#invite-member-modal')
      .get('#invite-email')
      .type('collectivitybyjean@test.fr', { force: true })
      .should('have.value', 'collectivitybyjean@test.fr');

    cy.get('#invite-member-modal')
      .get('#invite-message')
      .type(
        `Bonjour collectivitybyjean@test.fr, je t'invite à conseiller mon dossier ${currentProject.fields.name}`,
        { force: true }
      )
      .should(
        'have.value',
        `Bonjour collectivitybyjean@test.fr, je t'invite à conseiller mon dossier ${currentProject.fields.name}`
      );

    cy.get('#invite-member-modal')
      .contains("Envoyer l'invitation")
      .click({ force: true });

    cy.get("[data-test-id='administration-member-invitation-list']")
      .siblings('ul')
      .children('li')
      .contains('collectivitybyjean@test.fr');

    cy.get("[data-test-id='administration-member-invitation-list']")
      .siblings('ul')
      .children('li')
      .contains('collectivitybyjean@test.fr')
      .parent()
      .parent()
      .parent()
      .siblings()
      .find('#revoke-invite-member')
      .click({ force: true });
    cy.contains(
      `L'invitation de collectivitybyjean@test.fr a bien été supprimée.`
    );
  });
});
