// =============================================================================
// Project Monaro / F-DSE Risk Intelligence — Centralized Reactive State Store
// Google Standards Compliant (go/tsstyle, go/js-practices)
// =============================================================================

export class StateStore {
    constructor(initialState = {}) {
        this.state = {
            projectSlug: 'sample',
            config: null,
            rawData: null,
            liveRisks: [],
            liveIssues: [],
            teamGoogleRisks: [],
            blueprints: [],
            driverTree: [],
            timeMachineSnapshots: {},
            activeTimeMachineWeek: 'present',
            activeTab: 'exec-briefing',
            matrixRating: 'inherent',
            matrixStatus: 'open',
            activeMatrixCellFilter: null,
            teamGoogleMatrixRating: 'inherent',
            teamGoogleMatrixStatus: 'open',
            teamGoogleActiveMatrixCellFilter: null,
            searchQuery: '',
            filterCategory: 'all',
            filterBundle: 'all',
            filterGovernance: 'all',
            sortColumn: 'id',
            sortDirection: 'asc',
            ...initialState
        };

        this.listeners = new Map();
    }

    /**
     * Get current state snapshot or specific property.
     * @param {string} [key] 
     * @returns {*}
     */
    get(key) {
        return key ? this.state[key] : { ...this.state };
    }

    /**
     * Update state and notify subscribers.
     * @param {Object|string} keyOrObj 
     * @param {*} [val] 
     */
    set(keyOrObj, val) {
        const changes = typeof keyOrObj === 'string' ? { [keyOrObj]: val } : keyOrObj;
        let hasChanged = false;

        for (const [k, v] of Object.entries(changes)) {
            if (this.state[k] !== v) {
                this.state[k] = v;
                hasChanged = true;
                this._notify(k, v);
            }
        }

        if (hasChanged) {
            this._notify('*', this.state);
        }
    }

    /**
     * Subscribe to state property changes.
     * @param {string} key ('*' for all changes)
     * @param {Function} callback (newVal, key) => void
     * @returns {Function} unsubscribe function
     */
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, new Set());
        }
        this.listeners.get(key).add(callback);

        return () => {
            const set = this.listeners.get(key);
            if (set) {
                set.delete(callback);
                if (set.size === 0) this.listeners.delete(key);
            }
        };
    }

    _notify(key, value) {
        const set = this.listeners.get(key);
        if (set) {
            for (const cb of set) {
                try {
                    cb(value, key);
                } catch (err) {
                    console.error('[StateStore] Error in subscriber for ' + key + ':', err);
                }
            }
        }
    }
}

export const store = new StateStore();
