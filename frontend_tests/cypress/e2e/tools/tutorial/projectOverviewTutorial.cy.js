import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[1];
const currentProject2 = projects[24];

describe('I can follow the project tutorial', () => {
  xit('displays the launcher tutorial on the overview window as regional advisor', () => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}`);
    cy.get('[data-test-id="tutorial-project-launcher"]').should.exist;
  });

  xit('snooze the tutorial and tutorial disappear', () => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}`);

    cy.get('[data-test-id="snooze-tutorial"]').click();
    cy.visit(`/project/${currentProject.pk}`);
    cy.get('[data-test-id="tutorial-project-launcher"]').should('not.exist');
  });

  xit('fills up the tutorial and tutorial disappear', () => {
    cy.login('conseiller2');
    cy.visit(`/project/2`);

    cy.get('[data-test-id="button-join-as-advisor"]').click();
    cy.get('[data-test-id="launch-tutorial"]').click();
    cy.get('[data-test-id="tutorial-project-launcher"]').should(
      'not.be.visible'
    );
    cy.get('[data-test-id="project-overview-tutorial"]').should.exist;
    cy.get('.introjs-skipbutton').click();
    cy.get('[data-test-id="project-overview-tutorial"]').should('not.exist');
  });


  xit('displays the launcher tutorial on the overview window as advisor', () => {
    cy.login('conseiller3');
    cy.visit(`/project/${currentProject.pk}`);
    cy.becomeAdvisor(currentProject.pk);
    cy.get('[data-test-id="tutorial-project-launcher"]').should.exist;
  });

  it('displays the launcher tutorial on the overview window as observer', () => {
    cy.login('staff');
    cy.visit(`/project/${currentProject.pk}`);
    cy.becomeObserver(currentProject.pk);
    cy.get('[data-test-id="tutorial-project-launcher"]').should.exist;
  });

  it('displays the launcher tutorial on the overview window as regional advisor not on the right region ', () => {
    cy.login('conseiller4');
    cy.visit(`/project/${currentProject2.pk}`);
    cy.get('[data-test-id="tutorial-project-launcher"]').should.exist;
  });

  xit('displays the launcher tutorial on the overview window as regional advisor not on the right region', () => {
    cy.login('conseiller4');
    cy.visit(`/project/25`);
    cy.get('[data-test-id="tutorial-project-launcher"]').should.exist;
  });
});
