<script lang='ts'>
  import "../app.css";
  import { DarkMode } from "flowbite-svelte";
  import { page } from "$app/stores";
  import {
    Sidebar,
    SidebarGroup,
    SidebarItem,
    SidebarWrapper,
  } from "flowbite-svelte";
  import { getContext } from "svelte";
  import { MailBoxOutline } from "flowbite-svelte-icons";
  $: activeUrl = $page.url.pathname;
  const t: any = getContext("t");
  // let sidebar = t("sidebar")
  let sidebar = [
    t("sidebar.model_squre"),
    t("sidebar.finetune_manager"),
    t("sidebar.data_manager"),
    t("sidebar.model_eval"),
    t("sidebar.deployment_manager"),
    t("sidebar.model_download"),
    t("sidebar.error_log"),
    t("sidebar.settings"),
  ];
  let route = [
    "/model",
    "/finetune",
    "/data",
    "/eval",
    "/deployment",
    "/download",
    "/fault",
    "/config",
  ];
  // let darkmodebtn =
  // 	'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 rounded-lg text-lg p-2.5 fixed right-4 top-2 z-50';

  const icons = [
    MailBoxOutline,
    MailBoxOutline,
    MailBoxOutline,
    MailBoxOutline,
    MailBoxOutline,
    MailBoxOutline,
    MailBoxOutline,
    MailBoxOutline,
    MailBoxOutline,
    MailBoxOutline,
    MailBoxOutline,
    MailBoxOutline,
  ];
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
