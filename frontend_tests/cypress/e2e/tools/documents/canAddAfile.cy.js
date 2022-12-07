import file from '../../../fixtures/documents/file.json'

describe('I can add a file on the document tab', () => {
    beforeEach(() => {
        cy.login("bob");
    })

    it('upload a file', () => {
        cy.visit('/')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.contains("Fichiers et liens").click({ force: true })

        cy.url().should('include', '/documents')

        cy.document().then((doc) => {
            var popover = doc.getElementById('popover');
            popover.style = "display:block !important;"

            cy.get('[name="the_file"]').selectFile(file.path, { force: true });
            cy.get('#document-description').type(file.description, { force: true }).should('have.value', file.description)
            cy.get('#document-submit-button').click({ force: true })
        })

        cy.contains('Le document a bien été enregistré');
    })

    it('show the file in the file list', () => {

        cy.visit('/')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.contains("Fichiers et liens").click({ force: true })

        cy.url().should('include', '/documents')

        cy.contains(file.description);
    })
})
