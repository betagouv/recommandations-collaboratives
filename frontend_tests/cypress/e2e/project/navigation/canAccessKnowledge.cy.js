import projects from '../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can access knowledge tab in a project as a member', () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('goes to the knowledge page of my project', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.get("[data-test-id='project-navigation-knowledge']").click({
      force: true,
    });
    cy.url().should('include', '/connaissance');
  });
});

describe('I can access knowledge tab in a project as an advisor', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('goes to the knowledge page of my project', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.get("[data-test-id='project-navigation-knowledge']").click({
      force: true,
    });
    cy.url().should('include', '/connaissance');
  });
});
