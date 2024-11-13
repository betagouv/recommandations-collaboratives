import projects from '../../../fixtures/projects/projects.json';
import editor from '../../../support/tools/editor';

const currentProject = projects[1];

describe("I can't send an empty message", () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('shows a disabled send message button', () => {
    cy.visit(`/project/${currentProject.pk}/conversations`);

    cy.get('[data-test-id="send-message-conversation"]').should(
      'have.attr',
      'disabled'
    );
  });

  it('enables the send message if I type a message', () => {
    cy.visit(`/project/${currentProject.pk}/conversations`);

    editor.writeMessage(`new message`);

    cy.get('[data-test-id="send-message-conversation"]').should(
      'not.have.attr',
      'disabled'
    );
  });

  it('disables the send message if I erase my message (empty message)', () => {
    cy.visit(`/project/${currentProject.pk}/conversations`);

    editor.writeMessage(`new message`);

    cy.get('[data-test-id="send-message-conversation"]').should(
      'not.have.attr',
      'disabled'
    );

    editor.clear();

    cy.get('[data-test-id="send-message-conversation"]').should(
      'have.attr',
      'disabled'
    );
  });
});
