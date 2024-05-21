import users from '../fixtures/users/users.json';
import project from '../fixtures/projects/project.json';
import resources from '../fixtures/resources/resources.json';
import communes from '../fixtures/geomatics/commune.json';
const currentResource = resources[4];
const projectCommune = communes.find(
  (c) => c.fields.postal == project.postcode
);

Cypress.Commands.add('login', (role) => {
  let username = '';

  switch (role) {
    case 'jean':
      username = users[1].fields.username;
      break;
    case 'jeanne':
      username = users[2].fields.username;
      break;
    case 'jeannot':
      username = users[3].fields.username;
      break;
    case 'bob':
      username = users[4].fields.username;
      break;
    case 'boba':
      username = users[5].fields.username;
      break;
    case 'bobette':
      username = users[6].fields.username;
      break;
    case 'staff':
      username = users[0].fields.username;
      break;
    case 'nonactive':
      username = users[8].fields.username;
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

Cypress.Commands.add('loginWithUi', (role) => {
  const { username } = currentUser;
  cy.visit('/accounts/login/');

  cy.url().should('include', '/accounts/login/');

  cy.get('#id_login')
    .type(username, { force: true })
    .should('have.value', username);

  cy.get('#id_password')
    .type('derpderp', { force: true })
    .should('have.value', 'derpderp');

  cy.get('[type=submit]').click({ force: true });
  cy.visit('/');

  cy.contains(`Connexion avec ${username} réussie.`);

  // // we should be redirected to /dashboard
  cy.url().should('include', '/projects');

  // // our auth cookie should be present
  cy.getCookie('sessionid').should('exist');

  cy.acceptCookies();
});

Cypress.Commands.add('logout', () => {
  cy.get('#user-menu-button').click({ force: true });
  cy.contains('Déconnexion').click({ force: true });
});

/**
 * Consent to cookies banner
 */
Cypress.Commands.add('acceptCookies', () => {
  cy.get('[data-test-id="fr-consent-banner"]')
    .find('[data-test-id="button-consent-accept-all"]')
    .click({ force: true });
  cy.visit('/');
});

/**
 * Decline cookies banner
 */
Cypress.Commands.add('declineCookies', () => {
  cy.get('[data-test-id="fr-consent-banner"]')
    .find('[data-test-id="button-consent-decline-all"]')
    .click({ force: true });
  cy.visit('/');
});

Cypress.Commands.add('createProject', (label) => {
  cy.visit('/');

  cy.get('[data-test-id="button-need-help"]')
    .contains('Solliciter')
    .click({ force: true });

  cy.url().should('include', '/onboarding/project');

  cy.get('#id_name')
    .should('not.have.class', 'fr-input--error')
    .type(label || project.name)
    .should('have.value', label || project.name)
    .should('have.class', 'fr-input--valid');

  cy.get('#id_location')
    .should('not.have.class', 'fr-input--error')
    .type(project.location)
    .should('have.value', project.location)
    .should('have.class', 'fr-input--valid');

  cy.get('[data-test-id="input-postcode"]')
    .parent()
    .should('not.have.class', 'fr-input-group--error');

  cy.get('[data-test-id="input-postcode"]')
    .type(project.postcode)
    .should('have.value', project.postcode)
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
    .type(project.description)
    .should('have.value', project.description)
    .should('have.class', 'fr-input--valid');

  cy.get('button[type="submit"]').click();

  cy.url().should('include', '/onboarding/summary');
});

Cypress.Commands.add('becomeAdvisor', () => {
  cy.get('body').then((body) => {
    if (body.find('#positioning-form').length > 0) {
      cy.get('[data-test-id="button-join-as-advisor"]').click({
        force: true,
      });
    } else {
      assert.isOk('advisor', 'already advisor');
    }
  });
});

Cypress.Commands.add(
  'createTask',
  (label, topic = '', withResource = false) => {
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

        cy.get('[type=submit]').click({ force: true });

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

        cy.get('[type=submit]').click({ force: true });

        cy.url().should('include', '/actions');

        cy.contains('reco test from action');
      } else {
        assert.isOk('task', "can't create task");
      }
    });
  }
);

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

Cypress.Commands.add('navigateToProject', (index) => {
  cy.visit(`/`);
  cy.get('#projects-list-button').click({ force: true });
  cy.contains(`${project.name} ${index}`).click({ force: true });
});

Cypress.Commands.add('hideCookieBannerAndDjango', () => {
  cy.get('[data-test-id="fr-consent-banner"]')
    .find('[data-test-id="button-consent-accept-all"]')
    .click();
  cy.get('#djHideToolBarButton').click();
});

/**
 * Verify that image loads and that alt attribute corresponds to ARIA role.
 * Possible role values are:
 * - img-informative
 * - img-presentation
 * - img-functional
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
