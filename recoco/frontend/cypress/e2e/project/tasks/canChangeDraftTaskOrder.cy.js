import projects from '../../../fixtures/projects/projects.json';
import sharedContentsPanel from '../../../support/tools/sharedContentsPanel';

const currentProject = projects.find((p) => p.pk === 15);

describe('I can reorder draft recommendations @page-projet-recommandations', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.resetProjectRecommendations(currentProject.pk);
    cy.createTaskViaApi(currentProject.pk, {
      intent: `Brouillon A ${Date.now()}`,
      order: 1,
    });
    cy.createTaskViaApi(currentProject.pk, {
      intent: `Brouillon B ${Date.now()}`,
      order: 2,
    });
  });

  it('reorders draft recommendations with the arrow buttons', () => {
    cy.visit(`/project/${currentProject.pk}/conversations`);
    sharedContentsPanel.openFromTopic('drafts');
    sharedContentsPanel.expectDraftCount(2);

    // Capture the title currently at the top, move it down, then check the
    // order actually changed.
    sharedContentsPanel
      .getDraftCards()
      .eq(0)
      .find('[data-test-id="recommendation-card-title"]')
      .invoke('text')
      .then((firstTitle) => {
        sharedContentsPanel.moveDraftDown(0);

        cy.contains("L'ordre des brouillons a été sauvegardé");

        sharedContentsPanel
          .getDraftCards()
          .eq(1)
          .find('[data-test-id="recommendation-card-title"]')
          .should('have.text', firstTitle);
        sharedContentsPanel.expectDraftPosition(1, 2);
      });
  });
});
