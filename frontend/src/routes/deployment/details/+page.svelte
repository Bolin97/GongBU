<script lang="ts">
    import { page } from "$app/stores";
    import { Button, Hr, Modal } from "flowbite-svelte";
    import ActionPageTitle from "../../components/ActionPageTitle.svelte";
    import type Deployment from "../../../class/Deployment";
    import { getContext, onDestroy, onMount } from "svelte";
    import axios from "axios";
    import type OpenllmEntry from "../../../class/OpenllmEntry";
    import type Adapter from "../../../class/Adapter";
    import { UPDATE_VIEW_INTERVAL } from "../../store";
    import ModelCard from "../../components/ModelCard.svelte";
    import DeviceInfo from "../../components/DeviceInfo.svelte";
    import WrappedIframe from "./WrappedIframe.svelte";
    import { goto } from "$app/navigation";
    const t: any = getContext("t");
    const deployment_id = $page.url.searchParams.get("deployment_id");
    let deployment_entry: Deployment = null;
    let base_model: OpenllmEntry = null;
    let adapter: Adapter = null;


    async function fetchInfo() {
        deployment_entry = (await axios.get(`/api/deployment/${deployment_id}`)).data;
        if(deployment_entry.deploy_base_model) {
            base_model = (await axios.get(`/api/openllm/${deployment_entry.model_or_adapter_id}`)).data;
            adapter = null;
        } else {
            adapter = (await axios.get(`/api/adapter/${deployment_entry.model_or_adapter_id}`)).data;
            base_model = (await axios.get(`/api/openllm/entry/by_model_name/${adapter.base_model_name}`)).data;
        }
        stopClicked = false;
        startClicked = false;
    }
    let updater: any;
    onMount(async () => {
        fetchInfo();
        updater = setInterval(fetchInfo, UPDATE_VIEW_INTERVAL);
    });
    let startClicked = false;
    onDestroy(() => {
        clearInterval(updater);
    });

    async function handleStart() {
        startClicked = true;
        await axios.put(`/api/deployment/start/${deployment_id}`);
        fetchInfo();
    }

    let stopClicked = false;

    async function handleStop() {
        stopClicked = true;
        await axios.put(`/api/deployment/stop/${deployment_id}`);
        fetchInfo();
    }

    let delete_modal = false
    async function delete_entry_handle() {
        await axios.delete(`/api/deployment/${deployment_id}`);
        goto("/deployment");
    }
</script>


<Modal title="确认删除" bind:open={delete_modal} autoclose>
	<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">确认要删除吗？</p>
	<p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
		删除后，该任务的所有相关信息将<span class="font-semibold">无法</span>恢复。
	</p>
	<svelte:fragment slot="footer">
		<div class="w-full flex justify-end gap-2">
			<Button
				color="red"
				on:click={() => {
					delete_entry_handle();
				}}>删除</Button
			>
			<Button color="alternative">不</Button>
		</div>
	</svelte:fragment>
</Modal>

{#if base_model != null && deployment_entry != null}
<div>
    <ActionPageTitle returnTo="/deployment" title="详细信息">
        <svelte:fragment slot="right">
            <div class="flex gap-2">
                {#if deployment_entry.state == 2 && !stopClicked}
                    <Button color="blue" on:click={handleStop}>停止</Button>
                {/if}
                {#if deployment_entry.state == 0 && !startClicked}
                    <Button on:click={handleStart} color="green">启动</Button>
                {/if}
                <Button
                    color="red"
                    on:click={() => {
                        delete_modal = true;
                    }}
                >
                    删除
                </Button>
            </div>
        </svelte:fragment>
    </ActionPageTitle>
    <div class="flex flex-row">
        <div class="w-1/2">
            <div class="p-4 w-full">
                <div class="uppercase tracking-wide text-sm text-blue-600 font-semibold">{deployment_entry.name}</div>
                <p class="mt-2 text-gray-500">{deployment_entry.description}</p>
                <div class="mt-2">
                    <span class="text-gray-900 font-bold">State: </span>
                    <span class="text-gray-600">
                        {#if deployment_entry.state == 0}
                            {t("delpoyment.stopped")}
                        {:else if deployment_entry.state == 1}
                            {t("delpoyment.starting")}
                        {:else if deployment_entry.state == 2}
                            {t("delpoyment.running")}
                        {/if}    
                    </span>
                </div>
                <Hr/>
                <div class="mt-2">
                    <span class="text-gray-900 font-bold">Gradio Link: </span>
                    <div class="text-sm">
                        <p>
                            {t("deployment.gradio_url_prefix") + `/net/${deployment_entry.port}/`}
                        </p>
                        <p class="my-2">
                            {t("deployment.or")}
                        </p>
                        <p>
                            <a href={`/net/${deployment_entry.port}/`} target="_blank" class="text-blue-600 hover:underline">
                                {window.location.origin + `/net/${deployment_entry.port}/`}
                            </a>
                        </p>
                    </div>
                </div>
                <Hr/>
                <div class="mt-2">
                    <span class="text-gray-900 font-bold">Model: </span>
                    <ModelCard modelId={base_model.id} baseModelNoCursorChange/>
                </div>
                {#if adapter != null}
                    <div class="mt-2">
                        <span class="text-gray-900 font-bold">Adapter Name: </span>
                        <span class="text-gray-600">{adapter ? adapter.adapter_name : 'N/A'}</span>
                    </div>
                {/if}
                <Hr/>
                <div class="mt-2">
                    <div>
                        <span class="text-gray-900 font-bold">Deepspeed: </span>
                        <span class="text-gray-600">{deployment_entry.use_deepspeed ? 'Yes' : 'No'}</span>
                    </div>
                    <div>
                        <span class="text-gray-900 font-bold">Flash Attention: </span>
                        <span class="text-gray-600">{deployment_entry.use_flash_attention ? 'Yes' : 'No'}</span>
                    </div>
                </div>
                <Hr/>
                <div class="mt-2">
                    <span class="text-gray-900 font-bold">Device</span>
                    <div>
                        <DeviceInfo showDevices={deployment_entry.devices}/>
                    </div>
                </div>
            </div>
        </div>
        <div class="w-1/2">
            <WrappedIframe link={`/net/${deployment_entry.port}/`} avaliable={deployment_entry.state == 2}/>
        </div>
    </div>
</div>
{/if}