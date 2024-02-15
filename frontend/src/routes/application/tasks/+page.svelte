<script lang="ts">
    import axios from "axios";
    import { onMount } from "svelte";
    import { BACKEND } from "../../store";
	import { Button, Input, Label } from "flowbite-svelte";
	import { goto } from "$app/navigation";

    let apps: Array<{
        name: string;
        description: string;
        id: string;
    }> = [];
    onMount(async () => {
        const res = await axios.get(`${$BACKEND}/application`);
        apps = res.data;
    });
    let selected_app: string = "";
    let selected_deployment_id: number;

    enum DeploymentState {
		"出错" = -1,
		"准备中" = 0,
		"等待中" = 1,
		"可用" = 2,
		"结束" = 3,
	}

	let deployments: Array<DeploymentEntry> = [];
    onMount(async() => {
		deployments = (await axios.get(`${$BACKEND}/deploy_entry/`)).data as Array<DeploymentEntry>;
	})

    function select_deployment(id: number){
        selected_deployment_id = id;
    }

    function selectApp(id: string){
        selected_app = id;
    }

    let app_instance_name: string = "";
    let app_instance_description: string = "";
    let app_instance_port: string = "";

    async function submit() {
        axios.post(`${$BACKEND}/application`, {}, {
            params: {
                app_id: selected_app,
                name: app_instance_name,
                description: app_instance_description,
                deploy_id: selected_deployment_id,
                port: app_instance_port
            }
        });
        goto("/application");
    }
</script>
<div class="flex flex-col md:flex-row justify-between">
    <div class="w-full m-4 p-4">
        <p>选择一个应用:</p>
        <table class="table-auto border-collapse w-full">
            <thead>
                <tr
                    class="rounded-lg text-sm font-medium text-gray-700 text-left"
                    style="font-size: 0.9674rem"
                >
                    <th class="px-4 py-2 bg-gray-200" style="background-color:#f8f8f8">应用名</th>
                    <th class="px-4 py-2 bg-gray-200" style="background-color:#f8f8f8">应用描述</th>
                </tr>
            </thead>
            <tbody class="text-sm font-normal text-gray-700">
                {#each apps as app}
                    <tr class="rounded-lg {selected_app === app.id ? 'border-blue-600 border bg-blue-200' : ''}" on:click={() => selectApp(app.id)}>
                        <td class="px-4 py-4">{app.name}</td>
                        <td class="px-4 py-4">{app.description}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
        <p>选择一个已部署的模型:</p>
        <table class="table-auto border-collapse w-full">
            <thead>
                <tr
                    class="rounded-lg text-sm font-medium text-gray-700 text-left"
                    style="font-size: 0.9674rem"
                >
                    <th class="px-4 py-2 bg-gray-200" style="background-color:#f8f8f8">ID</th>
                    <th class="px-4 py-2 bg-gray-200" style="background-color:#f8f8f8">名称</th>
                    <th class="px-4 py-2 bg-gray-200" style="background-color:#f8f8f8">描述</th>
                </tr>
            </thead>
            <tbody class="text-sm font-normal text-gray-700">
                {#each deployments as deployment}
                    {#if deployment.state === 2}
                        <tr class="rounded-lg {selected_deployment_id === deployment.entry_id ? 'border-blue-600 border bg-blue-200' : ''}" on:click={() => select_deployment(deployment.entry_id)}>
                            <td class="px-4 py-4">{deployment.entry_id}</td>
                            <td class="px-4 py-4">{deployment.name}</td>
                            <td class="px-4 py-4">{deployment.description}</td>
                        </tr>
                    {/if}
                {/each}
            </tbody>
        </table>
    </div>
    <div class="w-full m-4 p-4">
        <div class="m-2 p-2">
            <Label>应用实例名</Label>
            <Input placeholder="在此输入应用实例名" bind:value={app_instance_name}/>
        </div>
        <div class="m-2 p-2">
            <Label>应用实例描述</Label>
        <Input placeholder="在此输入应用实例描述" bind:value={app_instance_description}/>
        </div>
        <div class="m-2 p-2">
            <Label>应用部署端口</Label>
            <Input placeholder="在此输入应用部署端口" bind:value={app_instance_port}/>
        </div>
    </div>
</div>

<div class="flex flex-row-reverse">
    <Button disabled={
        selected_deployment_id === undefined ||
        app_instance_port === ""
    } on:click={(_) => submit()}>
        创建应用实例
    </Button>
</div>