<script lang="ts">
  export let poolId: number;
  import axios from "axios";
  import {
    Accordion,
    AccordionItem,
    Radio,
    Button,
    Hr,
    Table,
    TableHead,
    TableHeadCell,
    TableBody,
    TableBodyCell,
    Input,
    Dropdown,
  } from "flowbite-svelte";
  // const dataset_types = ['微调数据', 'elastic', 'milvus', 'neo4j'];
  // let data_type: number = 0;

  import { Label } from "flowbite-svelte";
  import { Dropzone } from "flowbite-svelte";
  import { UPDATE_VIEW_INTERVAL } from "../store";
  import DatasetTable from "./DatasetTable.svelte";
  import type DatasetEntry from "../../class/DatasetEntry";
  import { onDestroy, onMount } from "svelte";

  interface SubmissionEntry {
    name: string;
    description: string;
    file: File;
  }

  let submissions: Array<SubmissionEntry> = [];
  let loadingProgress = 1;
  let loadingTotal = 0;
  // $: stageEmpty = submissions.length != 0;

  function file_to_default_entry(file: File): SubmissionEntry {
    return {
      name: file.name.split(".")[0],
      description: `Uploaded file ${file.name}`,
      file: file,
    };
  }

  function files_to_default_entries(files: Array<File>) {
    return files.map((file) => {
      return file_to_default_entry(file);
    });
  }

  function drop_handle(event: DragEvent) {
    event.preventDefault();
    const files_in_items = Array.from(event.dataTransfer.items)
      .filter((item) => {
        return item.kind === "file";
      })
      .map((item) => {
        return item.getAsFile();
      });
    const files_in_files = Array.from(event.dataTransfer.files);
    const files = Array.from(new Set([...files_in_items, ...files_in_files]));
    submissions = [...submissions, ...files_to_default_entries(files)];
  }

  function change_handle(event: any) {
    event.preventDefault();
    const files: Array<File> = Array.from(event.target.files);
    submissions = [...submissions, ...files_to_default_entries(files)];
  }

  const stage_table_heads = ["文件名", "数据集名", "描述", "操作"];

  let loading = false;

  async function submit_handle() {
    loadingTotal = submissions.length;
    loadingProgress = 0;
    loading = true;
    for (var i = 0; i < submissions.length; i++) {
      const form = new FormData();
      const entry = submissions[i];
      form.append("file", entry.file);
      await axios.post(`/api/dataset`, form, {
        params: {
          name: entry.name,
          description: entry.description,
          pool_id: poolId,
          kind: data_type,
        },
      });
      loadingProgress += 1;
    }
    // submissions.forEach(async (entry) => {
    // 	const form = new FormData();
    // 	form.append("file", entry.file);
    // 	await axios.post(`/api/dataset/`, form, {
    // 		params: {
    // 			name: entry.name,
    // 			description: entry.description,
    // 			pool_id: poolId,
    // 			kind: data_type,
    // 		}
    // 	});
    // 	loadingProgress += 1;
    // })

    // await Promise.all(
    // 	submissions.map((entry) => {
    // 		const form = new FormData();
    // 		form.append("file", entry.file);
    // 		return axios.post(`/api/dataset/`, form, {
    // 			params: {
    // 				name: entry.name,
    // 				description: entry.description,
    // 				pool_id: poolId,
    // 				kind: data_type,
    // 			}
    // 		});
    // 	})
    // );
    await fetch_dataset_entries();
    submissions = [];
    loading = false;
  }
  let fetch_entries_updater: number;
  onMount(async () => {
    fetch_entries_updater = setInterval(
      fetch_dataset_entries,
      UPDATE_VIEW_INTERVAL,
    );
  });
  onDestroy(async () => {
    clearInterval(fetch_entries_updater);
  });
  let entries: Array<DatasetEntry> = [];
  export let stageEmpty = submissions.length == 0;
  $: stageEmpty = submissions.length == 0;

  async function fetch_dataset_entries() {
    entries = (await axios.get(`/api/dataset_entry/by_pool/${poolId}`)).data;
  }

  onMount(async () => {
    await fetch_dataset_entries();
  });

  async function remove_from_stage_handle(i: number) {
    submissions = submissions.filter((_, index) => {
      return index != i;
    });
  }
  const dataset_types = ["instruct-input(optional)-output", "input-output"];
  let data_type: number = 0;
</script>

{#if !loading}
  <div class="w-full">
    <div class="m-2">
      <Accordion>
        <AccordionItem open={true}>
          <span slot="header">数据池详细信息</span>
          <DatasetTable
            datasetEntries={entries}
            on:modified={async (_) => {
              await fetch_dataset_entries();
            }}
          />
        </AccordionItem>
      </Accordion>
    </div>
    <div>
      <div class="m-2">
        <Accordion>
          <AccordionItem open={true}>
            <span slot="header">暂存区</span>
            <div class="flex flex-row justify-end items-center text-black">
              <div>以</div>
              <div class="flex flex-row gap-2 m-4 my-8">
                {#each dataset_types as type, index}
                  <Radio bind:group={data_type} name="method" value={index}
                    ><p class="text-lg">{type}</p></Radio
                  >
                {/each}
              </div>
              <span>格式</span>
              <div>
                <Button
                  class="m-2 text-center"
                  on:click={(_) => submit_handle()}>提交暂存区的所有文件</Button
                >
              </div>
            </div>
            <div class="border border-gray-200 text-gray-800 rounded p-2 m-2">
              {#if submissions.length == 0}
                <div class="w-full text-center">
                  <span>暂存区内无已上传文件</span>
                </div>
              {:else}
                <Table striped={true}>
                  <TableHead>
                    {#each stage_table_heads as head}
                      <TableHeadCell>{head}</TableHeadCell>
                    {/each}
                  </TableHead>
                  {#each submissions as entry, index (index)}
                    <TableBody>
                      <TableBodyCell>
                        {entry.file.name}
                      </TableBodyCell>
                      <TableBodyCell>
                        <Input
                          placeholder="输入数据集名称"
                          bind:value={entry.name}
                        />
                      </TableBodyCell>
                      <TableBodyCell>
                        <Input
                          placeholder="输入数据集描述"
                          bind:value={entry.description}
                        />
                      </TableBodyCell>
                      <TableBodyCell>
                        <button
                          on:click={(_) => remove_from_stage_handle(index)}
                          class="text-blue-500 hover:text-blue-800 hover:underline"
                          >移出暂存区</button
                        >
                      </TableBodyCell>
                    </TableBody>
                  {/each}
                </Table>
              {/if}
            </div>
          </AccordionItem>
        </Accordion>
      </div>

      <div class="m-4">
        <Dropzone
          id="dropzone"
          on:drop={drop_handle}
          on:dragover={(event) => {
            event.preventDefault();
          }}
          on:change={change_handle}
        >
          <svg
            aria-hidden="true"
            class="mb-3 w-10 h-10 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
            ><path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            /></svg
          >
          <p class="mb-2 text-sm text-gray-500 dark:text-gray-400">
            <span class="font-semibold">点击</span>或<span class="font-semibold"
              >拖拽</span
            >以上传文件至暂存区
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400">JSON</p>
        </Dropzone>
      </div>
    </div>
  </div>
{:else}
  <div>
    {loadingProgress} out of {loadingTotal}
  </div>
{/if}
