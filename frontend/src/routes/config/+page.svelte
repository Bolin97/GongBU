<script lang="ts">
    import { stringify } from "postcss";
    import { BACKEND, MODEL_LIST } from "../store";
    import { Input, Textarea } from "flowbite-svelte";

</script>

<div class="pt-2 w-full">
    <span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;设置</span>
    <span class="text-1xl pt-2 text-black-400 text-center"
        >&nbsp;&nbsp;配置系统参数</span
    >
</div>

<hr class="pt-1" />

<div class="grid grid-cols-1">
    <div class="m-2 p-2">
        <span class="my-2">后端地址</span>
        <Input
            bind:value={$BACKEND}
        />
    </div>
    <div class="m-2 p-2">
        <span class="my-2">模型列表</span>
        <Textarea
            rows="16"
            bind:value={$MODEL_LIST}
        />
    </div>
</div>