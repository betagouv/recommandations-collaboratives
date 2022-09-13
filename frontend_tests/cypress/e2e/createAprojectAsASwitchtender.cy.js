describe('I can create a project as a switchtender', () => {
    it('finds the content "type"', () => {
        cy.visit('/')
        cy.contains('Se connecter').click({ force: true });

        cy.url().should('include', '/accounts/login/')

        cy.get('#id_login')
            .type('switchtender@email.com', { force: true })
            .should('have.value', 'switchtender@email.com')

        cy.get('#id_password')
            .type('derpderp', { force: true })
            .should('have.value', 'derpderp')

        cy.get("[type=submit]").click({ force: true });

        cy.contains("Connexion avec switchtender réussie.")

        cy.contains("Ajouter un projet").click({ force: true })

        cy.url().should('include', '/projects/prefill/')

        cy.get('#id_first_name')
            .type('fakefirstname', { force: true })
            .should('have.value', 'fakefirstname')

        cy.get('#id_last_name')
            .type('fakelastname', { force: true })
            .should('have.value', 'fakelastname')

        cy.get('#id_email')
            .type('fake@email.com', { force: true })
            .should('have.value', 'fake@email.com')

        cy.get('#id_phone')
            .type('010101010101', { force: true })
            .should('have.value', '010101010101')

        cy.get('#id_org_name')
            .type('fake structure', { force: true })
            .should('have.value', 'fake structure')

        cy.get('#id_name')
            .type('fake project name', { force: true })
            .should('have.value', 'fake project name')

        cy.get('#input-project-address')
            .type('143 rue fake', { force: true })
            .should('have.value', '143 rue fake')

        cy.get('[name=postcode]')
            .type('30130', { force: true })
            .should('have.value', '30130')

        cy.get('#input-project-description')
            .type('Fake project description', { force: true })
            .should('have.value', 'Fake project description')

        cy.get('#id_response_1')
            .type('Fake project description precision', { force: true })
            .should('have.value', 'Fake project description precision')

        cy.get('#id_response_2_0')
            .check({ force: true })

        cy.contains("Ajouter ce projet et rejoindre l'équipe de suivi").click({ force: true });

        cy.url().should('include', '/project/')
        cy.url().should('include', '/connaissance')
        cy.contains("Fake Project Name")
        cy.contains("Présentation").click({force:true});

        cy.url().should('include', '/project/')
        cy.url().should('include', '/presentation')

        //Checking Contexte & Compléments
        cy.contains("Contexte")
        cy.contains("Fake project description")

        cy.contains("Pourquoi nous sollicitez-vous ?")
        cy.contains("Fake project description precision")

        cy.contains("Cartofriche")
        cy.contains("Ce projet peut être versé sur cartofriche")

        cy.contains("Conversation").click({force:true});

        cy.url().should('include', '/project/')
        cy.url().should('include', '/conversations')

        //Checking demande initiale
        cy.contains("Demande initiale")
        cy.contains("Fake project description")

        cy.contains("Pourquoi nous sollicitez-vous ?")
        cy.contains("Fake project description precision")

        cy.contains("Cartofriche")
        cy.contains("Ce projet peut être versé sur cartofriche")


    })

})
