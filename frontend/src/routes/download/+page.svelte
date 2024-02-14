<script lang="ts">
    import { onMount } from "svelte";
    import type OpenllmEntry from "../../class/OpenllmEntry";
    import { BACKEND, MODEL_LIST } from "../store";
    import { Input } from "flowbite-svelte";

    let loading = true;
    let error_parsing = false;

    interface Model {
        model_name: string;
        source: string;
        model_description: string;
        lora_support: number;
        lora_multi_device: number;
        prefix_tuning_support: number;
        prefix_tuning_multi_device: number;
        ptuning_support: number;
        ptuning_multi_device: number;
        prompt_tuning_support: number;
        prompt_tuning_multi_device: number;
        IA3_support: number;
        IA3_multi_device: number;
        finetune: number;
        deployment: number;
        download_url: string;
        avatar_url: string | null | undefined;
    }

    let model_list: Model[] = [];

    try {
        model_list = JSON.parse($MODEL_LIST);
    }
    catch (e) {
        error_parsing = true;
    }

</script>

<div class="pt-2 w-full">
    <span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;下载模型</span>
    <span class="text-1xl pt-2 text-black-400 text-center"
        >&nbsp;&nbsp;下载模型</span
    >
</div>

<hr class="pt-1" />

{#if error_parsing}
    <div class="text-red-500">模型列表无效，请在设置页重设。</div>
{/if}

<div>
    {$MODEL_LIST}
</div>

{#if !loading}
<div>a</div>
{/if}