<script lang="ts">
  import { getContext, onDestroy, onMount } from "svelte";
  import type OpenllmEntry from "../../class/OpenllmEntry";
  import { MODEL_LIST, UPDATE_VIEW_INTERVAL } from "../store";
  import {
    Alert,
    Button,
    Input,
    Modal,
    Textarea,
    Toast,
  } from "flowbite-svelte";
  import {
    Table,
    TableBody,
    TableBodyCell,
    TableBodyRow,
    TableHead,
    TableHeadCell,
  } from "flowbite-svelte";
  import axios from "axios";
  import { CloseOutline } from "flowbite-svelte-icons";
  import { default_model_list } from "../shared";
  const t: any = getContext("t");
  let error_parsing = false;

  class ModelListItem {
    model_display_name: string;
    model_name: string;
    source: string;
    model_description: string;
    download_url: string;
    avatar_url: string | null | undefined;
  }

  let model_display_name: string = '';
  const source: string = 'git';
  let model_description: string = '';
  let download_url: string ='';
  let avatar_url: string =''
  let model_list: ModelListItem[] = default_model_list;

  async function add_model(){
    const parts = download_url.split('/');
    const extract_name = parts[parts.length - 1].replace('.git', '');
    const newModel: ModelListItem = {
        model_display_name: model_display_name,
        model_name: extract_name,
        source: source,
        model_description: model_description,
        download_url: download_url,
        avatar_url: avatar_url
    };
    model_list = [...model_list, newModel]
    model_display_name = '';
    model_description = '';
    download_url = '';
  }

  // $: {
  // error_parsing = false;
  // try {
  //   model_list = JSON.parse($MODEL_LIST);
  //   //check if every element in the model_list is a Model
  //   const valid = Object.keys(new ModelListItem()).every((key) => {
  //     return model_list.every((model) => {
  //       return key in model;
  //     });
  //   });
  //   if (!valid) {
  //     error_parsing = true;
  //   }
  // } catch (e) {
  //   error_parsing = true;
  // }
  // }

  let model_stored = [] as Array<OpenllmEntry>;
  async function refresh_model_stored() {
    model_stored = (await axios.get(`/api/openllm`))
      .data as Array<OpenllmEntry>;
  }
  let updater: any;
  onMount(async () => {
    refresh_model_stored();
    updater = setInterval(refresh_model_stored, UPDATE_VIEW_INTERVAL);
  });
  onDestroy(async () => {
    clearInterval(updater);
  });

  async function automatic_download(model: ModelListItem) {
    const response = await axios.post(`/api/openllm/download`, model);
    await refresh_model_stored();
  }

  async function write_only_info(model: ModelListItem) {
    const response = await axios.post(`/api/openllm/no_download`, model);
    await refresh_model_stored();
  }

  let delete_modal = false;
  let delete_modal_id = "";
  let delete_entry_modal = false;

  let alerts = [];
  function add_alert(title: string, body: string) {
    alerts = [...alerts, { title: title, body: body }];
  }
  function delete_alert(index: number) {
    alerts = alerts.filter((_, i) => i !== index);
  }
  function delete_all_alerts() {
    alerts = [];
  }
</script>

<div class="w-full">
  <Modal title={t("download.delete.title")} bind:open={delete_modal} autoclose>
    <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
      {t("download.delete.p1")}
    </p>
    <p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
      {t("download.delete.p2")}<span class="font-semibold"
        >{t("download.delete.p3")}</span
      >
    </p>
    <svelte:fragment slot="footer">
      <div class="w-full flex justify-end gap-2">
        <Button
          color="red"
          on:click={() => {
            axios.delete(`/api/openllm/${delete_modal_id}`);
            refresh_model_stored();
            delete_modal = false;
            delete_modal_id = "";
          }}>{t("download.delete.delete")}</Button
        >
        <Button color="alternative" on:click={() => (delete_modal = false)}
          >{t("download.delete.no")}</Button
        >
      </div>
    </svelte:fragment>
  </Modal>

  <Modal
    title={t("download.delete.title")}
    bind:open={delete_entry_modal}
    autoclose
  >
    <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
      {t("download.delete.p1")}
    </p>
    <p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
      {t("download.delete.p2")}<span class="font-semibold"
        >{t("download.delete.p3")}</span
      >
    </p>
    <p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
      {t("download.delete.p4")}<span class="font-semibold"
        >{t("download.delete.p5")}</span
      >{t("download.delete.p6")}
    </p>
    <svelte:fragment slot="footer">
      <div class="w-full flex justify-end gap-2">
        <Button
          color="red"
          on:click={() => {
            axios.delete(`/api/openllm/entry/${delete_modal_id}`);
            refresh_model_stored();
            delete_entry_modal = false;
            delete_modal_id = "";
          }}>{t("download.delete.delete")}</Button
        >
        <Button color="alternative" on:click={() => (delete_modal = false)}
          >{t("download.delete.no")}</Button
        >
      </div>
    </svelte:fragment>
  </Modal>

  <div class="pt-2 w-full">
    <span class="text-2xl pt-1 text-black-400 font-bold"
      >&nbsp;&nbsp;{t("download.title")}</span
    >
    <span class="text-1xl pt-2 text-black-400 text-center"
      >&nbsp;&nbsp;{t("download.description")}</span
    >
  </div>

  <hr class="pt-1" />

  {#if alerts.length > 1}
    <div class="w-full mx-2 my-4">
      <Alert>
        <button
          on:click={() => {
            delete_all_alerts();
          }}
          class="flex justify-between items-center"
        >
          <span class="font-medium hover:underline">{t("download.alert")}</span>
        </button>
      </Alert>
    </div>
  {/if}

  {#each alerts as alert, index}
    <div class="w-full mx-2 my-4">
      <Alert>
        <div class="flex justify-between items-center">
          <div>
            <div class="font-medium">{alert.title}</div>
            <div>{alert.body}</div>
          </div>
          <button
            on:click={() => {
              delete_alert(index);
            }}
          >
            <CloseOutline />
          </button>
        </div>
      </Alert>
    </div>
  {/each}

  <!-- <div class="m-2 p-2">
    <span class="my-2">{t("config.model_list")}</span>
    <Textarea rows="5" bind:value={$MODEL_LIST} />
  </div> -->
  <div class="text-lg font-bold m-2">
    <span>{t("download.add")}:</span>
  </div>
  <div class="border border-gray-300 rounded-md">
    <div class="flex flex-row mt-2">
      <div class="w-1/4 mx-2">
        <span class="font-semibold text-lg m-2"
          >{t("download.model_display_name")}：</span
        >
        <Input
          class=""
          bind:value={model_display_name}
        />
      </div>
      <div class="w-full mx-2">
        <span class="font-semibold text-lg m-2"
          >{t("download.model_description")}：</span
        >
        <Input
          class=""
          bind:value={model_description}
        />
      </div>
    </div>
    <div class="mt-2 mx-2">
      <span class="font-semibold text-lg m-2"
        >{t("download.download_url")}：</span
      >
      <Input
        class="my-2"
        bind:value={download_url}
      />
    </div>
    <div class="mt-2 mx-2">
      <span class="font-semibold text-lg m-2"
        >{t("download.avatar_url")}：</span
      >
      <Input
        class="my-2"
        bind:value={avatar_url}
      />
    </div>
    <div class="flex m-1 justify-center">
      <Button class="my-2" on:click={add_model}>
        {t("download.add_button")}
      </Button>
    </div>
  </div>

  {#if error_parsing}
    <div class="text-red-500">{t("download.list_alert")}</div>
  {:else}
    <div class="text-lg font-bold m-2">
      <span>{t("download.list")}</span>
    </div>
    <div class="table w-full my-2">
      <Table >
        <TableHead >
          <TableHeadCell>{t("download.table.model")}</TableHeadCell>
          <!-- <TableHeadCell>{t("download.table.des")}</TableHeadCell> -->
          <TableHeadCell>{t("download.table.website")}</TableHeadCell>
          <TableHeadCell>{t("download.table.options")}</TableHeadCell>
        </TableHead>
        <TableBody >
          {#each model_list as model}
            <TableBodyRow>
              <TableBodyCell>{model.model_name}</TableBodyCell>
              <!-- <TableBodyCell>{model.model_description}</TableBodyCell> -->
              <TableBodyCell>{model.download_url}</TableBodyCell>
              <TableBodyCell
                ><div class="flex flex-row">
                  <button
                    on:click={() => {
                      automatic_download(model);
                      add_alert(`${model.model_name}${t("download.p1")}`, ``);
                    }}
                    class="mx-2 text-blue-600 hover:underline"
                  >
                    {t("download.p2")}
                  </button>
                  <button
                    on:click={() => {
                      write_only_info(model);
                      add_alert(
                        `${model.model_name}${t("download.p1")}`,
                        `${model.download_url}${t("download.p3")}${model.model_name}${t("download.p4")}`,
                      );
                    }}
                    class="mx-2 text-blue-600 hover:underline"
                  >
                    {t("download.p5")}
                  </button>

                  <button
                    on:click={() => {
                      model_list = model_list.filter(
                        (item) => item.model_name !== model.model_name,
                      );
                      $MODEL_LIST = JSON.stringify(model_list);
                    }}
                    class="mx-2 text-red-600 hover:underline"
                  >
                    {t("download.delete_from_list")}
                  </button>
                
                </div></TableBodyCell
              >
            </TableBodyRow>
          {/each}
        </TableBody>
      </Table>
    </div>
  {/if}

  <div class="text-lg font-bold m-2">
    <span>{t("download.model")}</span>
  </div>

  <div class="table w-full my-2">
    <Table>
      <TableHead>
        <TableHeadCell>{t("download.table.model")}</TableHeadCell>
        <TableHeadCell>{t("download.table.des")}</TableHeadCell>
        <TableHeadCell>{t("download.table.website")}</TableHeadCell>
        <TableHeadCell>{t("download.table.options")}</TableHeadCell>
        <TableHeadCell>{t("download.table.state")}</TableHeadCell>
      </TableHead>
      <TableBody>
        {#each model_stored as model}
          <TableBodyRow>
            <TableBodyCell
              ><div class="w-20 whitespace-normal overflow-auto">
                {model.model_name}
              </div></TableBodyCell
            >
            <TableBodyCell
              ><div class="w-40 whitespace-normal overflow-auto">
                {model.model_description}
              </div></TableBodyCell
            >
            <TableBodyCell
              ><div class="whitespace-normal overflow-auto">
                {model.remote_path}
              </div></TableBodyCell
            >
            <TableBodyCell
              ><div class="whitespace-normal overflow-auto">
                {model.storage_state}
              </div></TableBodyCell
            >
            <TableBodyCell
              ><div class="flex flex-row">
                <button
                  class="mx-2 text-red-600 hover:underline"
                  on:click={() => {
                    delete_modal_id = model.id;
                    delete_modal = true;
                  }}
                >
                  {t("download.delete.p7")}
                </button>
                <button
                  class="mx-2 text-red-600 hover:underline"
                  on:click={() => {
                    delete_modal_id = model.id;
                    delete_entry_modal = true;
                  }}
                >
                  {t("download.delete.p8")}
                </button>
              </div></TableBodyCell
            >
          </TableBodyRow>
        {/each}
      </TableBody>
    </Table>
  </div>
</div>
