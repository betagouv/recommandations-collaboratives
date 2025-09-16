describe('Project share between portal', () => {
  it('display share by and with portal on kanban', () => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit('/projects');
    cy.get('[data-cy="kanban-project-shared-by-origin"]')
      .should('be.visible')
      .should('include.text', 'example2');
    cy.get('[data-cy="kanban-project-shared-with"]')
      .should('be.visible')
      .should('include.text', 'example3');
  });

  it('display share by portal on moderation', () => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit('/projects/moderation');
    cy.get('[data-cy="moderation-folder-shared-by"]')
      .should('be.visible')
      .should('include.text', 'example2');
  });

  it('display current portal EDL first', () => {
    cy.login('collectivité1');
    cy.visit('/project/23/connaissance');

    cy.get('[data-cy="survey-name"]').each(($el, index) => {
      if (index === 0) {
        cy.wrap($el).should('contain.text', 'Questionnaire example');
      }
    });
  });
});
