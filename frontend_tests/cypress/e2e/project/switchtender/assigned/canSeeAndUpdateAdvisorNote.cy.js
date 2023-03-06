import projects from '../../../../fixtures/projects/projects.json'
const currentProject = projects[1];

describe('I can see and update an advisor note', () => {

    beforeEach(() => {
        cy.login("jeanne");
    })

    it('goes to project overview and update advisor note', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({force:true});

        cy.contains("Note interne")

        cy.contains('Non visible par la collectivité').parent().siblings('a').click({force:true})

        const now = new Date();

        cy.get('textarea').clear({ force: true })

        cy.get('textarea')
            .type(`test : ${now}`)
            .should('have.value', `test : ${now}`)

        cy.contains("Enregistrer").click({ force: true })

        cy.contains(`test : ${now}`)
    })
})
