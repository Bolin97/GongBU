<script lang="ts">
  import { onMount, setContext } from "svelte";
  import "../app.css";
  import Header from "./header.svelte";
  import Sidebar from "./sidebar.svelte";
  import axios from "axios";
  import getI18nStore from "../locales/index";
  import Login from "./Login.svelte";
  import Signup from "./Signup.svelte";
  import { Button } from "flowbite-svelte";

  const i18n = getI18nStore();

  const t = $i18n.t;
  setContext("i18n", i18n);
  setContext("t", t);

  let logged_in = false;
  let loginCheckPromise: Promise<void>;

  onMount(() => {
    if (localStorage.getItem("access_token")) {
      axios.defaults.headers.common["Authorization"] =
        `Bearer ${localStorage.getItem("access_token")}`;
      loginCheckPromise = axios
        .get(`/api/user/me`)
        .then((res) => {
          logged_in = true;
          localStorage.setItem("identifier", res.data);
        })
        .catch((err) => {
          logged_in = false;
          localStorage.removeItem("access_token");
        });
    } else {
      loginCheckPromise = Promise.resolve();
    }
  });

  let switch_to_signup = false;
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
    {:else if switch_to_signup}
      <Signup
        on:switch={() => {
          switch_to_signup = false;
        }}
      />
    {:else}
      <Login
        bind:logged_in
        on:switch={() => {
          switch_to_signup = true;
        }}
      />
    {/if}
  </div>
{/await}
