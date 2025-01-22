import projects from '../../../fixtures/projects/projects.json';
import file from '../../../fixtures/documents/file.json';

const currentProject = projects[1];

describe('I can fill a project survey @critical', () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('fills up the survey and upload a file', () => {
    cy.visit(`/project/${currentProject.pk}/connaissance`);

    cy.get('[data-test-id="link-fill-survey-cta"]')
      .first()
      .click({ force: true });

    // cy.url().should('include', '/projects/survey/')

    cy.get('#form_answer-1').check({ force: true });

    cy.get('#input-project-comment')
      .type('Fake comment on first survey question', { force: true })
      .should('have.value', 'Fake comment on first survey question');

    cy.get('[name="attachment"]').selectFile(file.path, { force: true });

    cy.get('[data-test-id="button-submit-survey-questionset"]').click({
      force: true,
    });

    cy.get('#form_answer-1').check({ force: true });

    cy.get('#input-project-comment')
      .type('Fake comment on first survey question', { force: true })
      .should('have.value', 'Fake comment on first survey question');

    cy.get('[data-test-id="button-submit-survey-questionset"]').click({
      force: true,
    });

    cy.get('[data-test-id="project-navigation-knowledge"]').click({
      force: true,
    });
    cy.url().should('include', '/connaissance');
    cy.contains('Propriété du site');
    cy.contains('100%');
    cy.contains('Fake comment on first survey question');
  });

  it('can see and download the file', () => {
    cy.visit(`/project/${currentProject.pk}/documents`);

    cy.contains("Fichier récupéré de l'état des lieux");

    // test download with cy verification
    cy.get('[data-cy="attachment-filename"]')
      .invoke('text')
      .then((text) => {
        cy.get('[data-test-id="download-attachment"]').click();
        cy.readFile(`${Cypress.config('downloadsFolder')}/${text}`);
      });
  });
});
