import documents from '../../../fixtures/documents/documents.json'

describe('I can unbookmark a file already pinned', () => {
    beforeEach(() => {
        cy.login("bob");
    })

    it('shows the pinned file', () => {
        cy.visit('/')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.contains("Fichiers et liens").click({ force: true })

        cy.url().should('include', '/documents')

        //Unbookmark a file
        cy.contains(documents[1].fields.description).parent().parent().get("#file-is-bookmarked")
        cy.contains(documents[1].fields.description).parent().parent().get("#file-is-bookmarked").parent().parent().click({ force: true })

        cy.wait(500);
    })

    it('checks if the file is now correctly unbookmarked', () => {
        cy.visit('/')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.contains("Fichiers et liens").click({ force: true })

        cy.url().should('include', '/documents')

        cy.contains(documents[1].fields.description).parent().parent().get("#file-is-not-bookmarked")
    })
})
