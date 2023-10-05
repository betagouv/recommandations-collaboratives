const currentTask = {
    name: "Tache 1",
    topic: "Topic 1"
}

describe('I can go to tasks tab', () => {
    beforeEach(() => {
        cy.login("jean");
    })

    it('changes the status to done', () => {
        cy.createProject("topic project")
        cy.becomeAdvisor();
        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')
        cy.createTask(currentTask.name, currentTask.topic);
        cy.contains(currentTask.topic)
    })
})
