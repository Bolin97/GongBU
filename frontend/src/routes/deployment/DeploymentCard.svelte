<script lang="ts">
  import type Deployment from "../../class/Deployment";
  import { getContext } from "svelte";
  const t: any = getContext("t");
  export let deployment: Deployment;
</script>

<div
  class="p-2 bg-white rounded-md overflow-hidden border shadow-sm shadow-gray-300 border-grey-300"
>
  <div class="md:flex">
    <div class="p-2">
      <div class="tracking-wide text-sm text-blue-600 font-semibold">
        {deployment.name}
      </div>
      <p class="mt-2 text-gray-500">{deployment.description}</p>
      <div class="mt-2">
        <span class="text-gray-900 font-bold">State: </span>
        <span class="text-gray-600">
          {#if deployment.state == 0}
            {t("delpoyment.stopped")}
          {:else if deployment.state == 1}
            {t("delpoyment.starting")}
          {:else if deployment.state == 2}
            {t("delpoyment.running")}
          {/if}
        </span>
      </div>
      <div class="mt-2">
        <a
          href={`/deployment/details?deployment_id=${deployment.id}`}
          class="text-blue-600 hover:underline">详细信息</a
        >
      </div>
    </div>
  </div>
</div>
