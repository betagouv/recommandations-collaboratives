import { resolve } from 'path';

const config = {
  plugins: [],
  root: resolve('./src'),
  base: '/static/',
  server: {
    origin: 'http://localhost:3000',
    host: '0.0.0.0',
    port: 3000,
    open: false,
    cors: true,
    watch: {
      usePolling: true,
      disableGlobbing: false,
    },
  },
  resolve: {
    extensions: ['.js', '.json'],
  },
  build: {
    outDir: resolve('./dist'),
    assetsDir: '',
    manifest: 'manifest.json',
    emptyOutDir: true,
    target: 'es2020',
    rollupOptions: {
      input: {
        main: resolve('./src/js/main.js'),
        onboarding: resolve('./src/js/apps/onboarding.js'),
        advisorCreateProject: resolve('./src/js/apps/advisorCreateProject.js'),
        home: resolve('./src/js/apps/home.js'),
        crm: resolve('./src/js/apps/crm.js'),
        project: resolve('./src/js/apps/project.js'),
        boardProjects: resolve('./src/js/apps/boardProjects.js'),
        tasks: resolve('./src/js/apps/tasks.js'),
        embedResource: resolve('./src/js/apps/embedResource.js'),
        advisorDashboard: resolve('./src/js/apps/advisorDashboard.js'),
        auth: resolve('./src/js/apps/auth.js'),
        projectDetails: resolve('./src/js/apps/projectDetails.js'),
        projectShare: resolve('./src/js/apps/projectShare.js'),
        projectAdministration: resolve(
          './src/js/apps/projectAdministration.js'
        ),
        documents: resolve('./src/js/apps/documents.js'),
        searchableList: resolve('./src/js/apps/searchableList.js'),
        consent: resolve('./src/js/apps/consent.js'),
        tagCloud: resolve('./src/js/apps/tagCloud.js'),
        organizationSearch: resolve('./src/js/apps/organizationSearch.js'),
        topicSearch: resolve('./src/js/apps/topicSearch.js'),
        user: resolve('./src/js/apps/user.js'),
        tutorial: resolve('./src/js/apps/tutorial.js'),
        contactApp: resolve('./src/js/apps/contactApp.js'),
        mapViewerStatic: resolve('./src/js/apps/mapViewerStatic.js'),
        mapViewerInteractive: resolve('./src/js/apps/mapViewerInteractive.js'),
        projectEmailReminder: resolve('./src/js/apps/projectEmailReminder.js'),
        mapEditor: resolve('./src/js/apps/mapEditor.js'),
        menuTop: resolve('./src/js/apps/menuTop.js'),
        actionsEmbed: resolve('./src/js/apps/actionsEmbed.js'),
        tasksEmbed: resolve('./src/js/apps/tasksEmbed.js'),
        projectKnowledge: resolve('./src/js/apps/projectKnowledge.js'),
        selectSearchable: resolve('./src/js/apps/selectSearchable.js'),
        ExpandableMenuHandler: resolve(
          './src/js/components/ExpandableMenuHandler.js'
        ),
        projectQueue: resolve('./src/js/store/projectQueue.js'),
        showRole: resolve('./src/js/store/showRole.js'),
        projects: resolve('./src/js/store/projects.js'),
        tutorialsEvents: resolve('./src/js/store/tutorialsEvents.js'),
        ClickToSeeUser: resolve('./src/js/components/ClickToSeeUser.js'),
        ActionPusher: resolve('./src/js/components/ActionPusher.js'),
        NotificationEater: resolve('./src/js/components/NotificationEater.js'),
        actionPusherStore: resolve('./src/js/store/actionPusher.js'),
        conversationsNew: resolve('./src/js/apps/conversationsNew.js'),
        featureAddContact: resolve('./src/js/apps/featureAddContact.js'),
        DepartmentsSelector: resolve(
          './src/js/components/DepartmentsSelector.js'
        ),
        RegionDepartmentPreparer: resolve(
          './src/js/components/RegionDepartmentPreparer.js'
        ),
        User: resolve('./src/js/components/User.js'),
        MultiSelectRegionDepartment: resolve(
          './src/js/components/MultiSelectRegionDepartment.js'
        ),
        MultiSelect2: resolve('./src/js/components/MultiSelect2.js'),
        ContactBook: resolve('./src/js/components/ContactBook.js'),
        ProjectPageTutorial: resolve(
          './src/js/components/onboarding-tutorials/ProjectPageTutorial.js'
        ),
        pageInvitation: resolve('./src/js/apps/pageInvitation.js'),
        idbObjectStoreMgmt: resolve('./src/js/store/idbObjectStoreMgmt.js'),
        actionPusher: resolve('./src/js/apps/actionPusher.js'),
        NewFeatureBanner: resolve('./src/js/components/NewFeatureBanner.js'),
        contactBookApp: resolve('./src/js/apps/contactBookApp.js'),
        ResourceCategoryFilter: resolve('./src/js/components/ResourceCategoryFilter.js'),
        departmentsSelector: resolve(
          './src/js/styles/departments-selector.css.js'
        ),
        surveyGridStyles: resolve('./src/js/styles/survey-grid.css.js'),
        personnalDashboardStyles: resolve(
          './src/js/styles/personnal-dashboard.css.js'
        ),
        tasksModalStyles: resolve('./src/js/styles/tasks-modal.css.js'),
        switchtenderListStyles: resolve(
          './src/js/styles/switchtender-list.css.js'
        ),
        projectBannerStyles: resolve('./src/js/styles/project-banner.css.js'),
        inviteNotAcceptedBannerStyles: resolve(
          './src/js/styles/invite-not-accepted-banner.css.js'
        ),
        homeStyles: resolve('./src/js/styles/home.css.js'),
        kanbanStyles: resolve('./src/js/styles/kanban.css.js'),
        baseStyles: resolve('./src/js/styles/base.css.js'),
        markdownxStyles: resolve('./src/js/styles/markdownx.css.js'),
        consentBannerStyles: resolve('./src/js/styles/consent-banner.css.js'),
        menuTopStyles: resolve('./src/js/styles/menu-top.css.js'),
        headerUserToolsStyles: resolve(
          './src/js/styles/header-user-tools.css.js'
        ),
        headerMenuBurgerStyles: resolve(
          './src/js/styles/header-menu-burger.css.js'
        ),
        accountLoginStyles: resolve('./src/js/styles/account-login.css.js'),
        accountLayoutFormStyles: resolve(
          './src/js/styles/account-layout-form.css.js'
        ),
        toolsEditorStyles: resolve('./src/js/styles/tools-editor.css.js'),
        contactCardStyles: resolve('./src/js/styles/contact-card.css.js'),
        contactMultiSelectStyles: resolve(
          './src/js/styles/contact-multi-select.css.js'
        ),
        contactSearchOrganizationStyles: resolve(
          './src/js/styles/contact-search-organization.css.js'
        ),
        contactSearchContactModalStyles: resolve(
          './src/js/styles/contact-search-contact-modal.css.js'
        ),
        contactCreateOrganizationModalStyles: resolve(
          './src/js/styles/contact-create-organization-modal.css.js'
        ),
        contactCreateContactModalStyles: resolve(
          './src/js/styles/contact-create-contact-modal.css.js'
        ),
        homeAuthStyles: resolve('./src/js/styles/home-auth.css.js'),
        homePrivacyStyles: resolve('./src/js/styles/home-privacy.css.js'),
        homeActorsStyles: resolve('./src/js/styles/home-actors.css.js'),
        homeCmsPageTextStyles: resolve(
          './src/js/styles/home-cms-page-text.css.js'
        ),
        homeCmsPageShowcaseStyles: resolve(
          './src/js/styles/home-cms-page-showcase.css.js'
        ),
        onboardingPrefillUserStyles: resolve(
          './src/js/styles/onboarding-prefill-user.css.js'
        ),
        pagesShowcaseListStyles: resolve(
          './src/js/styles/pages-showcase-list.css.js'
        ),
        projectsBoardStyles: resolve('./src/js/styles/projects-board.css.js'),
        projectsProjectStyles: resolve(
          './src/js/styles/projects-project.css.js'
        ),
        projectsOverviewStyles: resolve(
          './src/js/styles/projects-overview.css.js'
        ),
        projectsProjectNavigationStyles: resolve(
          './src/js/styles/projects-project-navigation.css.js'
        ),
        projectsProjectModerationStyles: resolve(
          './src/js/styles/projects-project-moderation.css.js'
        ),
        projectsConversationsNewStyles: resolve(
          './src/js/styles/projects-conversations-new.css.js'
        ),
        projectsAdministrationStyles: resolve(
          './src/js/styles/projects-administration.css.js'
        ),
        projectsPushStyles: resolve('./src/js/styles/projects-push.css.js'),
        projectsSearchbarStyles: resolve(
          './src/js/styles/projects-searchbar.css.js'
        ),
        projectsFileUploadStyles: resolve(
          './src/js/styles/projects-file-upload.css.js'
        ),
        projectsActionListStyles: resolve(
          './src/js/styles/projects-action-list.css.js'
        ),
        projectsCardInfoStyles: resolve(
          './src/js/styles/projects-card-info.css.js'
        ),
        projectsKanbanProjectStyles: resolve(
          './src/js/styles/projects-kanban-project.css.js'
        ),
        resourcesStyles: resolve('./src/js/styles/resources.css.js'),
        resourceCardStyles: resolve('./src/js/styles/resource-card.css.js'),
        surveyStyles: resolve('./src/js/styles/survey.css.js'),
        segmentedCtrlStyles: resolve('./src/js/styles/segmented_ctrl.css.js'),
        projectListCrm: resolve('./src/js/apps/CRM/projectListCrm.js'),
        crmNavigation: resolve('./src/js/apps/CRM/crmNavigation.js'),
        multiSelectStyles: resolve('./src/js/styles/multi-select.css.js'),
        projectsOnboardingTutorialStyles: resolve(
          './src/js/styles/projects-onboarding-tutorial.css.js'
        ),
        marianneStyles: resolve('./src/js/styles/marianne.css.js'),
        formResourcesStyles: resolve(
          './src/js/styles/form-resources.css.js'
        ),
        formResource: resolve('./src/js/components/Resources/FormResource.js'),
        ajvValidationSchema: resolve(
          './src/js/components/AjvValidationSchema.js'
        ),
        projectDetailsStyles: resolve('./src/js/styles/project-details.css.js'),
        resourceListCrm: resolve('./src/js/apps/CRM/resourceListCrm.js'),
      },
      output: {
        chunkFileNames: undefined,
      },
    },
  },
  test: {
    globals: true,
  },
};

export default config;
