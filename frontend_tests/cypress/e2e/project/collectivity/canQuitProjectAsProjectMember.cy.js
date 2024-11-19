import projects from '../../../fixtures/projects/projects.json';
import projectView from '../../../support/views/project';

const currentProject = projects[17];

describe('As collectivity project member, I can quit a project if I am not the owner', () => {
  it('I can quit a project from the project preferences', () => {
    cy.login('collectivité2');
    cy.visit(`/project/${currentProject.pk}/administration/`);
    projectView.quitProject('member');
  });
});
