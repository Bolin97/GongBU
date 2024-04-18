<script lang="ts">
  import { onMount, setContext } from "svelte";
  import "../app.css";
  import Header from "./header.svelte";
  import Sidebar from "./sidebar.svelte";
  import axios from "axios";
  import getI18nStore from "../locales/index";

  const i18n = getI18nStore();

  const t = $i18n.t;
  setContext("i18n", i18n);
  setContext("t", t);

  let mounted = false;
  let logged_in = false;
  let loginCheckPromise;

  onMount(() => {
    if (localStorage.getItem("access_token")) {
      axios.defaults.headers.common["Authorization"] =
        `Bearer ${localStorage.getItem("access_token")}`;
      loginCheckPromise = axios
        .get(`/api/user/me`)
        .then((res) => {
          logged_in = true;
        })
        .catch((err) => {
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
  let logging_in = false;
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
    {:else if !logging_in}
      <div class="w-full p-2">
        <form class="w-full max-w-sm m-auto">
          <div class="mb-4">
            <label
              for="username"
              class="block text-gray-700 text-sm font-bold mb-2"
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
            <label
              for="password"
              class="block text-gray-700 text-sm font-bold mb-2"
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
              on:click={login_handle}
              class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              {t("root.login")}
            </button>
          </div>
        </form>
      </div>
    {:else}
      <div class="items-center">
        <div class="spinner"></div>
      </div>
    {/if}
  </div>
{/await}

<style>
  .spinner {
    border: 16px solid #f3f3f3;
    border-top: 16px solid #3498db;
    border-radius: 50%;
    width: 120px;
    height: 120px;
    animation: spin 2s linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
</style>
