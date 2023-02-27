describe('I can ask a question on a resource', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('asks a question', () => {
        cy.visit('/ressource/3/')

        cy.contains("Poser une question").click({ force: true })
        cy.url().should('include', '/contact/')
        cy.contains(" Contacter l'équipe UrbanVitaliz")

        cy.get('#input-project-content')
            .type('Question sur la resource numéro 3', { force: true })
            .should('have.value', 'Question sur la resource numéro 3')

        cy.document().then((doc) => {
            var iframe = doc.getElementById('id_captcha').querySelector('iframe');
            var innerDoc = iframe.contentDocument || iframe.contentWindow.document;
            innerDoc.querySelector('.recaptcha-checkbox').click()
        })

        cy.wait(500)

        cy.contains('Envoyer mon message').click({ force: true });
        cy.url().should('include', '/ressource/3/')
    })
})
