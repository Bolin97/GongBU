<script lang="ts">
  import axios from "axios";
  import { createEventDispatcher, getContext, onMount } from "svelte";

  let identifier = "";
  let password = "";
  let signUpToken = "";
  let signingUp = false;
  let signUpTokenRequired = true;
  const t: any = getContext("t");
  const dispatch = createEventDispatcher();

  onMount(async () => {
    const response = await axios.get(`/api/user/signup-token-required`);
    signUpTokenRequired = response.data;
  });

  async function signUpHandle() {
    try {
      signingUp = true;
      const signUpForm = new FormData();
      signUpForm.append("identifier", identifier);
      signUpForm.append("password", password);
      if (signUpTokenRequired) {
        signUpForm.append("sign_up_token", signUpToken);
      }
      const response = await axios.post(`/api/user`, signUpForm);
      if (response.data) {
        signingUp = false;
        alert(t("root.signup_successful"));
      } else {
        signingUp = false;
        alert(t("root.signup_failed"));
      }
    } catch (e) {
      signingUp = false;
      alert(t("root.signup_failed"));
    }
  }
</script>

{#if !signingUp}
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
      {#if signUpTokenRequired}
        <div class="mb-6">
          <label
            for="signUpToken"
            class="block text-gray-700 text-sm font-bold mb-2"
            >{t("root.sign_up_token")}</label
          >
          <input
            type="text"
            id="signUpToken"
            bind:value={signUpToken}
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          />
        </div>
      {/if}
      <div class="flex items-center justify-between">
        <button
          type="button"
          on:click={(_) => {
            signUpHandle();
          }}
          class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          {t("root.sign_up")}
        </button>
      </div>
      <div class="flex items-center justify-between mt-10">
        <button
          type="button"
          on:click={(_) => {
            dispatch("switch");
          }}
          class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          {t("root.switch_to_login")}
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
