import projects from '../../../../../fixtures/projects/projects.json'

const currentProject = projects[1];

describe('I can create a recommandation with no resource as a switcthender from the action view', () => {
    beforeEach(() => {
        cy.login("jean");
    })

    it('creates a reco from action view', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({ force: true });

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.contains("Ajouter une recommandation").click({ force: true })

        cy.get("#push-noresource").click({ force: true });


        cy.get('#intent')
            .type('reco test from action', { force: true })
            .should('have.value', 'reco test from action')

        cy.get('textarea')
            .type(`reco test from action description`, { force: true })
            .should('have.value', `reco test from action description`)

        cy.get("[type=submit]").click({ force: true });

        cy.url().should('include', '/actions')

        cy.contains('reco test from action')
    })
})
