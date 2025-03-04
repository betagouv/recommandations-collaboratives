import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can read only public notes', () => {
  beforeEach(() => {
    cy.login('conseiller3');
  });

  it('cant goes to public notes ', () => {
    cy.visit(`/project/${currentProject.pk}/`);

    cy.get('[data-test-id="project-navigation-conversations"]').should(
      'be.disabled'
    );
  });
});
