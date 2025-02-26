let currentProjectId;
describe('I can go to tasks tab', () => {
  before(() => {
    cy.login('conseiller1');
    cy.createProject('task above').then((projectId) => {
      currentProjectId = projectId;
      cy.visit(`/project/${currentProjectId}`);
      cy.becomeAdvisor(currentProjectId); // A remplacer par une fixture avec un user déjà advisor du dossier
      cy.visit(`/project/${currentProjectId}/actions`);

      cy.createTask(1);
      cy.createTask(2);
    });
  });

  beforeEach(() => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProjectId}/actions`);
  });

  it('change task position above', () => {
    cy.get('#task-move-above').click();
  });

  it('change task position below', () => {
    cy.get('#task-move-below').click();
  });
});

// page recommandation
