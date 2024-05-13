<script lang="ts">
  import axios from "axios";
  import { Progressbar } from "flowbite-svelte";
  import { onMount, onDestroy } from "svelte";
  import type CudaDeviceEntry from "../../class/CudaDeviceEntry";
  import { UPDATE_VIEW_INTERVAL } from "../store";
  import { getContext } from "svelte";
  const t: any = getContext("t");
  export let showDevices: Array<string>;
  let devices: Array<CudaDeviceEntry> = [];
  let devices_updater: any;
  let device_mapper: any = {};
  async function update() {
    try {
      devices = (await axios.get("/api/cuda")).data as Array<CudaDeviceEntry>;
      device_mapper = devices.reduce((acc, cur) => {
        acc[cur.device_id] = cur;
        return acc;
      }, {});
    }
    catch (e) {
      console.error(e);
    }
  }
  onMount(async () => {
    devices_updater = setInterval(update, UPDATE_VIEW_INTERVAL);
  });
  onDestroy(() => {
    clearInterval(devices_updater);
  });
</script>

{#if devices.length == 0}
  <div>loading</div>
{:else}
  {#each showDevices[0] == "auto" ? devices.map((each) => {
        return each.device_id;
      }) : showDevices.map((each) => {
        return Number.parseInt(each, 10);
      }) as deviceId}
    <div class="inline-block border-gray-200 shadow p-2 m-2 w-40">
      <div class="m-2 text-md">CUDA:{deviceId}</div>
      <hr class="m-1" />
      <div class="m-1">
        <div>{t("components.device.GPU_utilization")}</div>
        <div>{device_mapper[deviceId]?.gpu_utilization?.toFixed(1)}%</div>
        <Progressbar
          progress={device_mapper[deviceId]?.gpu_utilization?.toFixed(1)}
        />
      </div>
      <hr class="m-1" />
      <div class="m-1">
        <div>{t("components.device.memory_utilization")}</div>
        <div>
          {device_mapper[deviceId]?.memory_utilization?.toFixed(1)}%
        </div>
        <Progressbar
          progress={device_mapper[deviceId]?.memory_utilization?.toFixed(1)}
        />
      </div>
    </div>
  {/each}
{/if}
