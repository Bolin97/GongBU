<script lang="ts">
    import axios from "axios";
    import { Progressbar } from "flowbite-svelte";
    import { onMount, onDestroy } from "svelte";
    import type CudaDeviceEntry from "../../class/CudaDeviceEntry";
    import { UPDATE_VIEW_INTERVAL } from "../store";
    export let showDevices: Array<string>;
    let devices: Array<CudaDeviceEntry> = [];
    let devices_updater: any;
    let device_mapper: any = {};
    onMount(async () => {
        async function update() {
            devices = (await axios.get(`/api/cuda`))
                .data as Array<CudaDeviceEntry>;
        }
        devices = (await axios.get(`/api/cuda`)).data as Array<CudaDeviceEntry>;
        device_mapper = devices.reduce((acc, cur) => {
            acc[cur.device_id] = cur;
            return acc;
        }, {});
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
          }) : showDevices.map(Number.parseInt) as deviceId}
        <div class="inline-block border-gray-200 shadow p-2 m-2 w-40">
            <div class="m-2 text-md">CUDA:{deviceId}</div>
            <hr class="m-1" />
            <div class="m-1">
                <div>GPU利用率：</div>
                <div>{device_mapper[deviceId].gpu_utilization.toFixed(1)}%</div>
                <Progressbar
                    progress={device_mapper[deviceId].gpu_utilization.toFixed(
                        1,
                    )}
                />
            </div>
            <hr class="m-1" />
            <div class="m-1">
                <div>显存利用率：</div>
                <div>
                    {device_mapper[deviceId].memory_utilization.toFixed(1)}%
                </div>
                <Progressbar
                    progress={device_mapper[
                        deviceId
                    ].memory_utilization.toFixed(1)}
                />
            </div>
        </div>
    {/each}
{/if}
