import projects from '../../../../fixtures/projects/projects.json';
import users from '../../../../fixtures/users/users.json';

const currentProject = projects[1];
const userToInvite = users[6];

describe('I can go to administration area of a project and send back an invite for a member', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('goes to the administration tab of a project and send back the member invitation', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.get("[data-test-id='navigation-administration-tab']").click({
      force: true,
    });
    cy.url().should('include', '/administration');

    cy.get('[data-cy="button-invite-project-member"]').click();

    cy.get('#invite-member-modal')
      .get('#invite-email')
      .type(`${userToInvite.fields.email}`, { force: true })
      .should('have.value', `${userToInvite.fields.email}`);

    cy.get('#invite-member-modal')
      .get('#invite-message')
      .type(
        `Bonjour ${userToInvite.fields.first_name}, je t'invite à conseiller mon dossier ${currentProject.fields.name}`,
        { force: true }
      )
      .should(
        'have.value',
        `Bonjour ${userToInvite.fields.first_name}, je t'invite à conseiller mon dossier ${currentProject.fields.name}`
      );

    cy.get('#invite-member-modal')
      .contains("Envoyer l'invitation")
      .click({ force: true });

    cy.get("[data-test-id='administration-member-invitation-list']")
      .siblings('ul')
      .children('li')
      .contains(userToInvite.fields.email);
    cy.get("[data-test-id='administration-member-invitation-list']")
      .siblings('ul')
      .children('li')
      .contains(userToInvite.fields.email)
      .parent()
      .parent()
      .parent()
      .siblings()
      .find('#resend-invite-member')
      .click({ force: true });
    // cy.contains(`Bobette@test.fr a bien été relancé par courriel.`)
  });
});
