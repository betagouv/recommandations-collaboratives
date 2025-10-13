import Alpine from 'alpinejs';
import api, { challengeUrl, challengeDefinitionUrl } from '../utils/api';

Alpine.data('ProjectPageTutorial', () => {
    return {
        challengesStatus: [],

        async init() {
            // await this.getChallenge(this.challengeCode);
            const challengesName = ['project-page-tutorial-part1', 'project-page-tutorial-part2', 'project-page-tutorial-part3', 'project-page-tutorial-part4'];
            const requests = [
              ...challengesName.map(name => api.get(challengeUrl(name)))
            ]
            const responses = await Promise.all(requests)
            console.log(responses)
        },
        // async getChallengeDefinition(code) {
        //     try {
        //       const json = await api.get(challengeDefinitionUrl(code));
        //       return json.data;
        //     } catch (err) {
        //       console.warn(err);
        //     }
        //   },
          async getChallenge(code) {
            try {
              const json = await api.get(challengeUrl(code));
              return json.data;
            } catch (err) {
              console.warn(err);
            }
          },

          test() {

          }
    };
});
