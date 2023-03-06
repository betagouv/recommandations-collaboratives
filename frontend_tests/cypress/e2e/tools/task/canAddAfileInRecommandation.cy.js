import file from '../../../fixtures/documents/file.json'
import projects from '../../../fixtures/projects/projects.json'

const currentProject = projects[2];

describe('I can add a file in a recommandation', () => {
    beforeEach(() => {
        cy.login("jeannot");
    })

    it('writes a message with a file', () => {
        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({force:true});

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.contains("Ajouter une recommandation").click({ force: true })

        cy.get("#push-noresource").click({ force: true });

        const now = new Date();

        cy.get('#intent')
            .type('fake recommandation with no resource', { force: true })
            .should('have.value', 'fake recommandation with no resource')

        cy.get('textarea')
            .type(`fake recommandation content with no resource : ${now}`, { force: true })
            .should('have.value', `fake recommandation content with no resource : ${now}`)

        cy.get('[name="the_file"]').selectFile(file.path, { force: true });

        cy.get("[type=submit]").click({ force: true });

        cy.url().should('include', '/actions')

        cy.contains(`fake recommandation content with no resource : ${now}`)
    })
})
