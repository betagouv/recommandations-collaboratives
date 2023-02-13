import file from '../../../fixtures/documents/file.json'

describe('I can add a file with my message in public notes', () => {
    beforeEach(() => {
        cy.login("bob");
    })

    it('writes a message with a file', () => {
        cy.visit('/')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')

        const now = new Date();

        cy.get('textarea')
            .type(`test avec fichier : ${now}`, { force: true })
            .should('have.value', `test avec fichier : ${now}`)

        cy.get('[name="the_file"]').selectFile(file.path, { force: true });

        cy.contains("Envoyer").click({ force: true })

        cy.contains(`test avec fichier : ${now}`)
        cy.contains(file.path.slice(-17,-4))
    })
})
