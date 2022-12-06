import documents from '../../../fixtures/documents/documents.json'

describe('I can unbookmark a file already pinned', () => {
    beforeEach(() => {
        cy.login("bob");
    })

    it('shows the unpinned file', () => {
        cy.visit('/')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.contains("Fichiers et liens").click({ force: true })

        cy.url().should('include', '/documents')

        //Unbookmark a file
        cy.contains(documents[2].fields.description).parent().parent().get("#file-is-not-bookmarked")
        cy.contains(documents[2].fields.description).parent().parent().get("#file-is-not-bookmarked").parent().parent().click({ force: true })

        cy.wait(500);
    })

    it('checks if the file is now correctly bookmarked', () => {
        cy.visit('/')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.contains("Fichiers et liens").click({ force: true })

        cy.url().should('include', '/documents')

        cy.contains(documents[2].fields.description).parent().parent().get("#file-is-bookmarked")
    })
})
