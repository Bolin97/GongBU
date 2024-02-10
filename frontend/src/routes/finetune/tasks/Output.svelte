<script lang="ts">
	import { Label, Input } from "flowbite-svelte";
	import ServerFile from "./serverfile/ServerFile.svelte";
	import { DEFAULT_MODEL_OUTPUT } from "../../store";

	export let dirArr: Array<string> = $DEFAULT_MODEL_OUTPUT.split("/").filter((x) => x != "");
</script>

<div>
	<div class="text-2xl m-2 my-4">
		<Label for="output" class="mb-2">输出路径</Label>
	</div>

	<div class="m-4 rounded p-2">
		<ServerFile bind:dir={dirArr} />
	</div>
</div>
