<script lang="ts">
	import { Label, Checkbox, Input } from "flowbite-svelte";
	let currentDate = new Date();
	export let start: string;
	export let end: string;
	let startImmediately = false;
	let stopManually = false;

	$: if (startImmediately) {
		const zone = new Date().getTimezoneOffset() / 60;
		const local_time = new Date(currentDate).valueOf() - zone * 60 * 60 * 1000;
		const date = new Date(local_time)
		start = date.toISOString().slice(0, 16);
	}

	$: if (stopManually) {
		end = "2100-01-01T00:00:00";
	}
</script>

<div class="text-1xl m-2 my-4">请选择部署日期：</div>

<div class="grid grid-cols-2">
	<div class="m-8 p-4 my-4">
		<label for="dateInput" class="m-2 text-xl font-bold">选择开始日期：</label>
		<Checkbox class="m-2" bind:checked={startImmediately}>立即开始</Checkbox>
		<Input class={`${startImmediately ? "hidden": ""} m-2`} type="datetime-local" bind:value={start} disabled={startImmediately} />
	</div>
	<div class="m-8 p-4 my-4">
		<label for="dateInput" class="text-xl font-bold m-2">选择结束日期：</label>
		<Checkbox class="m-2" bind:checked={stopManually}>手动停止</Checkbox>
		<Input class={`${stopManually ? "hidden": ""} m-2`} type="datetime-local" bind:value={end} disabled={stopManually} />
	</div>
</div>