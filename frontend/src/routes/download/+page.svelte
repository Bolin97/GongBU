<script lang="ts">
    import { onDestroy, onMount } from "svelte";
    import type OpenllmEntry from "../../class/OpenllmEntry";
    import { BACKEND, MODEL_LIST, UPDATE_VIEW_INTERVAL } from "../store";
    import { Alert, Button, Input, Modal, Toast } from "flowbite-svelte";
    import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from 'flowbite-svelte';
    import axios from "axios";
    import { CloseSolid } from "flowbite-svelte-icons";

    let error_parsing = false;

    class ModelListItem {
        model_display_name: string;
        model_name: string;
        source: string;
        model_description: string;
        download_url: string;
        avatar_url: string | null | undefined;
    }

    let model_list: ModelListItem[] = [];

    try {
        model_list = JSON.parse($MODEL_LIST);
        //check if every element in the model_list is a Model
        const valid = Object.keys(new ModelListItem()).every((key) => {
            return model_list.every((model) => {
                return key in model;
            });
        });
        if (!valid) {
            throw new Error("Invalid model list");
        }
    }
    catch (e) {
        error_parsing = true;
    }

    let model_stored = [] as Array<OpenllmEntry>;
    async function refresh_model_stored() {
        model_stored = (await axios.get(`${$BACKEND}/openllm/`)).data as Array<OpenllmEntry>;
    }
    let updater: number;
	onMount(async () => {
        refresh_model_stored();
		updater = setInterval(refresh_model_stored, UPDATE_VIEW_INTERVAL);
	});
    onDestroy(async () => {
        clearInterval(updater);
    });

    async function automatic_download(model: ModelListItem) {
        const response = await axios.post(`${$BACKEND}/openllm/download`, model);
        await refresh_model_stored();
    }

    async function write_only_info(model: ModelListItem) {
        const response = await axios.post(`${$BACKEND}/openllm/no_download`, model);
        await refresh_model_stored();
    }

    let delete_modal = false;
    let delete_modal_id = "";
    let delete_entry_modal = false;

    let alerts = [];
    function add_alert(title: string, body: string) {
        alerts = [...alerts, { title: title, body: body }];
    }
    function delete_alert(index: number) {
        alerts = alerts.filter((_, i) => i !== index);
    }
    function delete_all_alerts() {
        alerts = [];
    }
</script>





<Modal title="确认删除" bind:open={delete_modal} autoclose>
    <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
        确定要删除这个模型的所有记录和文件吗？
    </p>
    <p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
        此操作<span class="font-semibold">无法撤回</span>
    </p>
    <svelte:fragment slot="footer">
        <div class="w-full flex justify-end gap-2">
            <Button color="red" on:click={() => {
                axios.delete(`${$BACKEND}/openllm/${delete_modal_id}`);
                refresh_model_stored();
                delete_modal = false;
                delete_modal_id = "";
            }}>删除</Button>
            <Button color="alternative" on:click={() => delete_modal = false}>不</Button>
        </div>
    </svelte:fragment>
</Modal>

<Modal title="确认删除" bind:open={delete_entry_modal} autoclose>
    <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
        确定要删除这个模型的所有记录吗？
    </p>
    <p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
        此操作<span class="font-semibold">无法撤回</span>
    </p>
    <p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
        模型的文件将<span class="font-semibold">不会</span>被删除。
    </p>
    <svelte:fragment slot="footer">
        <div class="w-full flex justify-end gap-2">
            <Button color="red" on:click={() => {
                axios.delete(`${$BACKEND}/openllm/entry/${delete_modal_id}`);
                refresh_model_stored();
                delete_entry_modal = false;
                delete_modal_id = "";
            }}>删除</Button>
            <Button color="alternative" on:click={() => delete_modal = false}>不</Button>
        </div>
    </svelte:fragment>
</Modal>

<div class="pt-2 w-full">
    <span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;下载模型</span>
    <span class="text-1xl pt-2 text-black-400 text-center"
        >&nbsp;&nbsp;下载模型</span
    >
</div>

<hr class="pt-1" />

{#if alerts.length > 1} 
<div class="w-full mx-2 my-4">
    <Alert>
        <button on:click={() => {delete_all_alerts()}} class="flex justify-between items-center">
            <span class="font-medium hover:underline">
                关闭所有提醒
            </span>
        </button>
    </Alert>
</div>
{/if}

{#each alerts as alert, index}
    <div class="w-full mx-2 my-4">
        <Alert>
            <div class="flex justify-between items-center">
                <div>
                    <div class="font-medium">{alert.title}</div>
                    <div>{alert.body}</div>
                </div>
                <button on:click={() => {delete_alert(index)}}>
                    <CloseSolid/>
                </button>
            </div>
        </Alert>
    </div>
{/each}

{#if error_parsing}
    <div class="text-red-500">模型列表无效，请在设置页重设。</div>
{:else}
<div class="text-lg font-bold m-2">
    <span>模型列表</span>
</div>
<div class="table w-full my-2">
    <Table>
        <TableHead>
            <TableHeadCell>模型</TableHeadCell>
            <TableHeadCell>描述</TableHeadCell>
            <TableHeadCell>下载地址</TableHeadCell>
            <TableHeadCell>操作</TableHeadCell>
        </TableHead>
        <TableBody>
            {#each model_list as model}
            <TableBodyRow>
                <TableBodyCell>{model.model_name}</TableBodyCell>
                <TableBodyCell>{model.model_description}</TableBodyCell>
                <TableBodyCell>{model.download_url}</TableBodyCell>
                <TableBodyCell><div class="flex flex-row">
                    <button on:click={() => {
                        automatic_download(model);
                        add_alert(`模型${model.model_name}信息已写入，模型文件已开始下载。`, ``);
                    }} class="mx-2 text-blue-600 hover:underline">
                        自动下载
                    </button>
                    <button on:click={() => {
                        write_only_info(model);
                        add_alert(`模型${model.model_name}信息已写入，请手动下载模型文件。`, `将通过${model.download_url}下载得到的，包含config.json的文件夹重命名为${model.model_name}并放入models文件夹。`);
                    }} class="mx-2 text-blue-600 hover:underline">
                        仅写入信息（手动下载）
                    </button>
                </div></TableBodyCell>
            </TableBodyRow>
            {/each}
        </TableBody>
        </Table>
</div>
{/if}

<div class="text-lg font-bold m-2">
    <span>已有模型</span>
</div>

<div class="table w-full my-2">
    <Table>
        <TableHead>
          <TableHeadCell>模型</TableHeadCell>
          <TableHeadCell>描述</TableHeadCell>
          <TableHeadCell>下载地址</TableHeadCell>
          <TableHeadCell>状态</TableHeadCell>
          <TableHeadCell>操作</TableHeadCell>
        </TableHead>
        <TableBody>
          {#each model_stored as model}
            <TableBodyRow>
                <TableBodyCell><div class="w-20 whitespace-normal overflow-auto">
                    {model.model_name}
                </div></TableBodyCell>
                <TableBodyCell><div class="w-40 whitespace-normal overflow-auto">
                    {model.model_description}
                </div></TableBodyCell>
                <TableBodyCell><div class="whitespace-normal overflow-auto">
                    {model.remote_path}
                </div></TableBodyCell>
                <TableBodyCell><div class="whitespace-normal overflow-auto">
                    {model.storage_state}
                </div></TableBodyCell>
                <TableBodyCell><div class="flex flex-row">
                    <button class="mx-2 text-red-600 hover:underline" on:click={() => {
                        delete_modal_id = model.model_id;
                        delete_modal = true;
                    }}>
                        删除记录和模型文件
                    </button>
                    <button class="mx-2 text-red-600 hover:underline" on:click={() => {
                        delete_modal_id = model.model_id;
                        delete_entry_modal = true;
                    }}>
                        仅删除记录
                    </button>
                </div></TableBodyCell>
            </TableBodyRow>
          {/each}
        </TableBody>
      </Table>
</div>