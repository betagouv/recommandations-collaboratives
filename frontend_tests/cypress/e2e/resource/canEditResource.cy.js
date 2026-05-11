const now = new Date();

const resource = {
  title: 'Nouvelle ressource de test',
  subtitle: 'Soustitre de la ressource de test',
  summary: `test : ${now}`,
  deparments: {
    index: 1,
    name: 'Département de test numéro 2',
  },
  tags: 'etiquette1',
  expires_on: '2022-12-20',
};

describe('I can edit a resource as a staff @acces-ressources', () => {
  it('edits a resource', () => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit('/ressource/1/');
    cy.get('[data-test-id="edit-resource"]').click();
    cy.url().should('include', '/ressource/1/update/');

    cy.get('#id_title')
      .clear({ force: true })
      .type(resource.title, { force: true })
      .should('have.value', resource.title);

    cy.get('#id_subtitle')
      .clear({ force: true })
      .type(resource.subtitle, { force: true })
      .should('have.value', resource.subtitle);

    cy.get('#id_summary')
      .clear({ force: true })
      .type(resource.summary, { force: true })
      .should('have.value', resource.summary);

    cy.get('#id_tags')
      .clear({ force: true })
      .type(resource.tags, { force: true })
      .should('have.value', resource.tags);

    cy.get('#id_expires_on')
      .clear({ force: true })
      .type(resource.expires_on, { force: true })
      .should('have.value', resource.expires_on);

    cy.get('[data-test-id="publish-resource-btn"]').click({ force: true });

    cy.url().should('include', '/ressource/');

    cy.contains(resource.title);
    cy.contains(resource.subtitle);
    cy.contains(resource.summary);
    cy.contains(resource.tags);
  });
});
