const { resolve } = require('path');

module.exports = {
    plugins: [],
    root: resolve('./src'),
    base: '/static/',
    server: {
        host: 'localhost',
        port: 3000,
        open: false,
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
        target: 'es2017',
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
                projectDetails : resolve('./src/js/apps/projectDetails.js'),
                projectShare : resolve('./src/js/apps/projectShare.js'),
                projectAdministration : resolve('./src/js/apps/projectAdministration.js'),
                map: resolve('./src/js/apps/map.js'),
                documents: resolve('./src/js/apps/documents.js'),
                searchableList: resolve('./src/js/apps/searchableList.js'),
                consent: resolve('./src/js/apps/consent.js'),
                tagCloud: resolve('./src/js/apps/tagCloud.js'),
                organizationSearch: resolve('./src/js/apps/organizationSearch.js')
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
