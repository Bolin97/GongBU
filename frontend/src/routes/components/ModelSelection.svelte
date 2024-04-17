<script lang="ts">
    import axios from "axios";
    import type OpenllmEntry from "../../class/OpenllmEntry";
    import { onMount } from "svelte";
    import ModelCard from "./ModelCard.svelte";
    import type Adapter from "../../class/Adapter";

    export let selectedModelId = "";
    export let selectedAdapterId = "";
    export let enableAdapterSelection = false;

    let models = [] as Array<OpenllmEntry>;
    onMount(async () => {
        models = (await axios.get(`/api/openllm`)).data;
    });
</script>

<div class="grid grid-cols-2 m-4">
    {#each models as model}
        <div class="m-2">
            <ModelCard
                modelId={model.id}
                showAdapters={enableAdapterSelection}
                highlightBase={selectedModelId == model.id}
                on:baseClick={(_) => {
                    if(selectedModelId == model.id) {
                        selectedModelId = ""
                        selectedAdapterId = ""
                    } else {
                        selectedModelId = model.id.toString()
                        selectedAdapterId = ""
                    }
                }}
                highlightAdapter={selectedAdapterId}
                on:adapterClick={(e) => {
                    if(selectedAdapterId == e.detail.adapterId) {
                        selectedAdapterId = "";
                        selectedModelId = "";
                    } else {
                        selectedAdapterId = e.detail.adapterId;
                        selectedModelId = "";
                    }
                }}
            />
        </div>
    {/each}
</div>
