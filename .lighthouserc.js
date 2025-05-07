module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:8000/'],
      startServerCommand: './manage.py runserver',
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
