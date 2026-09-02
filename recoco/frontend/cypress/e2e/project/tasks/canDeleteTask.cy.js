import projects from '../../../fixtures/projects/projects.json';
import sharedContentsPanel from '../../../support/tools/sharedContentsPanel';

const currentProject = projects.find((p) => p.pk === 16);

describe('I can delete a draft recommendation @page-projet-recommandations @page-projet-recommandations-suppression', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.resetProjectRecommendations(currentProject.pk);
    cy.createTaskViaApi(currentProject.pk, {
      intent: `Brouillon à supprimer ${Date.now()}`,
    });
  });

  it('deletes a draft recommendation from the shared contents panel', () => {
    cy.visit(`/project/${currentProject.pk}/conversations`);
    sharedContentsPanel.openFromTopic('drafts');
    sharedContentsPanel.expectDraftCount(1);

    sharedContentsPanel.deleteDraft(0);

    cy.visit(`/project/${currentProject.pk}/conversations`);
    cy.get('[data-test-id="open-shared-drafts"]').should('not.exist');
  });
});
