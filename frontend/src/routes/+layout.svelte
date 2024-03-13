<script>
	import "../app.css";
	import Header from "./header.svelte";
	import Sidebar from "./sidebar.svelte";
</script>

<Header />
<div class="w-full h-screen pt-2 flex flex-row">
	<div>
		<Sidebar />
	</div>
	<div class="w-full p-2">
		<slot />
	</div>
</div>
