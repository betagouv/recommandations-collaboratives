import api, { askRecommendationsUrl, corecommendationsUrl } from './api';
/**
 * Client for the external LLM API (Recoco ML service).
 *
 * Every option can be overridden through the `opts` parameter.
 */

/**
 * Asks the LLM a free-form question with an optional context.
 *
 * @param {string} query - The user's query.
 * @param {string} [context] - Additional context (e.g. a project description).
 * @param {object} [opts]
 * @param {number} [opts.projectId] - Id of the current project
 * @param {AbortSignal} [opts.signal] - To cancel the request.
 * @returns {Promise<{ answer_chunks: Array, citations: Array, found_answer: boolean }>}
 * @throws {Error}
 */
export async function askLLM(query, context = '', opts = {}) {
  if (!opts.projectId) throw new Error('Project Id required');

  const url = askRecommendationsUrl(opts.projectId);

  try {
    const response = await api.post(url, JSON.stringify({ query, context }));
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(
        `LLM API error (ask): ${error.response.status} ${error.response.statusText}`
      );
    } else if (error.request) {
      throw new Error('LLM API error (ask): aucune réponse du serveur');
    } else {
      throw new Error(`LLM API error (ask): ${error.message}`);
    }
  }
}

/**
 * Fetches the resources frequently co-recommended with a given set of
 * resources.
 *
 * @param {Array<number|string>} resourceIds - Identifiers of the source resources.
 * @param {object} [opts]
 * @param {number} [opts.projectId] - Id of the current project
 * @param {AbortSignal} [opts.signal]
 * @returns {Promise<Array<{ resource_id: number, co_occurrence_score: number }>>}
 * @throws {Error} If the request fails.
 */
export async function fetchCoRecommendations(resourceIds, opts = {}) {
  if (!opts.projectId) throw new Error('Project Id required');

  const params = new URLSearchParams();
  resourceIds.forEach((id) => params.append('resource_ids', id));

  const url = corecommendationsUrl(opts.projectId, params);
  try {
    const response = await api(url);
    return response.data.co_recommendations || response.data || [];
  } catch (error) {
    if (error.response) {
      throw new Error(
        `LLM API error (co-recommendations): ${error.response.status} ${error.response.statusText}`
      );
    } else if (error.request) {
      throw new Error(
        'LLM API error (co-recommendations): aucune réponse du serveur'
      );
    } else {
      throw new Error(`LLM API error (co-recommendations): ${error.message}`);
    }
  }
}
