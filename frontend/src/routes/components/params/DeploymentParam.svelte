<script lang="ts">
    import { default_deployment_params, deployment_params, deployment_port, deployment_quantization_params } from "./Params";
    import ParamGroup from "./ParamGroup.svelte";
    import type { DeploymentRequestParams } from "../../../class/DeploymentRequestParams";
    import { Accordion, AccordionItem } from "flowbite-svelte";

    export let deploymentParams: DeploymentRequestParams;
    export let no_port: boolean = false;
    
    let params = default_deployment_params();

    $: {
        Object.keys(params).forEach((k) => {
            if (k in deploymentParams) {
                deploymentParams[k] = params[k];
            }
        });
        deploymentParams.load_4bit = params.load_xbit == 4;
        deploymentParams.load_8bit = params.load_xbit == 8;
    }
</script>

<div>
    <ParamGroup title="部署参数" entries={
        no_port ? deployment_params : deployment_params.concat(deployment_port)
    } bind:params={params} />
    {#if params.bits_and_bytes}
        <Accordion class="m-4">
            <AccordionItem>
                <span slot="header">量化参数</span>
                <ParamGroup title="部署量化参数" entries={deployment_quantization_params} bind:params={params} />
            </AccordionItem>
        </Accordion>
    {/if}
    
</div>