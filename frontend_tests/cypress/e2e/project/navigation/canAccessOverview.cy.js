import projects from '../../../fixtures/projects/projects.json'
const currentProject = projects[1];

describe('I can access overview tab in a project as a member', () => {

    beforeEach(() => {
        cy.login("bob");
    })

    it('goes to knowledge page and then overview page of my project', () => {

        cy.visit(`/project/${currentProject.pk}`)
        cy.get('.project-navigation').children('li').contains('État des lieux').click({force:true})
        cy.url().should('include', '/connaissance')
        cy.contains('Présentation').click({force:true})
        cy.url().should('include', '/presentation')
    })
})

describe('I can access overview tab in a project as an advisor', () => {

    beforeEach(() => {
        cy.login("jean");
    })

    it('goes to knowledge page and then overview page of my project', () => {

        cy.visit(`/project/${currentProject.pk}`)
        cy.get('.project-navigation').children('li').contains('État des lieux').click({force:true})
        cy.url().should('include', '/connaissance')
        cy.contains('Présentation').click({force:true})
        cy.url().should('include', '/presentation')
    })
})
