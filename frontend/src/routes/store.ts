import { writable, type Writable } from "svelte/store";
function persist(key, value) {
    const isBrowser = typeof window !== 'undefined';
    const storedValue = isBrowser ? localStorage.getItem(key) : null;
    const initial = storedValue ? JSON.parse(storedValue) : value;

    const store = writable(initial);
    if (isBrowser) {
        store.subscribe($value => {
            localStorage.setItem(key, JSON.stringify($value));
        });
    }

    return store;
}

export let MODEL_LIST: Writable<string> = persist("model_list", import.meta.env.VITE_MODEL_LIST || "[]");

// milliseconds
export const UPDATE_VIEW_INTERVAL = 5000;
export const REALTIME_FINETUNE_DETAIL = writable(false);
export const DEFAULT_MODEL_OUTPUT = writable(import.meta.env.VITE_DEFAULT_MODEL_OUTPUT || "/finetune_output");

export const token = writable(null);