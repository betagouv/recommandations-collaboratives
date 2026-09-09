import projects from '../../../fixtures/projects/projects.json';
import sharedContentsPanel from '../../../support/tools/sharedContentsPanel';

const currentProject = projects.find((p) => p.pk === 32);

describe('I can access the recommandations @page-projet-recommandations', () => {
  it('sees the recommendations shared by the advisor in the conversation', () => {
    // Owner (collectivity) can read the recommendation
    // published by the advisor, but cannot create one.
    cy.login('collectivité1');
    cy.visit(`/project/${currentProject.pk}/conversations`);

    sharedContentsPanel.openFromTopic('recommendations');
    sharedContentsPanel
      .getRecommendationCards()
      .should('contain.text', 'Reco collectivité fixture');

    cy.get('[data-test-id="create-task-button"]').should('not.exist');
  });
});
