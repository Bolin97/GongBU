<script lang="ts">
    import { ParamType, type ParamEntry } from "../../components/params/Params";
    import ParamGroup from "../../components/params/ParamGroup.svelte";
    import axios from "axios";
	import { BACKEND } from "../../store";
    const naming_is_hard: Array<ParamEntry> = [{
		var_name: "bits_and_bytes",
		name: "开启量化",
		param_type: ParamType.bool,
		description: "量化的参数",
		constrains: []
	}];
    const param_entries: Array<ParamEntry> = [{
		var_name: "load_xbit",
		name: "量化bit",
		param_type: ParamType.radio,
		description: "量化的参数",
		constrains: [{ values: [4, 8] }]
	}];
    export let params: any;
</script>

<div>
    <ParamGroup title="开启量化" entries={naming_is_hard} bind:params={params}/>
    {#if params["bits_and_bytes"]}
        <ParamGroup title="量化参数" entries={param_entries} bind:params={params}/>
    {/if}
</div>