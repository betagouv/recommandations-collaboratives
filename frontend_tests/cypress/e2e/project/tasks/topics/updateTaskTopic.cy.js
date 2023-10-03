const currentTask = {
    name: "Tache 1",
    topic: "Topic 1"
}

const topicUpdated = "Topic updated"

describe('I can go to tasks tab', () => {
    beforeEach(() => {
        cy.login("jean");
    })

    it('changes the status to done', () => {
        cy.createProject("topic project 2")
        cy.becomeAdvisor();
        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')
        cy.createTask(currentTask.name, currentTask.topic);
        cy.contains(currentTask.topic)
        cy.get('[data-test-id="open-task-actions-button"]').click({ force: true })
        cy.get('[data-test-id="update-task-action-button"]').click({ force: true })
        cy.get('#topic_name')
            .clear({ force: true })
            .type(`${topicUpdated}`, { force: true })
            .should('have.value', `${topicUpdated}`)

        cy.get('[data-test-id="publish-task-button"]').click({ force: true });
        cy.contains(topicUpdated)
    })
})
