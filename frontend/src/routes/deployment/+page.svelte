<script lang="ts">
    import axios from "axios";
    import { onMount } from "svelte";
    import DeploymentCard from "./DeploymentCard.svelte";
    import { Button } from "flowbite-svelte";
    import { PlusOutline } from "flowbite-svelte-icons";
    import ActionPageTitle from "../components/ActionPageTitle.svelte";

    let deploymemts = [];

    onMount(async () => {
        deploymemts = (await axios.get(`/api/deployment`)).data;
    });
</script>

<ActionPageTitle title="部署管理" subtitle="部署">
    <svelte:fragment slot="right">
        <Button href="/deployment/tasks">
            <PlusOutline/>
            部署
        </Button>
    </svelte:fragment>
</ActionPageTitle>
<div class="grid grid-cols-3 gap-2">
    {#each deploymemts as deployment}
        <DeploymentCard deployment={deployment}/>
    {/each}
</div>