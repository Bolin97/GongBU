<script lang="ts">
	import '../app.css';
	import { supportedLanguages } from '../locales';
    import { onMount } from 'svelte';
	import { getContext } from 'svelte';
	import { type i18n } from 'i18next';
    import type { Writable } from 'svelte/store';
    import { language } from './store';
    import { Button } from 'flowbite-svelte';

	const i18n: Writable<i18n> = getContext('i18n');
	let selectedLanguage = $language;
	$: {
		$language = selectedLanguage;
		$i18n.changeLanguage(selectedLanguage);
		// reload the page to take effect
		// location.reload();
	}

	const t = $i18n.t;
</script>

<div class="header w-full h-14 justify-between bg-gray-000 flex">
	<div class="left w-100 h-full text-center pt-2 px-2 flex">
		<img src="/logo.webp" alt="" width="70" />
		<span class="logo text-3xl pt-1 text-black-400 border-blue-400 font-bold"
			>&nbsp;&nbsp;{t("root.title")}</span
		>
		<!-- <span class="logo text-2xl pt-2 text-black-400 border-blue-400 text-center"
			>&nbsp;&nbsp;{t("root.subtitle")}</span
		> -->
	</div>
	<div class="right w-100 h-2/3 text-center pt-2 px-2 flex">
		<div>
			<select bind:value={selectedLanguage} class="form-select block w-full px-2 py-1 pr-8 rounded border border-gray-300 bg-white text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500">
				{#each supportedLanguages as lang (lang.value)}
					<option value={lang.value}>{lang.display}</option>
				{/each}
			</select>
		</div>
	</div>
</div>
<hr />
