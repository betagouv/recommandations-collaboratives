import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[1];

describe('I can go to overview tab', () => {
  beforeEach(() => {
    cy.login('staff');
  });

  it('see the project phone if no project owner phone number', () => {
    cy.visit(`/project/${currentProject.pk}`);

    //Used to match phone logic returned from django
    cy.contains(`${currentProject.fields.phone}`);
  });
});
