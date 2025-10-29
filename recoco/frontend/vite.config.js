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
    manifest: true,
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
        map: resolve('./src/js/apps/map.js'),
        documents: resolve('./src/js/apps/documents.js'),
        searchableList: resolve('./src/js/apps/searchableList.js'),
        consent: resolve('./src/js/apps/consent.js'),
        tagCloud: resolve('./src/js/apps/tagCloud.js'),
        organizationSearch: resolve('./src/js/apps/organizationSearch.js'),
        topicSearch: resolve('./src/js/apps/topicSearch.js'),
        user: resolve('./src/js/apps/user.js'),
        tutorial: resolve('./src/js/apps/tutorial.js'),
        contactApp: resolve('./src/js/apps/contactApp.js'),
        projectDetailsCss: resolve('./src/css/projectDetails.css'),
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
        actionPusher: resolve('./src/js/store/actionPusher.js'),
        conversationsNew: resolve('./src/js/apps/conversationsNew.js'),
        featureAddContact: resolve('./src/js/apps/featureAddContact.js'),
        DepartmentsSelector: resolve(
          './src/js/components/DepartmentsSelector.js'
        ),
        RegionDepartmentPreparer: resolve(
          './src/js/components/RegionDepartmentPreparer.js'
        ),
        User: resolve('./src/js/components/User.js'),
        MutliSelect: resolve('./src/js/components/MultiSelect.js'),
        ContactBook: resolve('./src/js/components/ContactBook.js'),
        projectPageTutorial: resolve('./src/js/components/onboarding-tutorials/ProjectPageTutorial.js'),
        pageInvitation: resolve('./src/js/apps/pageInvitation.js'),
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
