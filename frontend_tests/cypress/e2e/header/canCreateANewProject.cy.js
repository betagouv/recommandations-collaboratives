describe('I can create a new project from the main header project list dropdown as a collectivity', () => {

    beforeEach(() => {
        cy.login("bob");
    })

    it('', () => {

        cy.visit(`/`)
        cy.contains('Mes projets').siblings('button').click();
        cy.contains('Créer un nouveau projet').click({force:true})
        cy.url().should('include', '/onboarding')
    })
})

describe("I can't see create a new project from the main header project list dropdown as an advisor", () => {

    beforeEach(() => {
        cy.login("jean");
    })

    it('', () => {

        cy.visit(`/`)
        cy.contains('Mes projets').should('not.exist')
    })
})
