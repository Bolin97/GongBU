<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { getContext } from "svelte";
  const t: any = getContext("t");
  let value = "";
  export let tags = [];
  // const dispatch = createEventDispatcher();
  $: tags = value
    .split(",")
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0);
</script>

<input
  type="text"
  bind:value
  class="w-full border-2 border-gray-300 rounded-md focus:outline-none focus:border-blue-300"
  placeholder={t("fault.search_placeholder")}
/>
