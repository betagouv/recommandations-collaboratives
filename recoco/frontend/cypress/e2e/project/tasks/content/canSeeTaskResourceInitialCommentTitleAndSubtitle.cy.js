import resources from '../../../../fixtures/resources/resources.json';
import projects from '../../../../fixtures/projects/projects.json';
import sharedContentsPanel from '../../../../support/tools/sharedContentsPanel';
import resourcePreviewPanel from '../../../../support/tools/resourcePreviewPanel';

const currentResource = resources[4]; // "Resource 1 - publiée" (pk 2)
// pk 37 - conseiller1 advisor, published fixture reco with resource pk
const currentProject = projects.find((p) => p.pk === 37);

describe('I can see a recommendation resource with its initial comment @page-projet-recommandations @page-projet-recommandations-modal', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('sees the initial comment, title and subtitle of a recommendation with a resource', () => {
    cy.visit(`/project/${currentProject.pk}/conversations`);

    // The resource title and subtitle are shown on the recommendation card.
    sharedContentsPanel.openFromTopic('recommendations');
    sharedContentsPanel
      .getRecommendationCards()
      .should('contain.text', currentResource.fields.title)
      .and('contain.text', currentResource.fields.subtitle);

    // The detail panel shows the advisor initial comment.
    sharedContentsPanel.consultRecommendation(0);
    resourcePreviewPanel.expectOpen();
    cy.get('[data-test-id="resource-preview-panel"]').should(
      'contain.text',
      'Commentaire initial fixture'
    );
  });
});
