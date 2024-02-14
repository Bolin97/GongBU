<script>
	import "../app.css";
	import { DarkMode } from "flowbite-svelte";
	import { page } from "$app/stores";
	import { Sidebar, SidebarGroup, SidebarItem, SidebarWrapper } from "flowbite-svelte";
	import {
		GridSolid,
		MailBoxSolid,
		UserSolid,
		ArrowRightToBracketSolid,
	} from "flowbite-svelte-icons";
	$: activeUrl = $page.url.pathname;
	let sidebar = ["模型广场", "应用广场", "微调管理", "数据管理", "部署管理", "模型下载", "设置"];
	let route = ["/modelsqure", "/application", "/finetune", "/data", "/deployment", "/download", "/config"];
	// let darkmodebtn =
	// 	'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 rounded-lg text-lg p-2.5 fixed right-4 top-2 z-50';

	const icons = [GridSolid, ArrowRightToBracketSolid, UserSolid, MailBoxSolid, MailBoxSolid, MailBoxSolid, MailBoxSolid];
</script>

<!-- <DarkMode btnClass={darkmodebtn} /> -->
<div class="flex flex-row">
	<div>
		<Sidebar {activeUrl}>
			<SidebarWrapper>
				<SidebarGroup>
					{#each sidebar as side, index}
						<SidebarItem label={side} href={route[index]}>
							<svelte:fragment slot="icon">
								<svelte:component
									this={icons[index]}
									class="w-5 h-5 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white"
								/>
							</svelte:fragment>
							<!-- <svelte:fragment slot="subtext">
								<span class="inline-flex justify-center items-center px-2 ml-3 text-sm font-medium text-gray-800 bg-gray-200 rounded-full dark:bg-gray-700 dark:text-gray-300"> Pro </span>
							</svelte:fragment> -->
						</SidebarItem>
					{/each}
				</SidebarGroup>
			</SidebarWrapper>
		</Sidebar>
	</div>
	<div class="m-2 p-2">
		<slot />
	</div>
</div>
