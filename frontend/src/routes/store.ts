import { writable, type Writable } from "svelte/store";

export let BACKEND: Writable<string> = writable(import.meta.env.VITE_BACKEND);
export let MODEL_LIST: Writable<string> = writable(import.meta.env.VITE_BACMODEL_LIST);

export const LIST_SPLITTER = "|";
// milliseconds
export const UPDATE_VIEW_INTERVAL = 5000;
export const REALTIME_FINETUNE_DETAIL = writable(false);
export const DEFAULT_MODEL_OUTPUT = writable(
    import.meta.env.VITE_DEFAULT_MODEL_OUTPUT || "/finetune_output"
);