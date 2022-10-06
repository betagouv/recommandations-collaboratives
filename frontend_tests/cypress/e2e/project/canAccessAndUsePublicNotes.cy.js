describe('I can access and use privates notes', () => {

    beforeEach(() => {
        cy.login("switchtender");
    })

    it('goes to privates notes', () => {

        cy.visit('/projects')

        cy.contains('[Test] Frites & Friches 🍟').click({force:true});

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')

        const now = new Date();

        cy.get('textarea')
            .type(`test : ${now}`, { force: true })
            .should('have.value', `test : ${now}`)

        cy.contains("Envoyer").click({ force: true })

        cy.contains(`test : ${now}`)
    })
})
