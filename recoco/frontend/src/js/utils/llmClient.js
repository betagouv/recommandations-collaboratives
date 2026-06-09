import api, { askRecommendationsUrl, corecommendationsUrl } from './api';
/**
 * Client pour l'API LLM externe (service ML Recoco).
 *
 * Utilitaire pur, sans dépendance à Alpine, réutilisable depuis n'importe
 * quel composant, store, ou code hors Alpine.
 *
 * Toutes les options peuvent être surchargées via le paramètre `opts`.
 */

function buildUrl(baseUrl, params) {
  const base = (baseUrl || '').replace(/\/$/, '');
  const qs = params && params.toString() ? `?${params.toString()}` : '';
  return `${base}${qs}`;
}

/**
 * Pose une question libre à la LLM avec un contexte facultatif.
 *
 * @param {string} query - La requête de l'utilisateur.
 * @param {string} [context] - Contexte additionnel (ex: description d'un projet).
 * @param {object} [opts]
 * @param {number} [opts.projectId] - Id du projet courant
 * @param {AbortSignal} [opts.signal] - Pour annuler la requête.
 * @returns {Promise<{ answer_chunks: Array, citations: Array, found_answer: boolean }>}
 *   La réponse JSON brute de l'API.
 * @throws {Error} Si la requête échoue ou que la réponse n'est pas OK.
 */
export async function askLLM(query, context = '', opts = {}) {
  if (!opts.projectId) throw new Error('Project Id required');

  const url = askRecommendationsUrl(opts.projectId);

  try {
    const response = await api.post(url, {
      body: JSON.stringify({ query, context }),
    });
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
 * Récupère les ressources fréquemment co-recommandées avec un ensemble de
 * ressources données.
 *
 * @param {Array<number|string>} resourceIds - Identifiants des ressources sources.
 * @param {object} [opts]
 * @param {number} [opts.projectId] - Id du projet courant
 * @param {AbortSignal} [opts.signal]
 * @returns {Promise<Array<{ resource_id: number, co_occurrence_score: number }>>}
 *   La liste des co-recommandations (peut être emballée dans
 *   { co_recommendations: [...] } selon la version de l'API — on normalise).
 * @throws {Error} Si la requête échoue.
 */
export async function fetchCoRecommendations(resourceIds, opts = {}) {
  if (!opts.projectId) throw new Error('Project Id required');

  const params = new URLSearchParams();
  resourceIds.forEach((id) => params.append('resource_ids', id));

  const url = buildUrl(corecommendationsUrl(opts.projectId), params);
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
