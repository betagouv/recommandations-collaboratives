/**
 * Custom Cypress commands for various actions such as login, logout,
 * accepting/declining cookies, creating projects and tasks, and more.
 *
 * @module CypressCommands
 */

import users from '../fixtures/users/users.json';
import project from '../fixtures/projects/project.json';
import resources from '../fixtures/resources/resources.json';
import communes from '../fixtures/geomatics/commune.json';

const currentResource = resources[4];
const projectCommune = communes.find(
  (c) => c.fields.postal == project.postcode
);

/**
 * Logs in a user based on their role.
 *
 * @function login
 * @memberof Cypress.Commands
 * @param {string} role - The role of the user to log in as.
 */
Cypress.Commands.add('login', (role) => {
  let username = '';

  switch (role) {
    case 'jean': //conseiller
    case 'conseiller1': //conseiller
      username = users[1].fields.username;
      break;
    case 'jeanne': //conseiller
    case 'conseiller2': //conseiller
      username = users[2].fields.username;
      break;
    case 'jeannot': //conseiller
    case 'conseiller3': //conseiller
      username = users[3].fields.username;
      break;
    case 'bob': //collectivité
    case 'collectivité1': //collectivité
      username = users[4].fields.username;
      break;
    case 'boba': //collectivité
    case 'collectivité2': //collectivité
      username = users[5].fields.username;
      break;
    case 'bobette': //collectivité
    case 'collectivité3': //collectivité
      username = users[6].fields.username;
      break;
    case 'staff': //staff
      username = users[0].fields.username;
      break;
    case 'nonactive': //non active user
      username = users[8].fields.username;
      break;
    case 'national': // conseiller national
      username = users[7].fields.username;
      break;
    default:
      break;
  }
  cy.request({ url: '/accounts/login/' }).then((response) => {
    const setCookieValue = response.headers['set-cookie'][0];

    const regExp = /\=([^=]+)\;/;
    const matches = regExp.exec(setCookieValue);
    const token = matches[1];
    cy.request({
      method: 'POST',
      url: '/accounts/login/',
      form: true,
      body: {
        login: username,
        password: 'derpderp',
        csrfmiddlewaretoken: token,
      },
    }).then((response) => {
      cy.visit('/');
      cy.getCookie('sessionid').should('exist');
      cy.getCookie('csrftoken').should('exist');
    });
  });
});
// TODO Add a test to logout via ui
// Cypress.Commands.add('logout', () => {
//   cy.get('#user-menu-button').click({ force: true });
//   cy.contains('Déconnexion').click({ force: true });
// });

/**
 * Logs out the current user.
 *
 * @function logout
 * @memberof Cypress.Commands
 */
Cypress.Commands.add('logout', () => {
  cy.visit('/accounts/logout/');
});

/**
 * Accepts the cookies consent banner.
 *
 * @function acceptCookies
 * @memberof Cypress.Commands
 */
Cypress.Commands.add('acceptCookies', () => {
  cy.get('[data-test-id="fr-consent-banner"]')
    .find('[data-test-id="button-consent-accept-all"]')
    .click({ force: true });
  cy.visit('/');
});

/**
 * Declines the cookies consent banner.
 *
 * @function declineCookies
 * @memberof Cypress.Commands
 */
Cypress.Commands.add('declineCookies', () => {
  cy.get('[data-test-id="fr-consent-banner"]')
    .find('[data-test-id="button-consent-decline-all"]')
    .click({ force: true });
  cy.visit('/');
});

/**
 * Creates a new project with the given label and optional project object.
 *
 * @function createProject
 * @memberof Cypress.Commands
 * @param {string} label - The label for the new project.
 * @param {Object} [objProject=project] - Optional project object with additional details.
 */
Cypress.Commands.add('createProject', (label, objProject = project) => {
  cy.visit('/');

  cy.get('[data-test-id="button-need-help"]')
    .contains('Solliciter')
    .click({ force: true });

  cy.url().should('include', '/onboarding/project');

  cy.get('#id_name')
    .should('not.have.class', 'fr-input--error')
    .type(label || objProject.name || project.name, { delay: 0 })
    .should('have.value', label || objProject.name || project.name)
    .should('have.class', 'fr-input--valid');

  cy.get('#id_location')
    .should('not.have.class', 'fr-input--error')
    .type(objProject.location || project.location, { delay: 0 })
    .should('have.value', objProject.location || project.location)
    .should('have.class', 'fr-input--valid');

  cy.get('[data-test-id="input-postcode"]')
    .parent()
    .should('not.have.class', 'fr-input-group--error');

  cy.get('[data-test-id="input-postcode"]')
    .type(objProject.postcode || project.postcode, { delay: 0 })
    .should('have.value', objProject.postcode || project.postcode)
    .parent()
    .should('have.class', 'fr-input-group--valid');

  cy.get('[data-test-id="select-city"]')
    .should('not.have.class', 'fr-select-group--error')
    .focus();

  cy.get('[data-test-id="select-city"]')
    .should('contain.text', projectCommune.fields.name)
    .should('have.value', projectCommune.fields.insee)
    .parent()
    .should('have.class', 'fr-select-group--valid');

  cy.get('#id_description')
    .should('not.have.class', 'fr-input--error')
    .type(objProject.description || project.description, { delay: 0 })
    .should('have.value', objProject.description || project.description)
    .should('have.class', 'fr-input--valid');

  cy.get('button[type="submit"]').click();

  cy.url().should('include', '/onboarding/summary');

  cy.url().then((url) => {
    const idMatch = url.match(/\/onboarding\/summary\/(\d+)$/);

    if (idMatch) {
      const id = idMatch[1];
      cy.log(`L'ID récupéré est : ${id}`);
      cy.wrap(id).as('projectId');
    } else {
      throw new Error("ID non trouvé dans l'URL");
    }
  });
});

/**
 * Joins as an advisor if not already an advisor.
 *
 * @function becomeAdvisor
 * @memberof Cypress.Commands
 */
Cypress.Commands.add('becomeAdvisor', (projectId) => {
  cy.getCookie('csrftoken').then((csrfToken) => {
    cy.request({
      method: 'POST',
      url: `/project/${projectId}/switchtender/join`,
      headers: {
        'X-CSRFToken': csrfToken.value,
      },
    });
  });
});

/**
 * Creates a new task with the given label, topic, and options.
 *
 * @function createTask
 * @memberof Cypress.Commands
 * @param {string} label - The label for the new task.
 * @param {string} [topic=''] - The topic for the new task.
 * @param {boolean} [withResource=false] - Whether to associate a resource with the task.
 * @param {boolean} [draft=false] - Whether to save the task as a draft.
 */
Cypress.Commands.add(
  'createTask',
  (label, topic = '', withResource = false, draft = false) => {
    cy.get('body').then((body) => {
      if (body.find('[data-test-id="submit-task-button"]').length > 0) {
        cy.contains('Émettre une recommandation').click({
          force: true,
        });

        if (!withResource) {
          cy.get('#push-noresource').click({ force: true });

          cy.get('#intent')
            .type(`${label}`, { force: true })
            .should('have.value', `${label}`);
        } else {
          cy.get('#push-single').click({ force: true });
          cy.get('[data-test-id="search-resource-input"]').type(
            currentResource.fields.title,
            { force: true }
          );
          cy.get(`#resource-${currentResource.pk}`).check({
            force: true,
          });
        }

        cy.get('textarea')
          .type(`reco test from action description`, { force: true })
          .should('have.value', `reco test from action description`);

        if (topic !== '') {
          cy.get('#topic_name')
            .type(`${topic}`, { force: true })
            .should('have.value', `${topic}`);
        }

        if (draft) {
          cy.get('[data-test-id="publish-draft-task-button"]')
            .trigger('click')
            .click();
        } else {
          cy.get('[type=submit]').click({ force: true });
        }

        cy.url().should('include', '/actions');

        cy.contains('reco test from action');
      } else if (body.find('[data-test-id="create-task-button"]').length > 0) {
        cy.contains('Créer une recommandation').click({ force: true });

        cy.get('#push-noresource').click({ force: true });

        cy.get('#intent')
          .type(`${label}`, { force: true })
          .should('have.value', `${label}`);

        cy.get('textarea')
          .type(`reco test from action description`, { force: true })
          .should('have.value', `reco test from action description`);

        if (draft) {
          cy.get('[data-test-id="publish-draft-task-button"]')
            .trigger('click')
            .click();
        } else {
          cy.get('[type=submit]').click({ force: true });
        }

        cy.url().should('include', '/actions');

        cy.contains('reco test from action');
      } else {
        assert.isOk('task', "can't create task");
      }
    });
  }
);

/**
 * Approves a project with the given index.
 *
 * @function approveProject
 * @memberof Cypress.Commands
 * @param {number} index - The index of the project to approve.
 */
Cypress.Commands.add('approveProject', (index) => {
  cy.login('staff');
  cy.visit('nimda/projects/project/');
  cy.contains(`${project.name} ${index}`)
    .siblings('th.field-created_on.nowrap')
    .children('a')
    .click({ force: true });
  cy.get('#id_status').select(1);
  cy.get('#id_last_name')
    .type(`${project.last_name} ${index}`, { force: true })
    .should('have.value', `${project.last_name} ${index}`);
  cy.get('#id_first_name')
    .type(`${project.first_name} ${index}`, { force: true })
    .should('have.value', `${project.first_name} ${index}`);
  cy.contains('Enregistrer').click({ force: true });
  cy.contains('Déconnexion').click({ force: true });
  cy.visit('/');
});

/**
 * Navigates to a project with the given index.
 *
 * @function navigateToProject
 * @memberof Cypress.Commands
 * @param {number} index - The index of the project to navigate to.
 */
Cypress.Commands.add('navigateToProject', (index) => {
  cy.visit(`/`);
  cy.get('#projects-list-button').click({ force: true });
  cy.contains(`${project.name} ${index}`).click({ force: true });
});

/**
 * Hides the cookie banner and Django debug toolbar.
 *
 * @function hideCookieBannerAndDjango
 * @memberof Cypress.Commands
 */
Cypress.Commands.add('hideCookieBannerAndDjango', () => {
  cy.get('[data-test-id="fr-consent-banner"]')
    .find('[data-test-id="button-consent-accept-all"]')
    .click();
  cy.get('#djHideToolBarButton').click();
});

/**
 * Verifies that an image loads and that its alt attribute corresponds to its ARIA role.
 *
 * @function testImage
 * @memberof Cypress.Commands
 * @param {string} role - The ARIA role of the image. img-informative, img-presentation, or img-functional.
 * @param {string} type - The type of the image (e.g., 'svg', 'png', 'jpg', 'jpeg').
 */
Cypress.Commands.add(
  'testImage',
  { prevSubject: true },
  (subject, role, type) => {
    cy.wrap(subject).should(([img]) => {
      expect(img.alt).to.exist;
      expect(img.src).not.to.equal('');
      switch (role) {
        case 'img-presentation': {
          expect(img.alt).to.equal('');
          break;
        }
        case 'img-functional':
        case 'img-informative': {
          expect(img.alt).not.to.equal('');
          break;
        }
        default:
          assert(false);
          break;
      }
      switch (type) {
        case 'svg': {
          expect(img.width).to.be.greaterThan(0); // TODO: fix this test, as it will pass even if svg is not loaded
          expect(img.alt).to.equal('');
          break;
        }
        case 'png':
        case 'jpg':
        case 'jpeg': {
          // "naturalWidth" and "naturalHeight" are set when the image loads
          expect(img.naturalWidth).to.be.greaterThan(0);
          break;
        }
        default:
          assert(false);
          break;
      }
    });
  }
);

Cypress.Commands.add('clickRecaptcha', () => {
  cy.window().then((win) => {
    win.document
      .querySelector("iframe[src*='recaptcha']")
      .contentDocument.getElementById('recaptcha-token')
      .click();
    cy.wait(500);
  });
});
