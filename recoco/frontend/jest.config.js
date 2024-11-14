const config = {
  verbose: true,
  // this is very important to get right, you must add all the node_modules dependencies in one entry, seperated by a |
  // this is because the way this works is to ignore everything in node_modules, except for the stuff behind ?! . If we add
  // a second entry to the transformIgnorePatterns array without excluding the first ignorePattern in that second entry, we
  // are essentially saying, ['ignore all node_modules except swiper', 'ignore all node_modules except whatever whatever is here*']

  // * which also means ignore what was in the first one (and vice versa)

  // transformIgnorePatterns: ['/node_modules/(?!swiper|ssr-window|dom7)'],
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.(ts|tsx|js)$': 'babel-jest', // this is probably something you already had, if using ts-jest, it's probably fine to leave as ts-jest
    '^.+\\.(css)$': '<rootDir>/config/jest/fileTransform.js', // add this to fix css import issues
  },
};

module.exports = config;
