<script lang='ts'>
  import { Label, Input } from "flowbite-svelte";
  import { getContext } from "svelte";

  const t: any = getContext("t");

  export let name = "";
  export let description = "";
</script>

<div class="flex flex-col gap-2 m-8 mb-8">
  <div>
    <Label for="name" class="mb-2">{t("data.task.name")}</Label>
    <Input
      bind:value={name}
      type="text"
      id="first_name"
      placeholder={t("data.task.enter_name")}
    />
  </div>
  <div>
    <Label for="name" class="mb-2">{t("data.task.des")}</Label>
    <Input
      bind:value={description}
      type="text"
      id="first_name"
      placeholder={t("data.task.enter_des")}
    />
  </div>
</div>
