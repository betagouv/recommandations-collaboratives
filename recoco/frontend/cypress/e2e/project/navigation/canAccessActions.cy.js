import projects from '../../../fixtures/projects/projects.json';
import sharedContentsPanel from '../../../support/tools/sharedContentsPanel';

const currentProject = projects[1]; // pk 2 - conseiller1 advisor, collectivité1 owner
// pk 33 - conseiller1 advisor, published fixture reco.
const advisorTestProject = projects.find((p) => p.pk === 33);

describe('I can access the conversation tab in a project as a member @navigation-projet @page-projet-recommandations', () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('goes to the conversation page of my project and opens the recommendations panel', () => {
    cy.visit(`/project/${advisorTestProject.pk}`);
    cy.get('[data-test-id="project-navigation-conversations-new"]').click({
      force: true,
    });
    cy.url().should('include', '/conversations');
    sharedContentsPanel.openFromTopic('recommendations');
    sharedContentsPanel
      .getRecommendationCards()
      .should('contain.text', 'Reco navigation fixture');
  });
});

describe('I can access the conversation tab in a project as an advisor @navigation-projet @page-projet-recommandations', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('goes to the conversation page and opens the recommendations panel', () => {
    cy.visit(`/project/${advisorTestProject.pk}/conversations`);

    sharedContentsPanel.openFromTopic('recommendations');
    sharedContentsPanel
      .getRecommendationCards()
      .should('contain.text', 'Reco navigation fixture');
  });
});
