import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[2];

describe('I can invite a member', () => {
  const invitedFullName = 'New Member';
  const invitedEmail = 'new.member@test.fr';
  const inviterFullName = 'Boba collectivité';
  const inviterEmail = 'boba@test.fr';
  const project = 'Friche numéro 2';

  it('goes to the overview page and invite a member', () => {
    cy.login('collectivité2');
    const message = `Bonjour ${invitedFullName}, je t'invite à conseiller mon dossier ${project} ${invitedEmail}`;
    const sentNotification = `Un courriel d'invitation à rejoindre le dossier a été envoyé à ${invitedEmail}`;

    cy.visit(`/project/${currentProject.pk}`);

    cy.get('[data-cy="invite-project-member-button"]').click();

    cy.get('#invite-member-modal')
      .get('#invite-email')
      .type(invitedEmail, { force: true })
      .should('have.value', invitedEmail);

    cy.get('#invite-member-modal')
      .get('#invite-message')
      .type(message, { force: true })
      .should('have.value', message);

    cy.get('#invite-member-modal')
      .contains("Envoyer l'invitation")
      .click({ force: true })
      .wait(500);
    cy.contains(sentNotification);
  });

  it('can see a notification of the invitation on the project activity feed', () => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit(`/project/${currentProject.pk}`);
    cy.get('[data-test-id="fr-consent-banner"]')
      .find('[data-test-id="button-consent-accept-all"]')
      .click({ force: true })
      .wait(300);
    cy.get('[data-test-id="project-activity-link"]').click({ force: true });
    cy.get('[data-test-id="project-activity-tracking-staff"]')
      .find('[data-test-id="project-activity-notification"]')
      .then(() => {
        cy.contains(inviterFullName);
        cy.contains('a invité ');
        cy.contains(invitedEmail);
        cy.contains('en tant que demandeur ou partenaire');
      });
  });
});
