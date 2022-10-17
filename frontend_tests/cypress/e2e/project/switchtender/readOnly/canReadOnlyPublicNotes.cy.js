describe('I can read only public notes', () => {

    beforeEach(() => {
        cy.login("switchtender2");
    })

    it('goes to public notes and read only content', () => {

        cy.visit('/projects')

        cy.contains('Friche numéro 1').click({force:true});

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')

        cy.contains("Envoyer").should('not.exist')
    })
})
