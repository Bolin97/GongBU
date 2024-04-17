<script lang="ts">
    import type PoolEntry from "../../class/PoolEntry";

    export let pool: PoolEntry; // Replace 'any' with the actual type of 'pool' if available
</script>

<div class="p-2 bg-white rounded-md overflow-hidden border shadow-sm shadow-gray-300 border-grey-300">
    <div class="md:flex">
        <div class="p-2">
            <div class="tracking-wide text-sm text-blue-600 font-semibold">{pool.name}</div>
            <p class="mt-2 text-gray-500">{pool.description}</p>
            <div class="mt-2">
                <span class="text-gray-900 font-bold">ID: </span>
                <span class="text-gray-600">{pool.id}</span>
            </div>
            <div class="mt-2">
                <span class="text-gray-900 font-bold">Created On: </span>
                <span class="text-gray-600">{pool.created_on}</span>
            </div>
            <div class="mt-2">
                <span class="text-gray-900 font-bold">Size: </span>
                <span class="text-gray-600">{pool.size}</span>
            </div>
            <div class="mt-2">
                <a href={`/data/details?pool_id=${pool.id}`} class="text-blue-600 hover:underline">查看详情</a>
            </div>
        </div>
    </div>
</div>