import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[1];

describe('I can follow the project tutorial', () => {
  beforeEach(() => {
    // cy.login('collectivité1');
    // cy.visit(`/project/${currentProject.pk}`);
    // const challengeCode = 'project-advisor-overview';
    // cy.intercept(`/api/challenges/definitions/${challengeCode}`, {
    //   fixture: 'settings/challengeDefinition',
    // });
    // cy.intercept(`/api/challenges/${challengeCode}`, {
    //   fixture: 'settings/challenge',
    // });
  });

  it('displays the launcher tutorial on the overview window', () => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}`);

    // cy.wait(8000);
    cy.get('[data-test-id="tutorial-project-launcher"]').should.exist;
  });

  it('snooze the tutorial and tutorial disappear', () => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}`);

    cy.get('[data-test-id="snooze-tutorial"]').click();
    cy.visit(`/project/${currentProject.pk}`);
    cy.get('[data-test-id="tutorial-project-launcher"]').should('not.exist');
  });

  it('fills up the tutorial and tutorial disappear', () => {
    cy.login('jeannot');
    cy.visit(`/project/2`);

    cy.get('[data-test-id="become-advisor"]').click();
    cy.get('[data-test-id="launch-tutorial"]').click();
    cy.get('[data-test-id="tutorial-project-launcher"]').should(
      'not.be.visible'
    );
    cy.get('[data-test-id="project-overview-tutorial"]').should.exist;
    cy.get('.introjs-skipbutton').click();
    cy.get('[data-test-id="project-overview-tutorial"]').should('not.exist');
  });
});
