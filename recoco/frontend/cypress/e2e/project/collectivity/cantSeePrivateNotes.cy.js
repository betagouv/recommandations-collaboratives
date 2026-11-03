import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[3];

describe('I can access and use public notes @page-projet-espace-conseiller', () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('goes to public notes', () => {
    cy.visit(`/project/${currentProject.pk}`);

    cy.contains('Suivi interne').should('not.exist');
  });
});
