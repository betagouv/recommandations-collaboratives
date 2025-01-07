import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[1];

describe("I can go to action page but can't see the loop to access the inline tasks", () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it("goes to action page and can't see inline tasks loop button", () => {
    cy.visit(`/project/${currentProject.pk}/actions`);

    cy.get('#tasks-inline-button').should('not.exist');
  });
});

// page recommandations
