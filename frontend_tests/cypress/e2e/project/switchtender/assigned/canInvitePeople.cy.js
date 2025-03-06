import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can invite people', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('goes to share a project page', () => {
    cy.visit(`/project/${currentProject.pk}`);

    cy.get('[data-cy="invite-project-member-button"]').click();

    cy.get('#invite-member-modal')
      .get('#invite-email')
      .type('member@test.fr', { force: true })
      .should('have.value', 'member@test.fr');

    cy.get('#invite-member-modal')
      .get('#invite-message')
      .type(
        "Bonjour membre, je t'invite à conseiller mon projet friche numéro 2",
        { force: true }
      )
      .should(
        'have.value',
        "Bonjour membre, je t'invite à conseiller mon projet friche numéro 2"
      );

    cy.get('#invite-member-modal')
      .contains("Envoyer l'invitation")
      .click({ force: true });
    cy.contains(
      "Un courriel d'invitation à rejoindre le projet a été envoyé à member@test.fr"
    );
  });
});
