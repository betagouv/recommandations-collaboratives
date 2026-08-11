/**
 * Vérifie qu'un staff peut arrêter un portail depuis /crm/site_config et que,
 * une fois arrêté :
 *   - la bannière « Site inactif » s'affiche sur la page d'accueil,
 *   - les boutons permettant de déposer un nouveau dossier disparaissent
 *     (« Solliciter » sur la home, « Déposer un dossier » dans le menu top).
 *
 * Le portail est systématiquement réactivé en fin de test pour ne pas
 * polluer les autres suites.
 */

const BANNER_TEXT = 'Site inactif';
const STOP_BUTTON_LABEL = "Mettre le portail à l'arrêt";
const REACTIVATE_BUTTON_LABEL = 'Réactiver le portail';
const CONFIRM_STOP_LABEL = "Oui, mettre à l'arrêt";
const CONFIRM_REACTIVATE_LABEL = 'Oui, réactiver';

function stopPortal() {
  cy.login('staff');
  cy.visit('/crm/site_config');
  cy.get('body').then(($body) => {
    if ($body.text().includes(STOP_BUTTON_LABEL)) {
      cy.contains('button', STOP_BUTTON_LABEL).click({ force: true });
      cy.contains('button', CONFIRM_STOP_LABEL).click({ force: true });
      cy.url().should('include', '/crm/site_config');
      cy.contains('button', REACTIVATE_BUTTON_LABEL).should('exist');
    }
  });
  cy.logout();
}

function reactivatePortal() {
  cy.login('staff');
  cy.visit('/crm/site_config');
  cy.get('body').then(($body) => {
    if ($body.text().includes(REACTIVATE_BUTTON_LABEL)) {
      cy.contains('button', REACTIVATE_BUTTON_LABEL).click({ force: true });
      cy.contains('button', CONFIRM_REACTIVATE_LABEL).click({ force: true });
      cy.url().should('include', '/crm/site_config');
      cy.contains('button', STOP_BUTTON_LABEL).should('exist');
    }
  });
  cy.logout();
}

describe('Stopping a portal disables new project submissions @portail-arrete', () => {
  after(() => {
    cy.logout();
    reactivatePortal();
  });

  it('lets a staff user stop the portal from /crm/site_config', () => {
    stopPortal();
  });

  it('shows the « Site inactif » banner on the home page for anonymous visitors', () => {
    cy.visit('/');
    cy.contains(BANNER_TEXT).should('be.visible');
  });

  it('hides the « Solliciter » button on the home page for anonymous visitors', () => {
    cy.visit('/');
    cy.get('[data-test-id="button-need-help"]').should('not.exist');
  });

  it('hides the « Déposer un dossier » button in the top menu for a collectivity', () => {
    cy.login('collectivité1');
    cy.visit('/');
    cy.contains(BANNER_TEXT).should('be.visible');
    cy.get('[data-test-id="create-project"]').should('not.exist');
  });

  it('hides the « Déposer un dossier » button in kanban for staff', () => {
    cy.login('staff');
    cy.visit('/projects/');
    cy.get('[data-test-id="new-project-btn-toolbar"]').should('not.exist');
  });

  it('keeps the « Solliciter » button hidden for an authenticated collectivity on the home page', () => {
    cy.login('collectivité1');
    cy.visit('/');
    cy.get('[data-test-id="button-need-help"]').should('not.exist');
  });
});
