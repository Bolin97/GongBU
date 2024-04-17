<script lang="ts">
    import { page } from "$app/stores";
    import axios from "axios";
    import type OpenllmEntry from "../../class/OpenllmEntry";
    import { createEventDispatcher, onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { Accordion, AccordionItem } from "flowbite-svelte";
    import { getContext } from "svelte";
    import type Adapter from "../../class/Adapter";

    const t: any = getContext("t");

    const dispatcher = createEventDispatcher();

    export let modelId: string;
    export let highlightBase = false;
    export let showAdapters = false;
    export let adapterAction = false;
    export let highlightAdapter: string | null = null;
    export let baseModelNoCursorChange = false;
    export let adapterNoCursorChange = false;

    let model: OpenllmEntry = null;
    let adapters = [] as Array<Adapter>;

    onMount(async () => {
        model = (await axios.get(`/api/openllm/${modelId}`)).data;
        if (showAdapters) {
            adapters = (
                await axios.get(`/api/adapter/by_base_model/${modelId}`)
            ).data;
        }
    });
</script>

{#if model != null}
<div
    class={
    `p-2 bg-white rounded-md overflow-hidden border shadow-sm shadow-gray-300 border-grey-300`
}
>
    <div class="flex">
        <div class="md:flex-shrink-0">
            <img
                class="h-32 w-full object-scale-down md:w-32"
                src={`/api/openllm/avatar/${modelId}`}
                alt={model.display_name}
            />
        </div>
        <button class={`p-2 ${baseModelNoCursorChange ? "cursor-default" : ""} w-full rounded-md ${highlightBase ? "text-white bg-blue-400 border border-blue-800 shadow-lg" : ""}`}
            on:click={() => dispatcher("baseClick", model)}
        >
            <div
                class={`tracking-wide text-md ${highlightBase ? "text-white" : "text-blue-600"} font-bold`}
            >
                {model.display_name}
            </div>
            <p class="mt-1 ${highlightBase ? "text-white" : "text-gray-800"} text-xs">{model.model_description}</p>
            <div class="mt-2">
                <slot name="base-action" />
            </div>
        </button>
    </div>
    {#if showAdapters && adapters.length > 0}
        <div class="mx-4">
            <Accordion flush>
                <AccordionItem>
                    <span slot="header"
                        >{t("components.model_card.adapters")}</span
                    >
                    <table class="table-auto border-collapse w-full h-full">
                        <thead>
                            <tr
                                class="rounded-lg text-sm font-medium text-gray-700 text-left"
                                style="font-size: 0.9674rem"
                            >
                                <th
                                    class="px-4 py-2 bg-gray-200"
                                    style="background-color:#f8f8f8"
                                    >{t("components.model_card.id")}</th
                                >
                                <th
                                    class="px-4 py-2 bg-gray-200"
                                    style="background-color:#f8f8f8"
                                    >{t(
                                        "components.model_card.name_and_description",
                                    )}</th
                                >
                                {#if adapterAction}
                                    <th
                                        class="px-4 py-2 bg-gray-200"
                                        style="background-color:#f8f8f8"
                                    >
                                        {t("components.model_card.action")}
                                    </th>
                                {/if}
                            </tr>
                        </thead>
                        <tbody class="text-sm font-normal text-gray-700">
                            {#each adapters as adapter}
                                <tr on:click={() => {
                                    dispatcher("adapterClick", {
                                        adapterId: adapter.id
                                    });
                                }} class={`my-2 ${adapter.id === highlightAdapter ? "bg-blue-400 text-white border border-blue-800" : "hover:bg-gray-100 border border-transparent"} ${adapterNoCursorChange ? "" : "cursor-pointer"}`}>
                                    <td class="px-4 py-2">{adapter.id}</td>
                                    <td class={`px-4 py-2 `}
                                        ><div class="flex flex-col">
                                            <div>{adapter.adapter_name}</div>
                                            <div class={`text-xs ${adapter.id === highlightAdapter ? "text-white": "text-gray-500"}`}>
                                                {adapter.adapter_description}
                                            </div>
                                        </div></td
                                    >
                                    {#if adapterAction}
                                        <td class="px-4 py-2">
                                            <slot name="adapter-action" adapter={adapter}/>
                                        </td>  
                                    {/if}
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </AccordionItem>
            </Accordion>
        </div>
    {/if}
</div>
{/if}