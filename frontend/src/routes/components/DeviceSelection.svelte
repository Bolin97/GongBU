<script lang="ts">
  import { Checkbox, Label, Progressbar, Radio, Toggle } from "flowbite-svelte";
  import type CudaDeviceEntry from "../../class/CudaDeviceEntry";
  import axios from "axios";
  import { UPDATE_VIEW_INTERVAL } from "../store";
  import { PlusOutline, CheckCircleOutline } from "flowbite-svelte-icons";
  import { getContext, onDestroy, onMount } from "svelte";
  const t: any = getContext("t");
  let devices: Array<CudaDeviceEntry> = [];
  export let updaterOn = true;


  let devices_updater: any;
  onMount(async () => {
    async function update() {
      if (updaterOn) {
        devices = (await axios.get(`/api/cuda`)).data as Array<CudaDeviceEntry>;
      }
    }
    devices = (await axios.get(`/api/cuda`)).data as Array<CudaDeviceEntry>;
    devices_updater = setInterval(update, UPDATE_VIEW_INTERVAL);
  });
  onDestroy(() => {
    clearInterval(devices_updater);
  });

  function clickHandle(id: number) {
    if (!auto_dist && useDevices != "auto") {
      if (useDevices.includes(id)) {
        useDevices = useDevices.filter((value) => value != id);
      } else {
        useDevices = [...useDevices, id];
      }
    }
  }
  let auto_dist = false;
  function toggle_auto() {
    if (useDevices == "auto") {
      useDevices = [];
    } else {
      useDevices = "auto";
    }
    auto_dist = !auto_dist;
  }
  export let useDevices: number[] | "auto" = [] as number[];
</script>

<div class="flex flex-col">
  <div class="flex flex-row justify-between">
    <span class="text-1xl m-2 mt-4">{t("finetune.device_params.auto")}</span>
    <Toggle
      on:change={(_) => {
        toggle_auto();
      }}
    />
  </div>
  <div class="text-1xl m-2 my-4 mt-2">{t("finetune.device_params.local_devices")}</div>
  <div class={`flex flex-col ${auto_dist ? "opacity-50" : ""}`}>
    <div class="m-2 flow-root">
      {#each devices as device}
        <button
          class={`m-2 p-2 inline-grid w-60 border ${
            !(useDevices == "auto" || useDevices.includes(device.device_id))
              ? "border-gray-200"
              : "border-blue-600"
          } rounded shadow-sm text-left gap-2`}
          on:click={(_) => clickHandle(device.device_id)}
        >
          <div class="m-2">
            {#if useDevices == "auto" || useDevices.includes(device.device_id)}
              <CheckCircleOutline size="sm" class="text-blue-600" />
            {:else}
              <PlusOutline size="sm" class="text-gray-400" />
            {/if}

            <div class="m-2 text-lg">CUDA:{device.device_id}</div>
            <div class="m-2">
              {t("components.device.GPU_utilization")}{device.gpu_utilization.toFixed(1)}%
              <Progressbar progress={device.gpu_utilization.toFixed(1)} />
            </div>
            <div class="m-2">
              {t("components.device.memory_utilization")}{device.memory_utilization.toFixed(1)}%
              <Progressbar progress={device.memory_utilization.toFixed(1)} />
            </div>
          </div>
        </button>
      {/each}
    </div>
  </div>
</div>
