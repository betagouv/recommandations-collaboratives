describe('I can see the resource contact list if im logged', () => {
    beforeEach(() => {
        cy.login("bob");
    })

    it('see the contact list', () => {
        cy.visit('/ressource/3/')

        cy.contains("Lala")
        cy.contains("Lili")
        cy.contains("Lulu")
    })
})

describe("I can't see the resource contact list if im not logged", () => {
    beforeEach(() => {
    })

    it('cannot see a contact list', () => {
        cy.visit('/ressource/3/')
        cy.contains("contacts associés à cette ressource. Si vous souhaitez y accéder, veuillez vous identifier.");
    })
})
