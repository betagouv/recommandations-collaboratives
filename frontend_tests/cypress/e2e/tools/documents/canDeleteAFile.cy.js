import documents from '../../../fixtures/documents/documents.json'

describe('I can delete a file on the document tab', () => {
    beforeEach(() => {
        cy.login("bob");
    })

    it('deletes a file', () => {
        cy.visit('/')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.contains("Fichiers et liens").click({ force: true })

        cy.url().should('include', '/documents')

        cy.contains(documents[3].fields.description).parent().siblings().children().find("#file-delete-button").click({ force: true });

        cy.contains('Le document a bien été supprimé');
    })

    it('must not show the deleted link', () => {
        cy.visit('/')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.contains("Fichiers et liens").click({ force: true })

        cy.url().should('include', '/documents')

        cy.contains(documents[3].fields.description).should('not.exist');
    })
})
