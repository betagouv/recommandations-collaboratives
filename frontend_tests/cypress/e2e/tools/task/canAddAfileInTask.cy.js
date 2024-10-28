import file from '../../../fixtures/documents/file.json';

describe('I can add a file in a task', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.createProject('file in task');
  });

  it('writes a message with a file', () => {
    cy.visit(`/projects`);
    cy.contains('file in task').first().click({ force: true });

    cy.becomeAdvisor();
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');

    cy.get("[data-test-id='submit-task-button']").click({ force: true });

    cy.get('#push-noresource').click({ force: true });

    const now = new Date();

    cy.get('#intent')
      .type('fake recommandation with no resource', { force: true })
      .should('have.value', 'fake recommandation with no resource');

    cy.get('textarea')
      .type(`fake recommandation content with no resource : ${now}`, {
        force: true,
      })
      .should(
        'have.value',
        `fake recommandation content with no resource : ${now}`
      );

    cy.get('[name="the_file"]').selectFile(file.path, { force: true });

    cy.get('[type=submit]').click({ force: true });

    cy.url().should('include', '/actions');

    cy.contains(`fake recommandation content with no resource`);
  });
});
