<script lang="ts">
  import { Button } from "flowbite-svelte";
  export let link: string;
  export let avaliable: boolean;

  let iframe: HTMLIFrameElement;
    import { getContext } from "svelte";
  const t: any = getContext("t");
</script>

{#if avaliable}
  <iframe bind:this={iframe} title={link} src={link} class="w-full h-[75vh]"
  ></iframe>
{:else}
  <div class="text-center">
    <p>{t("deployment.detail.p1")}</p>
  </div>
{/if}
