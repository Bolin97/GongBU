<script lang="ts">
  import { page } from "$app/stores";
  import axios from "axios";
  import { getContext, onMount } from "svelte";
  import GoBack from "../../components/GoBack.svelte";
  import { Button } from "flowbite-svelte";

  const params = $page.url.searchParams;

  let fault_id = params.get("id");

  if (params.has("id")) {
    console.log("fault_id: ", fault_id);
  }

  let log_content = "";
  let downloadUrl = "";

  onMount(async () => {
    log_content = (await axios.get(`/api/fault/log/${fault_id}`)).data
      .log_content;
    const blob = new Blob([log_content], { type: "text/plain" });
    downloadUrl = URL.createObjectURL(blob);
  });

  const t: any = getContext("t");
</script>

<div class="my-2 flex items-start flex-wrap">
  <div class="mr-2">
    <GoBack returnTo="/fault" />
  </div>
  <div class="mx-2">
    <Button>
      <a href={downloadUrl} download={`log_${fault_id}.txt`}>
        {t("fault.download_logs")}
      </a>
    </Button>
  </div>
</div>

<div>
  <div class="p-4 bg-gray-200 rounded-md overflow-x-scroll w-3/4">
    <pre>{log_content}</pre>
  </div>
</div>
