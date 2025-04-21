<script lang="ts">
  import { page } from "$app/stores";
  import { onMount, setContext, onDestroy } from "svelte";
  import "../app.css";
  import Header from "./Header.svelte";
  import Sidebar from "./Sidebar.svelte";
  import axios from "axios";
  import getI18nStore from "../locales/index";
  import Login from "./Login.svelte";
  import Signup from "./Signup.svelte";
  import { Button } from "flowbite-svelte";
  import { goto } from "$app/navigation";
  const i18n = getI18nStore();

  const t = $i18n.t;
  setContext("i18n", i18n);
  setContext("t", t);

  let logged_in = false;
  let loaded = false;
  let showFloatingButton = false; // 新增变量来控制是否显示悬浮按钮
  // 在根 layout.svelte 中监听 $page.url.pathname 是否是 /community，自动设置 community
  let community = false;
  const unsubscribe = page.subscribe(($page) => {
    if ($page.url.pathname.startsWith("/api/")) {
      showFloatingButton = true;
    } else {
      showFloatingButton = false;
    }
    if ($page.url.pathname.startsWith("/community")) {
      community = true;
    } else {
      community = false;
    }
  });
  onDestroy(() => unsubscribe());

  onMount(() => {
    if (localStorage.getItem("access_token")) {
      axios.defaults.headers.common["Authorization"] =
        `Bearer ${localStorage.getItem("access_token")}`;
      axios
        .get(`/api/user/me`)
        .then((res) => {
          logged_in = true;
          localStorage.setItem("identifier", res.data);
        })
        .catch((err) => {
          logged_in = false;
          localStorage.removeItem("access_token");
        });
    }
    loaded = true;
  });

  let switch_to_signup = false;
</script>
<style>
  /* 悬浮按钮样式 */
  .floating-btn {
      position: fixed;
      right: 20px;
      bottom: 20px;
      width: 56px;
      height: 56px;
      background: #3b82f6;
      border-radius: 50%;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
      z-index: 999;
  }

  .floating-btn:hover {
      background: #2563eb;
      transform: scale(1.1);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }

  .floating-btn i {
      color: white;
      font-size: 24px;
  }
</style>

{#if !community}
<Header />
{/if}
{#if loaded}
  <div class="w-full h-screen pt-2 flex flex-row">
    {#if logged_in && !community}
      <div>
        <Sidebar />
      </div>
    {/if}
    {#if logged_in}
      <div class="w-full h-full">
        <slot />
      </div>
      {#if showFloatingButton}
        <button class="floating-btn" id="communityBtn" on:click={() => goto("/community")}>
          <i class="material-icons">forum</i>
        </button>
      {/if}
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
{/if}
