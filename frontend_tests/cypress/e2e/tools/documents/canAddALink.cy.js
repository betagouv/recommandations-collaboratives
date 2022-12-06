import link from '../../../fixtures/documents/link.json'

describe('I can add a link on the document tab', () => {
    beforeEach(() => {
        cy.login("bob");
    })

    it('add a link', () => {
        cy.visit('/')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.contains("Fichiers et liens").click({ force: true })

        cy.url().should('include', '/documents')

        cy.document().then((doc) => {
            var popover = doc.getElementById('link-popover');
            popover.style = "display:block !important;"

            cy.get('[name="the_link"]').type(link.url, { force: true }).should('have.value', link.url);
            cy.get('#link-description').type(link.description, { force: true }).should('have.value', link.description)
            cy.get('#link-submit-button').click({ force: true })
        })
    })

    it('show the link in the link list', () => {

        cy.visit('/')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.contains("Fichiers et liens").click({ force: true })

        cy.url().should('include', '/documents')
        
        cy.contains(link.description);
    })
})
