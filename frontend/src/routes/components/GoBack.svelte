<script lang="ts">
  import { goto } from "$app/navigation";

  import { Button } from "flowbite-svelte";
  import { AngleLeftOutline } from "flowbite-svelte-icons";
  import { getContext } from "svelte";
  export let returnTo: string;

  const t: any = getContext("t");
</script>

<Button
  class={$$props.class}
  on:click={(_) => {
    goto(returnTo);
  }}
>
  <AngleLeftOutline size="sm" />{t("components.go_back")}
</Button>
