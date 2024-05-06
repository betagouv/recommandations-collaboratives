describe('As a visitor to a recoco site, I can find a way to contact the site team', () => {

	beforeEach(() => {
		cy.visit(`/`)
	})

	it('Displays a contact form or a contact email', () => {
			cy.visit(`/contact`)

			cy.get('[data-test-id="contact-form-name"]').type("Cecile Ménard",{force:true})
			cy.get('[data-test-id="contact-form-email"]').type("cecile@example.com",{force:true})
			cy.get('[data-test-id="contact-form-subject"]').type("Premier contact",{force:true})
			cy.get('[data-test-id="contact-form-message"]').type("Bonjour, Ma commune a une friche qu'on souhaite réhabiliter. Comment faire ?",{force:true})

			cy.document().then((doc) => {
				var iframe = doc.getElementById('id_captcha').querySelector('iframe');
				var innerDoc = iframe.contentDocument || iframe.contentWindow.document;
				innerDoc.querySelector('.recaptcha-checkbox').click()
			})

			cy.wait(500)

			cy.get('[data-test-id="contact-form-submit"]').click({force:true})

			cy.contains(`Merci, votre demande a été transmis à l'équipe`)
	})
})
