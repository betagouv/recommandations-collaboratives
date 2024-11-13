import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can read only public notes', () => {
  beforeEach(() => {
    cy.login('conseiller3');
  });

  it('goes to public notes and read only content', () => {
    cy.visit(`/project/${currentProject.pk}/conversations`);

    cy.get('textarea').should('not.exist');
  });
});
