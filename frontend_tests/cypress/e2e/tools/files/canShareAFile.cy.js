describe('I can share a file on the conversation tab', () => {
    beforeEach(() => {
        cy.login("bob");
    })

    it('upload an image and check if it exists', () => {
        cy.visit('/')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')

        // cy.get('#add-file-button').trigger("click",{force:true})

        cy.document().then((doc) => {
            var popover = doc.getElementById('popover');
            popover.style = "display:block !important;"

            cy.get('[name="the_file"]').selectFile('cypress/fixtures/images/ui-screenshot.png', { force: true });
            cy.get('#file-description').type('fichier de test', { force: true }).should('have.value', `fichier de test`)
            cy.get('#file-submit').click({ force: true })

            cy.contains('Le fichier a bien été envoyé');
            cy.contains('fichier de test');

        })
    })
})
