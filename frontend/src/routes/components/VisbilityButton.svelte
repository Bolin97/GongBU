<script lang="ts">
  import { Button } from "flowbite-svelte";
  import axios from "axios";
  import { getContext, onMount } from "svelte";

  export let id: string;
  export let asset: "dataset" | "openllm" | "adapter" | "pool";
  export let interactStyle: "button" | "link" = "button";

  let owns = false;
  let publicized = false;
  let loaded = false;

  async function checkOwnershipAndPublicity() {
    owns = (await axios.get(`/api/visibility/${asset}/owns/${id}`)).data;
    if (!owns) return;
    publicized = (await axios.get(`/api/visibility/${asset}/public/${id}`))
      .data;
  }

  onMount(async () => {
    await checkOwnershipAndPublicity();
    loaded = true;
  });

  async function toggleVisibility() {
    await axios.put(
      `/api/visibility/${asset}/public/${id}`,
      {},
      {
        params: {
          public: !publicized,
        },
      },
    );
    publicized = !publicized;
  }

  const t: any = getContext("t");

  $: should_show = loaded && owns;
</script>

{#if interactStyle == "button"}
  <Button
    on:click={toggleVisibility}
    class={`${should_show ? "" : "invisible"}`}
  >
    {publicized
      ? t("components.visibility_button.hide")
      : t("components.visibility_button.publicize")}
  </Button>
{:else if interactStyle == "link"}
  <button
    on:click={toggleVisibility}
    class={`text-blue-500 hover:underline ${should_show ? "" : "invisible"}`}
  >
    {publicized
      ? t("components.visibility_button.hide")
      : t("components.visibility_button.publicize")}
  </button>
{/if}
