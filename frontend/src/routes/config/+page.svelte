<script lang="ts">
  import { stringify } from "postcss";
  import { MODEL_LIST } from "../store";
  import { Button, Input, Textarea } from "flowbite-svelte";
  import { ArrowLeftToBracketOutline } from "flowbite-svelte-icons";
  import { getContext } from "svelte";
  import { goto } from "$app/navigation";
  const t: any = getContext("t");
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
    <span class="my-2">{t("config.model_list")}</span>
    <Textarea rows="16" bind:value={$MODEL_LIST} />
  </div>

  <div class="m-2 p-2">
    <span class="my-2">{t("config.log_out")}</span>
    <div class="my-2">
      <Button
        on:click={() => {
          //logout, then refresh the page
          localStorage.removeItem("access_token");
          goto("/");
          //refresh the page
          location.reload();
        }}
      >
        <ArrowLeftToBracketOutline />{t("config.log_out")}
      </Button>
    </div>
  </div>
</div>
