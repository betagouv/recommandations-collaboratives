import projects from '../../../fixtures/projects/projects.json';

// pk 34 - conseiller1 advisor, published fixture reco "Reco publiée fixture".
const currentProject = projects.find((p) => p.pk === 34);

describe('I cannot unpublish a recommendation anymore @page-projet-recommandations @page-projet-recommandations-brouillon', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('cannot turn a published recommendation back into a draft', () => {
    cy.visit(`/project/${currentProject.pk}/conversations`);

    // Open the edit page of the published fixture recommendation.
    cy.get('[data-test-id="message-edit-recommendation"]').first().click({
      force: true,
    });
    cy.url().should('include', '/update');

    // A published recommendation can no longer be saved as a draft.
    cy.get('[data-test-id="publish-draft-task-button"]').should('not.exist');
  });
});
