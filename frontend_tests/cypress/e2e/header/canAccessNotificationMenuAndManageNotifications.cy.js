describe('As a switchtender I can manage notifications in header', () => {
  before(() => {
    cy.login('bob');
    cy.visit('/project/2/conversations');

    for (let i = 0; i < 4; i++) {
      cy.get('[data-test-id="tiptap-editor-content"]').type('Hello World');
      cy.get('[data-test-id="send-message-conversation"]').click();
    }

    cy.logout();
  });

  afterEach(() => {
    cy.logout();
  });

  it('displays badge notification in the menu', () => {
    cy.login('jean');
    cy.visit('/');
    cy.get('[data-test-id="notification-badge"]').then((span) => {
      expect(+span.text()).be.greaterThan(0);
    });
  });

  it('displays a button to open and close notification menu', () => {
    cy.login('jean');
    cy.visit('/');
    cy.get('[data-test-id="notification-menu-open"]').click();
    cy.get('.dropdown-menu.notifications').should('be.visible');
    cy.get('[data-test-id="notification-menu-close"]').click();
    cy.get('.dropdown-menu.notifications').should('not.be.visible');
  });

  it('displays a button to mark notification as read one by one', () => {
    cy.login('jean');
    cy.visit('/');
    cy.get('[data-test-id="notification-badge"]').then((span) => {
      const notificationNumber = +span.text();
      expect(notificationNumber).be.greaterThan(0);
      cy.get('[data-test-id="notification-menu-open"]').click();
      for (let i = 0; i < notificationNumber - 2; i++) {
        cy.get('[data-test-id="notification-mark-as-read-one"]')
          .first()
          .click();
        cy.wait(400);
      }
      cy.get('[data-test-id="notification-badge"]').then((spanafter) => {
        const notificationNumberAfter = +spanafter.text();
        expect(notificationNumberAfter).be.equal(2);
      });
    });
  });

  it('displays a button to mark all notifications as read', () => {
    cy.login('jean');
    cy.visit('/');
    cy.get('[data-test-id="notification-badge"]').then((span) => {
      const notificationNumber = +span.text();
      expect(notificationNumber).be.greaterThan(0);
      cy.get('[data-test-id="notification-menu-open"]').click();
      cy.get('[data-test-id="notification-mark-all-as-read"]').click({
        force: true,
      });
      cy.wait(400);
      cy.get('[data-test-id="notification-mark-all-as-read"]').should(
        'be.disabled'
      );
      cy.get('[data-test-id="notification-badge"]').should('not.be.visible');
    });
  });
});
