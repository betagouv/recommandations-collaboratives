import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can advice a project', () => {
  beforeEach(() => {
    cy.login('conseiller2');
  });

  xit('goes to overview page and advise the project', () => {
    cy.visit(`/project/${currentProject.pk}`);

    // cy.contains("Conseiller ce dossier").click({ force: true })
    // cy.wait(500);
    // cy.contains("Ne plus conseiller ce dossier")
    // cy.contains("Jeanne Conseille")
  });
});
