<script lang="ts">
    import DeviceSelection from "../../components/DeviceSelection.svelte";

	export let updaterOn = true;
	export let useDevices: number[] | "auto" = [] as number[];
</script>

<DeviceSelection bind:updaterOn={updaterOn} bind:useDevices={useDevices}/>