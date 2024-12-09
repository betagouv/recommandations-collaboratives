describe.skip('As a visitor, I can access the menu and content on different devices', () => {
  const testLayouts = ['phone', 'tablet', 'desktop'];
  const breakpoint = 690;

  before(() => {
    cy.visit(`/`);
    cy.acceptCookies();
  });

  testLayouts.forEach((testItem) => {
    it(`displays correctly on a ${testItem}`, () => {
      cy.fixture('utils/devices').then((testDevices) => {
        const devices = testDevices.devices.filter(
          ({ layout }) => layout === testItem
        );
        const layouts = testDevices.layouts.find(
          ({ name }) => name === testItem
        );

        devices.forEach(({ dimensions }) => {
          const [width, height] = dimensions;
          let menuIsHidden = breakpoint > width;

          layouts.config.forEach((orientation) => {
            cy.visit(`/`);
            if (orientation === 'portrait') {
              cy.viewport(width, height);
            }
            if (orientation === 'landscape') {
              cy.viewport(height, width);
              menuIsHidden = breakpoint > height;
            }
            // Test here
            if (menuIsHidden) {
              cy.get('[data-test-id="secondary-menu"]').should(
                'not.be.visible'
              );
              // FIXME : this selector is no longer valid
              cy.get('[data-test-id="toggler-secondary-menu"]')
                .should('be.visible')
                .click();
              cy.get('[data-test-id="secondary-menu"]')
                .find('[data-test-id="link-ressources"]')
                .should('be.visible');
              // FIXME : this selector is no longer valid
              cy.get('[data-test-id="toggler-secondary-menu"]').click();
            } else {
              cy.get('[data-test-id="secondary-menu"]').should('be.visible');
              cy.get('[data-test-id="secondary-menu"]')
                .find('[data-test-id="link-ressources"]')
                .should('be.visible');
            }
          });
        });
      });
    });
  });
});
