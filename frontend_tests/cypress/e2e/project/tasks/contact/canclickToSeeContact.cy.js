import projects from '../../../../fixtures/projects/projects.json';

const currentProject = projects[24]; // à adpater quand le code sera merge sur develop ou créer une commande pour sélectionner un projet par id

describe('I can see contacts information', () => {
  beforeEach(() => {
    cy.login('bob');
  });

  it('click to see contat info', () => {
    cy.visit(`/project/${currentProject.pk}/actions`);
    cy.get('[data-test-id="task-item"]').first().click();

    cy.get('iframe')
        .its('0.contentDocument.body')
        .should('not.be.empty')
        // eslint-disable-next-line @typescript-eslint/unbound-method
        .then(cy.wrap)
        .find('#caVaMarcher')
        .each(($button)=>{cy.wrap($button).click({ force: true })});
    cy.wait(5000);
    cy.visit(`/project/${currentProject.pk}/actions`);
    cy.get('[data-test-id="task-item"]').first().click();
    cy.get('[data-test-id="see-contact-info-button"]').should('not.exist');
//   cy.get('[data-test-id="see-contact-info-button"]').each(($button)=>{cy.wrap($button).click({ force: true })});
  });
//   it('doesnt have to click again to see the same contact info', () => {


//   });
});
