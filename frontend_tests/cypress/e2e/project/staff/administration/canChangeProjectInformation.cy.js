import projects from '../../../../fixtures/projects/projects.json';

const currentProject = projects[1];

describe('I can go to administration area of a project and change general information', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('goes to the administration tab of a project general information', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.get("[data-test-id='navigation-administration-tab']").click({
      force: true,
    });
    cy.url().should('include', '/administration');

    cy.get('#id_name')
      .clear({ force: true })
      .type(`${currentProject.fields.name} updated`, { force: true })
      .should('have.value', `${currentProject.fields.name} updated`);

    cy.get('#input-project-description')
      .clear({ force: true })
      .type(`${currentProject.fields.description} updated`, { force: true })
      .should('have.value', `${currentProject.fields.description} updated`);

    cy.contains('Modifier les informations du dossier').click({ force: true });

    cy.url().should('include', '/presentation');

    cy.contains(`${currentProject.fields.description} updated`);
  });
});
