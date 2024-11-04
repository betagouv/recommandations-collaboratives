import projects from '../../../fixtures/projects/projects.json';
import projectView from '../../../support/views/project';

const ownerEmail = 'bob@test.fr';
describe.skip('As project owner, I can see project email reminders', () => {
  it('Displays no reminder message on projects with no scheduled emails', () => {
    const currentProject = projects[19];
    cy.login('collectivité1');
    cy.visit(`/project/${currentProject.pk}`);
    projectView.checkNextEmailReminder({});
  });

  it('Displays a reminder message when an email is scheduled to be sent', () => {
    const currentProject = projects[20];
    cy.login('collectivité1');
    cy.visit(`/project/${currentProject.pk}`);
    projectView.checkNextEmailReminder({ email: ownerEmail });
  });

  it('Reminders settings popup is accessible and provides access to preferences panel', () => {
    const currentProject = projects[20];
    cy.login('collectivité1');
    cy.visit(`/project/${currentProject.pk}`);
    projectView.openEmailReminderTooltip('exist', { email: ownerEmail });
  });
});
