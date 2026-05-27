/**
 * Client pour l'API LLM externe (service ML Recoco).
 *
 * Utilitaire pur, sans dépendance à Alpine, réutilisable depuis n'importe
 * quel composant, store, ou code hors Alpine.
 *
 * Variables d'environnement (Vite) lues par défaut :
 * - VITE_ML_API_BASE_URL
 * - VITE_ML_API_TOKEN
 *
 * Toutes les options peuvent être surchargées via le paramètre `opts`.
 */

const DEFAULT_BASE_URL = import.meta.env.VITE_ML_API_BASE_URL;
const DEFAULT_TOKEN = import.meta.env.VITE_ML_API_TOKEN;

function buildHeaders(token) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

function buildUrl(baseUrl, path, params) {
  const base = (baseUrl || '').replace(/\/$/, '');
  const qs = params && params.toString() ? `?${params.toString()}` : '';
  return `${base}${path}${qs}`;
}

/**
 * Pose une question libre à la LLM avec un contexte facultatif.
 *
 * @param {string} query - La requête de l'utilisateur.
 * @param {string} [context] - Contexte additionnel (ex: description d'un projet).
 * @param {object} [opts]
 * @param {string|number} [opts.siteId] - Identifiant du site (multi-tenant).
 * @param {string} [opts.token] - Token Bearer (sinon VITE_ML_API_TOKEN).
 * @param {string} [opts.baseUrl] - URL de base (sinon VITE_ML_API_BASE_URL).
 * @param {AbortSignal} [opts.signal] - Pour annuler la requête.
 * @returns {Promise<{ answer_chunks: Array, citations: Array, found_answer: boolean }>}
 *   La réponse JSON brute de l'API.
 * @throws {Error} Si la requête échoue ou que la réponse n'est pas OK.
 */
export async function askLLM(query, context = '', opts = {}) {
  const baseUrl = opts.baseUrl || DEFAULT_BASE_URL;
  const token = opts.token !== undefined ? opts.token : DEFAULT_TOKEN;

  const params = new URLSearchParams();
  if (opts.siteId) {
    params.append('site_id', opts.siteId);
  }

  const url = buildUrl(baseUrl, '/ask', params);

  const response = await fetch(url, {
    method: 'POST',
    headers: buildHeaders(token),
    body: JSON.stringify({ query, context }),
    signal: opts.signal,
  });

  if (!response.ok) {
    throw new Error(`LLM API error (ask): ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Récupère les ressources fréquemment co-recommandées avec un ensemble de
 * ressources données.
 *
 * @param {Array<number|string>} resourceIds - Identifiants des ressources sources.
 * @param {object} [opts]
 * @param {string|number} [opts.siteId]
 * @param {string} [opts.token]
 * @param {string} [opts.baseUrl]
 * @param {AbortSignal} [opts.signal]
 * @returns {Promise<Array<{ resource_id: number, co_occurrence_score: number }>>}
 *   La liste des co-recommandations (peut être emballée dans
 *   { co_recommendations: [...] } selon la version de l'API — on normalise).
 * @throws {Error} Si la requête échoue.
 */
export async function fetchCoRecommendations(resourceIds, opts = {}) {
  const baseUrl = opts.baseUrl || DEFAULT_BASE_URL;
  const token = opts.token !== undefined ? opts.token : DEFAULT_TOKEN;

  const params = new URLSearchParams();
  resourceIds.forEach((id) => params.append('resource_ids', id));
  if (opts.siteId) {
    params.append('site_id', opts.siteId);
  }

  const url = buildUrl(baseUrl, '/co-recommendations', params);

  const response = await fetch(url, {
    method: 'GET',
    headers: buildHeaders(token),
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
