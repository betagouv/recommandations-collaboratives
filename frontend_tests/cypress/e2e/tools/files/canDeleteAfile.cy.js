const now = new Date();

describe('I can delete a file on the conversation tab', () => {
    beforeEach(() => {
        cy.login("bob");
    })

    it('upload an image and check if it exists', () => {
        cy.visit('/')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')

        cy.document().then((doc) => {
            var popover = doc.getElementById('popover');
            popover.style = "display:block !important;"

            cy.get('[name="the_file"]').selectFile('cypress/fixtures/images/ui-screenshot.png', { force: true });

            cy.get('#file-description').type(`test : ${now.getTime()}`, { force: true }).should('have.value', `test : ${now.getTime()}`)
            cy.get('#file-submit').click({ force: true })

            cy.contains('Le fichier a bien été envoyé');

            cy.contains(`test : ${now.getTime()}`);
        })
    })

    it('delete the uploaded image', () => {
        cy.visit('/')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')

        cy.contains(`test : ${now.getTime()}`).parent().siblings().get('#form-delete-file').submit({force:true})

        cy.contains('Le fichier a bien été supprimé');

        cy.contains(`test : ${now.getTime()}`).should('not.exist')
    })
})
