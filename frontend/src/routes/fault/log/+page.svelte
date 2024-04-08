<script lang="ts">
    import { page } from "$app/stores";
    import axios from "axios";
    import { onMount } from "svelte";

    const params = $page.url.searchParams;

    let fault_id = params.get("id");

    if (params.has("id")) {
        console.log("fault_id: ", fault_id);
    }

    let log_content = "";

    onMount(async () => {
        log_content = (await axios.get(`/api/fault/log/${fault_id}`)).data.log_content
    })
</script>

<div>
    <div class="p-4 bg-gray-200 rounded-md overflow-x-scroll w-3/4">
        <pre>{log_content}</pre>
    </div>
</div>