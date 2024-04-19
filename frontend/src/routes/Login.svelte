<script lang="ts">
  import axios from "axios";
  import { getContext } from "svelte";

  let identifier = "";
  let password = "";
  let logging_in = false;
  export let logged_in: boolean;
  async function login_handle() {
    try {
      const loginForm = new FormData();
      loginForm.append("username", identifier);
      loginForm.append("password", password);
      const response = await axios.post(`/api/token`, loginForm);
      logged_in = true;
      if (response.status == 200) {
        logged_in = true;
        axios.defaults.headers.common["Authorization"] =
          `Bearer ${response.data.access_token}`;
        localStorage.setItem("access_token", response.data.access_token);
        logging_in = false;
      } else {
        localStorage.removeItem("access_token");
        logging_in = false;
        alert(t("root.login_failed"));
      }
      logging_in = false;
    } catch (e) {
      logging_in = false;
      alert(t("root.login_failed"));
      localStorage.removeItem("access_token");
    }
  }

  const t: any = getContext("t");
  import { createEventDispatcher } from "svelte";
  const dispatch = createEventDispatcher();
</script>

{#if !logging_in}
  <div class="w-full p-2">
    <form class="w-full max-w-sm m-auto">
      <div class="mb-4">
        <label for="username" class="block text-gray-700 text-sm font-bold mb-2"
          >{t("root.username")}</label
        >
        <input
          type="text"
          id="username"
          bind:value={identifier}
          class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        />
      </div>
      <div class="mb-6">
        <label for="password" class="block text-gray-700 text-sm font-bold mb-2"
          >{t("root.password")}</label
        >
        <input
          type="password"
          id="password"
          bind:value={password}
          class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        />
      </div>
      <div class="flex items-center justify-between">
        <button
          type="button"
          on:click={(_) => {
            login_handle();
          }}
          class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          {t("root.login")}
        </button>
    </div>
    <div class="flex items-center justify-between mt-10">
        <button
        type="button"
        on:click={(_) => {
            dispatch("switch")
        }}
        class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
            {t("root.switch_to_signup")}
        </button>
    </div>
    </form>
  </div>
{:else}
<div class="relative w-screen h-screen">
    <div
        class="absolute top-1/2 left-1/2 animate-spin border-t-4 border-blue-500 rounded-full w-32 h-32"
    ></div>
</div>
{/if}
