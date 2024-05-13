<script lang="ts">
  import { Button } from "flowbite-svelte";
  import { PlusOutline } from "flowbite-svelte-icons";
  import type PoolEntry from "../../class/PoolEntry";
  import { onMount } from "svelte";
  import axios from "axios";
  import ActionPageTitle from "../components/ActionPageTitle.svelte";
  import PoolCard from "./PoolCard.svelte";

  import { getContext } from "svelte";
  const t: any = getContext("t");

  const col_names = ["ID", "名称", "创建时间", "条目数", "描述", ""];
  let pools = [] as Array<PoolEntry>;
  onMount(async () => {
    pools = (await axios.get(`/api/pool/`)).data as Array<PoolEntry>;
  });
</script>

<ActionPageTitle title={t("data.title")} subtitle={t("data.description")}>
  <svelte:fragment slot="right">
    <Button href="/data/create_pool">
      <PlusOutline />
      {t("data.create_pool")}
    </Button>
  </svelte:fragment>
</ActionPageTitle>
<div class="w-full grid grid-cols-3">
  {#each pools as pool}
    <div class="m-2">
      <PoolCard {pool} />
    </div>
  {/each}
</div>
