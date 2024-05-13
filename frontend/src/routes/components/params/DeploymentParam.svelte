<script lang="ts">
  import {
    default_deployment_params,
    deployment_params,
    deployment_port,
    deployment_quantization_params,
  } from "./Params";
  import ParamGroup from "./ParamGroup.svelte";
  import type { DeploymentRequestParams } from "../../../class/DeploymentRequestParams";
  import { Accordion, AccordionItem } from "flowbite-svelte";
  import { t } from "../../../locales";
  export let deploymentParams: DeploymentRequestParams;
  export let hideParams: Array<string> = [];

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
  <ParamGroup
    title={t("components.deployment_params.title")}
    entries={deployment_params}
    hideParamNames={hideParams}
    bind:params
  />
  {#if params.bits_and_bytes}
    <Accordion class="m-4">
      <AccordionItem>
        <span slot="header">{t("components.deployment_params.subtitle")}</span>
        <ParamGroup
          title={t("components.deployment_params.subsubtitle")}
          entries={deployment_quantization_params}
          bind:params
        />
      </AccordionItem>
    </Accordion>
  {/if}
</div>
