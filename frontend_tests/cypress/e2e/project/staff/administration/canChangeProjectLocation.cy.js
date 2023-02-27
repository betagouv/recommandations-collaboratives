import projects from '../../../../fixtures/projects/projects.json'
import commune from '../../../../fixtures/geomatics/commune.json'

const currentCommune = commune[1]

const currentProject = projects[1];

describe('I can go to administration area of a project and change the project location', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('goes to the administration tab of a project and change the project location', () => {

        cy.visit(`/project/${currentProject.pk}`)
        cy.get('.project-navigation').children('li').contains('Administration').click({ force: true })
        cy.url().should('include', '/administration')

        cy.get('#input-project-address')
            .clear({ force: true })
            .type(`${currentProject.fields.location} updated`, { force: true })
            .should('have.value', `${currentProject.fields.location} updated`)

        cy.get('[name=postcode]')
            .clear({ force: true })
            .type(currentCommune.fields.insee, { force: true })
            .should('have.value', currentCommune.fields.insee)

        cy.get('#id_name')
            .clear({ force: true })
            .type(`${currentProject.fields.name} updated`, { force: true })
            .should('have.value', `${currentProject.fields.name} updated`)


        cy.contains('Modifier les informations du projet').click({ force: true });

        cy.url().should('include', '/presentation')

        cy.contains(`${currentCommune.fields.insee}`);
        cy.contains(`${currentCommune.fields.name}`);
    })
})
