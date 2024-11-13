import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe("I can't access privates notes as a non positionned adviser", () => {
  beforeEach(() => {
    cy.login('conseiller3');
  });

  it('goes to the project page and not beeing able to see the private note tab', () => {
    cy.visit(`/project/${currentProject.pk}`);

    cy.contains('Suivi interne').should('not.exist');
  });
});
