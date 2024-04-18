<script>
  import { Label, Input } from "flowbite-svelte";

  export let name = "";
  export let description = "";
</script>

<div class="flex flex-col gap-2 m-8 mb-8">
  <div>
    <Label for="name" class="mb-2">数据池名称</Label>
    <Input
      bind:value={name}
      type="text"
      id="first_name"
      placeholder="请输入数据池名称"
    />
  </div>
  <div>
    <Label for="name" class="mb-2">数据池描述</Label>
    <Input
      bind:value={description}
      type="text"
      id="first_name"
      placeholder="请输入数据池描述"
    />
  </div>
</div>
