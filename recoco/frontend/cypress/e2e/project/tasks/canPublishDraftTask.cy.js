import projects from '../../../fixtures/projects/projects.json';
import sharedContentsPanel from '../../../support/tools/sharedContentsPanel';

const currentProject = projects.find((p) => p.pk === 29);

describe('I can publish a draft recommendation @page-projet-recommandations @page-projet-recommandations-creation', () => {
  const intent = `Brouillon à publier ${Date.now()}`;

  beforeEach(() => {
    cy.login('conseiller1');
    cy.resetProjectRecommendations(currentProject.pk);
    cy.createTaskViaApi(currentProject.pk, { intent });
  });

  it('sees the draft in the drafts tab and publishes it', () => {
    cy.visit(`/project/${currentProject.pk}/conversations`);
    sharedContentsPanel.openFromTopic('drafts');
    sharedContentsPanel.expectDraftCount(1);
    sharedContentsPanel.getDraftCards().should('contain.text', intent);

    // Publishing removes it from the drafts tab...
    sharedContentsPanel.publishDraft(0);
    sharedContentsPanel.expectDraftCount(0);

    // ...and it becomes a published recommendation.
    sharedContentsPanel.switchTab('recommendations');
    sharedContentsPanel.getRecommendationCards().should('contain.text', intent);
  });
});
