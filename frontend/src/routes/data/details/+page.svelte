<script lang="ts">
  import { Label, Radio, Button, Hr, Modal } from "flowbite-svelte";
  import { AngleLeftOutline } from "flowbite-svelte-icons";
  import { page } from "$app/stores";
  import Uploader from "../Uploader.svelte";
  import { goto } from "$app/navigation";
  import axios from "axios";
  import { getContext } from "svelte";
  const t: any = getContext("t");

  const id = $page.url.searchParams.get("pool_id");

  let next_modal = false;
  let delete_modal = false;
  let stage_empty: boolean;

  async function handle_delete() {
    await axios.delete(`/api/pool/${id}`);
    goto(`/data`);
  }

  function return_handle() {
    if (stage_empty) {
      goto(`/data`);
    } else {
      next_modal = true;
    }
  }
</script>

<Modal title={t("data.detail.title_1")} bind:open={delete_modal} autoclose>
  <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
    {t("data.detail.p1")}
  </p>
  <p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
    {t("data.detail.p2")}<span class="font-semibold">{t("data.detail.p3")}</span>{t("data.detail.p4")}
  </p>
  <svelte:fragment slot="footer">
    <div class="w-full flex justify-end gap-2">
      <Button
        color="red"
        on:click={() => {
          handle_delete();
        }}>{t("data.detail.yes")}</Button
      >
      <Button color="alternative">{t("data.detail.no")}</Button>
    </div>
  </svelte:fragment>
</Modal>

<Modal title={t("data.detail.title_2")} bind:open={next_modal} autoclose>
  <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
    {t("data.detail.p5")}
  </p>
  <p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
    {t("data.detail.p6")}<span class="font-semibold">{t("data.detail.p7")}</span>{t("data.detail.p8")}
  </p>
  <svelte:fragment slot="footer">
    <div class="w-full flex justify-end gap-2">
      <Button
        color="red"
        on:click={() => {
          goto(`/data/details?pool_id=${id}`);
        }}>{t("data.detail.yes")}</Button
      >
      <Button color="alternative">{t("data.detail.no")}</Button>
    </div>
  </svelte:fragment>
</Modal>
<div class="flex flex-row justify-between">
  <div class="flex">
    <div class="flex flex-row">
      <Button
        on:click={(_) => {
          return_handle();
        }}
      >
        <AngleLeftOutline size="sm" />{t("components.go_back")}
      </Button>
    </div>
    <span class="text-2xl pt-1 text-black-400 font-bold"
      >&nbsp;&nbsp;{t("data.detail.detail")}</span
    >
  </div>
  <div class="flex flex-row">
    <Button
      on:click={(_) => {
        delete_modal = true;
      }}
      color="red"
    >
      {t("data.detail.delete")}
    </Button>
  </div>
</div>
<Hr />
<Uploader bind:stageEmpty={stage_empty} poolId={Number.parseInt(id)} />
