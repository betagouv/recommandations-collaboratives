/**
 * Alpine Store Devtools
 *
 * Outil de développement pour inspecter les stores Alpine.js en temps réel.
 *
 * Usage :
 * 1. Import dans main.js (ou un entry point) :
 *    import './utils/alpineStoreDevtools';
 *
 * 2. Raccourci clavier : Ctrl+Shift+S pour toggle le panneau
 *
 * 3. Ou via la console :
 *    window.AlpineStoreDevtools.toggle()
 *    window.AlpineStoreDevtools.show()
 *    window.AlpineStoreDevtools.hide()
 */

import Alpine from 'alpinejs';

const DEVTOOLS_ID = 'alpine-store-devtools';

// Ne s'active qu'en développement
const isDev = import.meta.env?.DEV ??
  (typeof process !== 'undefined' && process.env?.NODE_ENV === 'development') ??
  window.location.hostname === 'localhost';

/**
 * Registry des stores interceptés
 * Alpine 3.x ne permet pas d'accéder directement à tous les stores,
 * donc on patch Alpine.store() pour les capturer.
 */
const storeRegistry = {};

/**
 * Patch Alpine.store() pour intercepter les stores
 */
function patchAlpineStore() {
  const originalStore = Alpine.store.bind(Alpine);

  Alpine.store = function(name, value) {
    // Si on définit un store (2 arguments)
    if (value !== undefined) {
      const result = originalStore(name, value);
      // Enregistrer la référence au store
      storeRegistry[name] = originalStore(name);
      return result;
    }

    // Si on récupère un store (1 argument)
    const store = originalStore(name);
    if (store && !storeRegistry[name]) {
      storeRegistry[name] = store;
    }
    return store;
  };
}

/**
 * Noms de stores connus du projet (fallback)
 */
const KNOWN_STORE_NAMES = [
  'app',
  'utils',
  'editor',
  'djangoData',
  'onLeaveAlert',
  'crisp',
  'projects',
  'projectQueue',
  'tasksView',
  'tasksData',
  'actionPusher',
  'showRole',
  'previewModal',
  'geolocation',
  'tutorialsEvents',
  'idbObjectStoreMgmt',
  'resourcePreviewPanel',
  'sharedContentsPanel',
];

/**
 * Récupère tous les stores Alpine montés
 */
function getAlpineStores() {
  const stores = {};

  // Méthode 1: Registry de stores interceptés (si patch appliqué avant les stores)
  if (Object.keys(storeRegistry).length > 0) {
    Object.assign(stores, storeRegistry);
  }

  // Méthode 2: Alpine._stores (certaines versions/builds)
  if (Alpine._stores && typeof Alpine._stores === 'object') {
    Object.assign(stores, Alpine._stores);
  }

  // Méthode 3: Scanner les noms de stores connus via Alpine.store(name)
  // Cela fonctionne même si le patch n'a pas été appliqué à temps
  for (const name of KNOWN_STORE_NAMES) {
    if (!stores[name]) {
      try {
        const store = Alpine.store(name);
        if (store !== undefined) {
          stores[name] = store;
          // Ajouter au registry pour les prochains appels
          storeRegistry[name] = store;
        }
      } catch (e) {
        // Store n'existe pas, ignorer
      }
    }
  }

  return stores;
}

/**
 * Sérialise une valeur pour l'affichage
 */
function serializeValue(value, depth = 0, maxDepth = 4) {
  if (depth > maxDepth) return '...';

  if (value === null) return 'null';
  if (value === undefined) return 'undefined';

  const type = typeof value;

  if (type === 'function') {
    return `ƒ ${value.name || 'anonymous'}()`;
  }

  if (type === 'string') {
    const truncated = value.length > 100 ? value.slice(0, 100) + '...' : value;
    return `"${truncated}"`;
  }

  if (type === 'number' || type === 'boolean') {
    return String(value);
  }

  if (Array.isArray(value)) {
    if (value.length === 0) return '[]';
    if (depth >= maxDepth) return `Array(${value.length})`;
    return value;
  }

  if (type === 'object') {
    if (value instanceof Date) {
      return value.toISOString();
    }
    if (value instanceof RegExp) {
      return value.toString();
    }
    if (value instanceof Map) {
      return `Map(${value.size})`;
    }
    if (value instanceof Set) {
      return `Set(${value.size})`;
    }
    // Proxy Alpine ou objet simple
    return value;
  }

  return String(value);
}

/**
 * Crée le panneau de devtools
 */
function createDevtoolsPanel() {
  if (document.getElementById(DEVTOOLS_ID)) {
    return document.getElementById(DEVTOOLS_ID);
  }

  const panel = document.createElement('div');
  panel.id = DEVTOOLS_ID;
  panel.innerHTML = `
    <div x-data="AlpineStoreDevtools"
         x-show="isVisible"
         x-transition
         class="alpine-devtools-panel"
         :style="{ left: position.x + 'px', top: position.y + 'px' }">

      <!-- Header draggable -->
      <div class="alpine-devtools-header"
           @mousedown="startDrag($event)"
           @touchstart="startDrag($event)">
        <span class="alpine-devtools-title">Alpine Stores</span>
        <div class="alpine-devtools-actions">
          <button @click="refresh()" title="Rafraîchir" class="alpine-devtools-btn">
            ↻
          </button>
          <button @click="toggleMinimize()" title="Réduire" class="alpine-devtools-btn">
            <span x-text="isMinimized ? '▢' : '−'"></span>
          </button>
          <button @click="hide()" title="Fermer (Ctrl+Shift+S)" class="alpine-devtools-btn">
            ✕
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="alpine-devtools-content" x-show="!isMinimized" x-collapse>
        <!-- Search -->
        <div class="alpine-devtools-search">
          <input type="text"
                 x-model="searchTerm"
                 placeholder="Filtrer stores/props..."
                 class="alpine-devtools-input">
        </div>

        <!-- Stores list -->
        <div class="alpine-devtools-stores">
          <template x-for="(store, name) in filteredStores" :key="name">
            <div class="alpine-devtools-store">
              <div class="alpine-devtools-store-header"
                   @click="toggleStore(name)">
                <span class="alpine-devtools-arrow"
                      :class="{ 'expanded': expandedStores[name] }">▶</span>
                <span class="alpine-devtools-store-name" x-text="name"></span>
                <span class="alpine-devtools-store-count"
                      x-text="'(' + Object.keys(getStoreProperties(store)).length + ')'"></span>
              </div>

              <div class="alpine-devtools-store-content"
                   x-show="expandedStores[name]"
                   x-collapse>
                <template x-for="(value, key) in getStoreProperties(store)" :key="key">
                  <div class="alpine-devtools-property"
                       :class="{ 'is-function': typeof value === 'function' }">
                    <span class="alpine-devtools-key" x-text="key"></span>
                    <span class="alpine-devtools-separator">:</span>
                    <span class="alpine-devtools-value"
                          :class="getValueClass(value)"
                          :title="getFullValue(value)"
                          x-text="formatValue(value)"></span>
                  </div>
                </template>
              </div>
            </div>
          </template>

          <div x-show="Object.keys(filteredStores).length === 0"
               class="alpine-devtools-empty">
            Aucun store trouvé
          </div>
        </div>

        <!-- Footer -->
        <div class="alpine-devtools-footer">
          <span x-text="Object.keys(stores).length + ' stores'"></span>
          <span>•</span>
          <span>Ctrl+Shift+S</span>
        </div>
      </div>
    </div>
  `;

  // Injecter les styles
  injectStyles();

  document.body.appendChild(panel);
  return panel;
}

/**
 * Injecte les styles CSS
 */
function injectStyles() {
  if (document.getElementById('alpine-devtools-styles')) return;

  const styles = document.createElement('style');
  styles.id = 'alpine-devtools-styles';
  styles.textContent = `
    .alpine-devtools-panel {
      position: fixed;
      z-index: 99999;
      width: 360px;
      max-height: 70vh;
      background: #1e1e2e;
      border-radius: 8px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
      font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
      font-size: 12px;
      color: #cdd6f4;
      overflow: hidden;
      border: 1px solid #313244;
    }

    .alpine-devtools-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      background: #313244;
      cursor: grab;
      user-select: none;
    }

    .alpine-devtools-header:active {
      cursor: grabbing;
    }

    .alpine-devtools-title {
      font-weight: 600;
      color: #89b4fa;
    }

    .alpine-devtools-actions {
      display: flex;
      gap: 4px;
    }

    .alpine-devtools-btn {
      background: transparent;
      border: none;
      color: #a6adc8;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 14px;
      line-height: 1;
    }

    .alpine-devtools-btn:hover {
      background: #45475a;
      color: #cdd6f4;
    }

    .alpine-devtools-content {
      display: flex;
      flex-direction: column;
      max-height: calc(70vh - 40px);
    }

    .alpine-devtools-search {
      padding: 8px;
      border-bottom: 1px solid #313244;
    }

    .alpine-devtools-input {
      width: 100%;
      padding: 6px 10px;
      background: #11111b;
      border: 1px solid #45475a;
      border-radius: 4px;
      color: #cdd6f4;
      font-family: inherit;
      font-size: 12px;
    }

    .alpine-devtools-input:focus {
      outline: none;
      border-color: #89b4fa;
    }

    .alpine-devtools-stores {
      overflow-y: auto;
      flex: 1;
      padding: 4px 0;
    }

    .alpine-devtools-store {
      border-bottom: 1px solid #313244;
    }

    .alpine-devtools-store:last-child {
      border-bottom: none;
    }

    .alpine-devtools-store-header {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 12px;
      cursor: pointer;
      transition: background 0.15s;
    }

    .alpine-devtools-store-header:hover {
      background: #313244;
    }

    .alpine-devtools-arrow {
      color: #6c7086;
      font-size: 10px;
      transition: transform 0.15s;
    }

    .alpine-devtools-arrow.expanded {
      transform: rotate(90deg);
    }

    .alpine-devtools-store-name {
      color: #f9e2af;
      font-weight: 500;
    }

    .alpine-devtools-store-count {
      color: #6c7086;
      font-size: 11px;
    }

    .alpine-devtools-store-content {
      padding: 4px 12px 8px 24px;
      background: #181825;
    }

    .alpine-devtools-property {
      display: flex;
      align-items: flex-start;
      gap: 4px;
      padding: 3px 0;
      line-height: 1.4;
    }

    .alpine-devtools-property.is-function {
      opacity: 0.6;
    }

    .alpine-devtools-key {
      color: #94e2d5;
      flex-shrink: 0;
    }

    .alpine-devtools-separator {
      color: #6c7086;
    }

    .alpine-devtools-value {
      color: #cdd6f4;
      word-break: break-all;
      cursor: default;
    }

    .alpine-devtools-value.string { color: #a6e3a1; }
    .alpine-devtools-value.number { color: #fab387; }
    .alpine-devtools-value.boolean { color: #f38ba8; }
    .alpine-devtools-value.null { color: #6c7086; font-style: italic; }
    .alpine-devtools-value.function { color: #89b4fa; font-style: italic; }
    .alpine-devtools-value.object { color: #cba6f7; }
    .alpine-devtools-value.array { color: #89dceb; }

    .alpine-devtools-empty {
      padding: 20px;
      text-align: center;
      color: #6c7086;
    }

    .alpine-devtools-footer {
      display: flex;
      justify-content: center;
      gap: 8px;
      padding: 6px;
      background: #313244;
      color: #6c7086;
      font-size: 11px;
    }

    /* Responsive */
    @media (max-width: 480px) {
      .alpine-devtools-panel {
        width: calc(100vw - 20px);
        left: 10px !important;
        right: 10px;
      }
    }
  `;

  document.head.appendChild(styles);
}

/**
 * Composant Alpine pour les devtools
 */
Alpine.data('AlpineStoreDevtools', () => ({
  isVisible: false,
  isMinimized: false,
  stores: {},
  expandedStores: {},
  searchTerm: '',
  position: { x: 20, y: 20 },
  isDragging: false,
  dragOffset: { x: 0, y: 0 },

  init() {
    this.refresh();

    // Rafraîchissement périodique pour capturer les changements réactifs
    this._refreshInterval = setInterval(() => {
      if (this.isVisible && !this.isMinimized) {
        this.refresh();
      }
    }, 500);

    // Gestion du drag
    this._onMouseMove = this.onDrag.bind(this);
    this._onMouseUp = this.stopDrag.bind(this);

    // Charger la position sauvegardée
    const savedPosition = localStorage.getItem('alpine-devtools-position');
    if (savedPosition) {
      try {
        this.position = JSON.parse(savedPosition);
      } catch (e) {}
    }
  },

  destroy() {
    if (this._refreshInterval) {
      clearInterval(this._refreshInterval);
    }
  },

  refresh() {
    this.stores = getAlpineStores();
  },

  get filteredStores() {
    if (!this.searchTerm) return this.stores;

    const term = this.searchTerm.toLowerCase();
    const filtered = {};

    for (const [name, store] of Object.entries(this.stores)) {
      // Filtre par nom de store
      if (name.toLowerCase().includes(term)) {
        filtered[name] = store;
        continue;
      }

      // Filtre par nom de propriété
      const props = this.getStoreProperties(store);
      const hasMatchingProp = Object.keys(props).some(key =>
        key.toLowerCase().includes(term)
      );

      if (hasMatchingProp) {
        filtered[name] = store;
      }
    }

    return filtered;
  },

  getStoreProperties(store) {
    if (!store || typeof store !== 'object') return {};

    const props = {};

    // Récupérer toutes les propriétés (y compris celles du proxy Alpine)
    const allKeys = new Set([
      ...Object.keys(store),
      ...Object.getOwnPropertyNames(store)
    ]);

    for (const key of allKeys) {
      // Ignorer les propriétés internes Alpine
      if (key.startsWith('_') || key.startsWith('$')) continue;

      try {
        props[key] = store[key];
      } catch (e) {
        props[key] = '[Erreur de lecture]';
      }
    }

    return props;
  },

  toggleStore(name) {
    this.expandedStores[name] = !this.expandedStores[name];
  },

  formatValue(value) {
    return serializeValue(value);
  },

  getFullValue(value) {
    if (typeof value === 'string' && value.length > 100) {
      return value;
    }
    if (typeof value === 'object' && value !== null) {
      try {
        return JSON.stringify(value, null, 2);
      } catch (e) {
        return '[Circular]';
      }
    }
    return String(value);
  },

  getValueClass(value) {
    if (value === null || value === undefined) return 'null';
    if (typeof value === 'function') return 'function';
    if (typeof value === 'string') return 'string';
    if (typeof value === 'number') return 'number';
    if (typeof value === 'boolean') return 'boolean';
    if (Array.isArray(value)) return 'array';
    if (typeof value === 'object') return 'object';
    return '';
  },

  show() {
    this.isVisible = true;
    this.refresh();
  },

  hide() {
    this.isVisible = false;
  },

  toggle() {
    this.isVisible ? this.hide() : this.show();
  },

  toggleMinimize() {
    this.isMinimized = !this.isMinimized;
  },

  startDrag(event) {
    if (event.target.closest('button')) return;

    this.isDragging = true;
    const clientX = event.touches?.[0]?.clientX ?? event.clientX;
    const clientY = event.touches?.[0]?.clientY ?? event.clientY;

    this.dragOffset = {
      x: clientX - this.position.x,
      y: clientY - this.position.y
    };

    document.addEventListener('mousemove', this._onMouseMove);
    document.addEventListener('mouseup', this._onMouseUp);
    document.addEventListener('touchmove', this._onMouseMove);
    document.addEventListener('touchend', this._onMouseUp);
  },

  onDrag(event) {
    if (!this.isDragging) return;

    event.preventDefault();
    const clientX = event.touches?.[0]?.clientX ?? event.clientX;
    const clientY = event.touches?.[0]?.clientY ?? event.clientY;

    this.position = {
      x: Math.max(0, Math.min(window.innerWidth - 100, clientX - this.dragOffset.x)),
      y: Math.max(0, Math.min(window.innerHeight - 50, clientY - this.dragOffset.y))
    };
  },

  stopDrag() {
    this.isDragging = false;
    document.removeEventListener('mousemove', this._onMouseMove);
    document.removeEventListener('mouseup', this._onMouseUp);
    document.removeEventListener('touchmove', this._onMouseMove);
    document.removeEventListener('touchend', this._onMouseUp);

    // Sauvegarder la position
    localStorage.setItem('alpine-devtools-position', JSON.stringify(this.position));
  }
}));

/**
 * API publique
 */
const AlpineStoreDevtools = {
  _component: null,

  _getComponent() {
    const panel = document.getElementById(DEVTOOLS_ID);
    if (panel) {
      const el = panel.querySelector('[x-data="AlpineStoreDevtools"]');
      if (el && el._x_dataStack) {
        return el._x_dataStack[0];
      }
    }
    return null;
  },

  show() {
    const comp = this._getComponent();
    if (comp) comp.show();
  },

  hide() {
    const comp = this._getComponent();
    if (comp) comp.hide();
  },

  toggle() {
    const comp = this._getComponent();
    if (comp) comp.toggle();
  },

  getStores() {
    return getAlpineStores();
  },

  logStores() {
    console.table(
      Object.entries(getAlpineStores()).map(([name, store]) => ({
        name,
        properties: Object.keys(store).filter(k => !k.startsWith('_')).length,
        methods: Object.keys(store).filter(k => typeof store[k] === 'function').length
      }))
    );
  }
};

// Initialisation
function init() {
  if (!isDev) {
    console.log('[Alpine Store Devtools] Désactivé en production');
    return;
  }

  // Patcher Alpine.store() immédiatement pour capturer tous les stores
  patchAlpineStore();

  // Créer le panneau quand le DOM est prêt
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      // Attendre un tick pour que tous les stores soient enregistrés
      setTimeout(createDevtoolsPanel, 100);
    });
  } else {
    setTimeout(createDevtoolsPanel, 100);
  }

  // Raccourci clavier
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'S') {
      e.preventDefault();
      AlpineStoreDevtools.toggle();
    }
  });

  // Exposer l'API globalement
  window.AlpineStoreDevtools = AlpineStoreDevtools;

  console.log(
    '%c[Alpine Store Devtools] %cActivé - Ctrl+Shift+S pour toggle',
    'color: #89b4fa; font-weight: bold;',
    'color: #a6adc8;'
  );
}

init();

export default AlpineStoreDevtools;
