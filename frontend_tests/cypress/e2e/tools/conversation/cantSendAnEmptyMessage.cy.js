import projects from '../../../fixtures/projects/projects.json';
import editor from '../../../support/tools/editor';

const currentProject = projects[1];

describe("I can't send an empty message @page-projet-conversations-nouveau-message", () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}/conversations`);
  });

  it('enables and disables the send message if I erase my message (empty message)', () => {
    editor.checkSubmitButton('be.disabled');

    cy.wait(500);

    editor.writeMessage(`new message`);

    editor.checkSubmitButton('not.be.disabled');

    editor.clear();

    editor.checkSubmitButton('be.disabled');
  });
});
