import projects from '../../../../fixtures/projects/projects.json';

const currentProject = projects[24]; // à adpater quand le code sera merge sur develop ou créer une commande pour sélectionner un projet par id

describe('I can see contacts information', () => {
  beforeEach(() => {
    cy.login('bob');
  });

  it('click to see contat info and doesnt have to click again', () => {
    cy.visit(`/ressource/2`);
    cy.get('[data-test-id="see-contact-info-button"]').each(($button)=>{cy.wrap($button).click({ force: true })});
    cy.get('[data-test-id="see-contact-info-button"]').should('not.be.visible');
    cy.visit(`/ressource/2`);
    cy.get('[data-test-id="see-contact-info-button"]').should('not.be.visible');
  });

});
