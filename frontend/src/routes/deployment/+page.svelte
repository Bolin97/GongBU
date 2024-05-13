<script lang="ts">
  import axios from "axios";
  import { getContext, onMount } from "svelte";
  import DeploymentCard from "./DeploymentCard.svelte";
  import { Button } from "flowbite-svelte";
  import { PlusOutline } from "flowbite-svelte-icons";
  import ActionPageTitle from "../components/ActionPageTitle.svelte";

  let deploymemts = [];
  const t: any = getContext("t");

  onMount(async () => {
    deploymemts = (await axios.get(`/api/deployment`)).data;
  });
</script>

<ActionPageTitle title={t("deployment.title")} subtitle={t("deployment.description")}>
  <svelte:fragment slot="right">
    <Button href="/deployment/tasks">
      <PlusOutline />
      {t("deployment.task.button")}
    </Button>
  </svelte:fragment>
</ActionPageTitle>
<div class="grid grid-cols-3 gap-2">
  {#each deploymemts as deployment}
    <DeploymentCard {deployment} />
  {/each}
</div>
