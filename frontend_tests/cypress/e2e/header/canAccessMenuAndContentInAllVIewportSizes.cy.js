describe('As a visitor, I can access the menu and content on different devices', () => {
	const testLayouts = ['phone', 'tablet', 'desktop'];
	const breakpoint = 690

	before(() => {
		cy.visit(`/`);
		cy.get('[data-test-id="fr-consent-banner"]').find('[data-test-id="button-consent-decline-all"]').click()
	});

	testLayouts.forEach((testItem) => {

		it(`displays correctly on a ${testItem}`, () => {
			let devices = [];
			let layouts = [];
			cy.fixture('utils/devices').then((testDevices) => {
				devices = testDevices.devices.filter(({layout})=> layout === testItem);
				layouts = testDevices.layouts.find(({name})=> name === testItem);

				devices.forEach(({ dimensions }) => {
					const [width, height] = dimensions;
					let menuIsHidden = breakpoint > width;
	
					layouts.config.forEach((orientation) => {
						cy.visit(`/`);
						if(orientation === "portrait") {
							cy.viewport(width, height)
						}
						if(orientation === "landscape") {
							cy.viewport(height, width)
							menuIsHidden = breakpoint > height;
						}
						// Test here
						if(menuIsHidden) {
							cy.get('[data-test-id="secondary-menu"]').should('not.be.visible')
							cy.get('[data-test-id="toggler-secondary-menu"]').should('be.visible').click()
							cy.get('[data-test-id="secondary-menu"]').find('[data-test-id="link-ressources"]').should('be.visible')
							cy.get('[data-test-id="toggler-secondary-menu"]').click()
						} else {
							cy.get('[data-test-id="secondary-menu"]').should('be.visible')
							cy.get('[data-test-id="secondary-menu"]').find('[data-test-id="link-ressources"]').should('be.visible')
						}
					});
				});
			})
		});
  });
})