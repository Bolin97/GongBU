<script lang="ts">
  import { onMount } from "svelte";
  import type EvalEntry from "../../class/EvalEntry";
  import ActionPageTitle from "../components/ActionPageTitle.svelte";
  import axios from "axios";
  import EvalCard from "./EvalCard.svelte";
  import { Button } from "flowbite-svelte";
  import { PlusOutline } from "flowbite-svelte-icons";
  let eval_entries: Array<EvalEntry> = [];
  onMount(async () => {
    eval_entries = (await axios.get("/api/eval")).data;
  });
</script>

<ActionPageTitle
  title="Evaluation"
  subtitle="Evaluate the performance of your models"
>
  <svelte:fragment slot="right">
    <div class="flex gap-2">
      <Button color="blue" href="/eval/tasks">
        <PlusOutline class="sm" />
        New Task
      </Button>
    </div>
  </svelte:fragment>
</ActionPageTitle>

<div class="grid grid-cols-3 gap-2">
  {#each eval_entries as eval_entry}
    <EvalCard evalEntry={eval_entry} />
  {/each}
</div>
