<script lang="ts">
	import { Button } from "flowbite-svelte";
	import { PlusSolid } from "flowbite-svelte-icons";
	import type PoolEntry from "../../class/PoolEntry";
	import { onMount } from "svelte";
	import axios from "axios";
	import { BACKEND } from "../store";

	const col_names = ["ID", "名称", "创建时间", "条目数", "描述", ""];
	let pools = [] as Array<PoolEntry>;
	onMount(async () => {
		pools = (await axios.get(`${$BACKEND}/pool/`)).data as Array<PoolEntry>;
	});
</script>

<div class="pt-2 w-full">
	<span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;数据管理</span>
	<span class="text-1xl pt-2 text-black-400 text-center">&nbsp;&nbsp;数据池的查看与修改</span>
</div>
<hr class="pt-1" />
<div class="table w-full">
	<div class="w-full p-5">
		<Button href="/data/create_pool"><PlusSolid size="sm" />&nbsp;&nbsp;创建数据池</Button>
	</div>
	<div>
		<table class="table-auto border-collapse w-full h-full">
			<thead>
				<tr
					class="rounded-lg text-sm font-medium text-gray-700 text-left"
					style="font-size: 0.9674rem"
				>
					{#each col_names as name (name)}
						<th class="px-4 py-2 bg-gray-200" style="background-color:#f8f8f8"
							>{name}</th
						>
					{/each}
				</tr>
			</thead>
			<tbody class="text-sm font-normal text-gray-700">
				{#each pools as pool}
					<tr class="hover:bg-gray-100 rounded-lg">
						<td class="px-4 py-4">{pool.id}</td>
						<td class="px-4 py-4">{pool.name}</td>
						<td class="px-4 py-4">{pool.created_on}</td>
						<td class="px-4 py-4">{pool.size}</td>
						<td class="px-4 py-4">{pool.description}</td>
						<td class="px-4 py-4">
							<a
								href={`/data/details?pool_id=${pool.id}`}
								class="text-blue-600 hover:underline"
							>
								查看详情
							</a>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
