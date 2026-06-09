import { askRecommendationsUrl, corecommendationsUrl } from './api';
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
 * @param {number} [opts.CSRFToken] - Jeton CSRF
 * @param {AbortSignal} [opts.signal] - Pour annuler la requête.
 * @returns {Promise<{ answer_chunks: Array, citations: Array, found_answer: boolean }>}
 *   La réponse JSON brute de l'API.
 * @throws {Error} Si la requête échoue ou que la réponse n'est pas OK.
 */
export async function askLLM(query, context = '', opts = {}) {
  if (!opts.projectId) throw new Error('Project Id required');

  const url = askRecommendationsUrl(opts.projectId);

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': opts.CSRFToken,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, context }),
    signal: opts.signal,
  });

  if (!response.ok) {
    throw new Error(
      `LLM API error (ask): ${response.status} ${response.statusText}`
    );
  }

  return response.json();
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

  const response = await fetch(url, {
    method: 'GET',
    signal: opts.signal,
  });

  if (!response.ok) {
    throw new Error(
      `LLM API error (co-recommendations): ${response.status} ${response.statusText}`
    );
  }

  const data = await response.json();
  return data.co_recommendations || data || [];
}
