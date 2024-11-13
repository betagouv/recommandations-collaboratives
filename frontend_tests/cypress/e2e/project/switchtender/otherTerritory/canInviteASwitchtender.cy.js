import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can invite a switchtender as a regional actor', () => {
  beforeEach(() => {
    cy.login('conseiller3');
  });

  it('goes to the overview page and invite a switchtender', () => {
    cy.visit(`/project/${currentProject.pk}`);
  });
});
