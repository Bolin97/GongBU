<script lang="ts">
  import type PoolEntry from "../../class/PoolEntry";
  import VisbilityButton from "../components/VisbilityButton.svelte";
  import { getContext } from "svelte";
  const t: any = getContext("t");
  export let pool: PoolEntry; // Replace 'any' with the actual type of 'pool' if available
</script>

<div
  class="p-2 bg-white rounded-md overflow-hidden border shadow-sm shadow-gray-300 border-grey-300"
>
  <div class="md:flex">
    <div class="p-2">
      <div class="tracking-wide text-sm text-blue-600 font-semibold">
        {pool.name}
      </div>
      <div>
        <p class="mt-2 text-gray-500">
          {pool.description}
          {#if pool.description.length == 0}
            <span class="italic text-gray-400">&nbsp;</span>
          {/if}
        </p>
      </div>
      <div class="mt-2">
        <span class="text-gray-900 font-bold">ID: </span>
        <span class="text-gray-600">{pool.id}</span>
      </div>
      <div class="mt-2">
        <span class="text-gray-900 font-bold">{t("data.detail.create_on")}</span>
        <span class="text-gray-600">{pool.created_on}</span>
      </div>
      <div class="mt-2">
        <span class="text-gray-900 font-bold">{t("data.detail.size")}</span>
        <span class="text-gray-600">{pool.size}</span>
      </div>
      <div class="mt-2">
        <a
          href={`/data/details?pool_id=${pool.id}`}
          class="text-blue-600 hover:underline">{t("data.detail.title")}</a
        >
        <a
          href={`/data/sift?pool_id=${pool.id}`}
          class="text-blue-600 hover:underline">{t("data.detail.sift")}</a
        >
        <VisbilityButton
          id={pool.id.toString()}
          asset="pool"
          interactStyle="link"
        />
      </div>
    </div>
  </div>
</div>
