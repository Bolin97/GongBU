<script>
	import { onMount } from "svelte";
	import "../app.css";
	import Header from "./header.svelte";
	import Sidebar from "./sidebar.svelte";
	import axios from "axios";
	
	let mounted = false;
	let logged_in = false;
	// let logged_in = true;
	let loginCheckPromise;

	onMount(() => {
		if (localStorage.getItem("access_token")) {
			axios.defaults.headers.common["Authorization"] = `Bearer ${localStorage.getItem("access_token")}`;
			loginCheckPromise = axios.get(`/api/user/me`).then((res) => {
				logged_in = true;
			}).catch((err) => {
				logged_in = false;
				localStorage.removeItem("access_token");
			});
		} else {
			loginCheckPromise = Promise.resolve();
		}
		mounted = true;
	});

	let identifier = "";
	let password = "";
	async function login_handle() {
		const loginForm = new FormData();
		loginForm.append("username", identifier);
		loginForm.append("password", password);
		const response = await axios.post(`/api/token`, loginForm);
		if (response.status == 200) {
			logged_in = true;
			axios.defaults.headers.common["Authorization"] = `Bearer ${response.data.access_token}`;
			localStorage.setItem("access_token", response.data.access_token);
		}
		else {
			alert("登录失败！");
			localStorage.removeItem("access_token");
		}
	}
</script>

<Header />
{#await loginCheckPromise then}
<div class="w-full h-screen pt-2 flex flex-row">
	{#if logged_in}
		<div>
			<Sidebar />
		</div>
	{/if}
	{#if logged_in}
		<div class="w-full p-2">
			<slot />
		</div>
	{:else}
		<div class="w-full p-2">
			<form class="w-full max-w-sm m-auto">
				<div class="mb-4">
					<label for="username" class="block text-gray-700 text-sm font-bold mb-2">用户名</label>
					<input type="text" id="username" bind:value={identifier} class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />
				</div>
				<div class="mb-6">
					<label for="password" class="block text-gray-700 text-sm font-bold mb-2">密码</label>
					<input type="password" id="password" bind:value={password} class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />
				</div>
				<div class="flex items-center justify-between">
					<button type="button" on:click={login_handle} class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
						登录
					</button>
				</div>
			</form>
		</div>
	{/if}
</div>
{/await}