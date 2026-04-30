import projects from '../../../../fixtures/projects/projects.json';
import projectView from '../../../../support/views/project';

const ownerEmail = 'bob@test.fr';
describe('As project advisor, I can see project email reminders @page-projet-presentation-rappel-email', () => {
  it('Displays no reminder message on projects with no scheduled emails', () => {
    const currentProject = projects.find((x) => x.pk == 20);
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}`);
    projectView.checkNextEmailReminder({ role: 'advisor' });
  });

  it('Displays a reminder message when an email is scheduled to be sent', () => {
    const currentProject = projects.find((x) => x.pk == 21);
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}`);
    projectView.checkNextEmailReminder({ email: ownerEmail });
  });

  it('Reminders settings popup is accessible and provides access to preferences panel', () => {
    const currentProject = projects.find((x) => x.pk == 21);
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}`);
    projectView.checkEmailReminderTooltip();
  });
});
