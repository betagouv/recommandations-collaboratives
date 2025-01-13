import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[10];

describe('I can go to tasks tab', () => {
  before(() => {
    cy.login('conseiller1');
    cy.becomeAdvisor(currentProject.pk);
  });

  it('creates a single task and display a singular label for new tasks banner', () => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}/actions`);
    cy.createTask(1);
    cy.logout();

    cy.login('collectivité1');
    cy.visit(`/project/${currentProject.pk}/actions`);
    cy.contains('Vous avez 1 recommandation non lue');
    cy.get('[data-test-id="banner-new-tasks"]')
      .find('[data-test-id="img-presentation"]')
      .testImage('img-presentation', 'svg');
  });

  it('display a plural label for new tasks banner', () => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}/actions`);
    cy.createTask(2);
    cy.logout();

    cy.login('collectivité1');
    cy.visit(`/project/${currentProject.pk}/actions`);
    cy.contains('Vous avez 2 recommandations non lues');
  });
});


// page recommandations
