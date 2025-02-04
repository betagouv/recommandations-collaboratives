import project from '../../../fixtures/projects/project.json';

const projectName = 'New project onboarding answer';
let projetId;
describe('I can see onboarding answer on the overview tab', () => {
  before(() => {
    cy.login('collectivité1');
    cy.createProject(projectName).then((projectId) => {
      projetId = projectId;
      cy.logout();
    });
  });

  afterEach(() => {
    cy.logout();
  });

  it('should see the project description on overview tab as staff', () => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit(`/project/${projetId}`);
    cy.get('[data-test-id="project-information-card-context"]').should(
      'contain.text',
      project.description
    );
  });

  it('should see the project description on overview tab as collectivity', () => {
    cy.login('collectivité1');
    cy.visit(`/project/${projetId}`);
    cy.get('[data-test-id="project-information-card-context"]').should(
      'contain.text',
      project.description
    );
  });

  // TODO add fixture for complete questions onboarding
});
