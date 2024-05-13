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
      <div>
        <p class="mt-2 text-gray-500">{deployment.description}</p>
      </div>
      <div class="mt-2">
        <span class="text-gray-900 font-bold">{t("deployment.detail.state")}</span>
        <span class="text-gray-600">
          {#if deployment.state == 0}
            {t("deployment.stopped")}
          {:else if deployment.state == 1}
            {t("deployment.starting")}
          {:else if deployment.state == 2}
            {t("deployment.running")}
          {:else if deployment.state == -1}
            {t("deployment.error")}
          {/if}
        </span>
      </div>
      <div class="mt-2">
        <a
          href={`/deployment/details?deployment_id=${deployment.id}`}
          class="text-blue-600 hover:underline">{t("deployment.detail.title")}</a
        >
      </div>
    </div>
  </div>
</div>
