<script lang="ts">
	export let indexes: Array<string>;

	const values = ["A", "B", "D", "F", "P", "R"]
	const presets = [
		{
			name: "Accuracy",
			value: "A",
			description: "预测正确的样本数/样本数总数"
		},
		{
			name: "Recall",
			value: "R",
			description: "基于召回率判断两个句子的相似程度"
		},
		{
			name: "F1-Score",
			value: "F",
			description: "Accuracy和Recall的调和指标"
		},
		{
			name: "Precision",
			value: "P",
			description: "评估生成文本中与参考文本匹配的内容所占的比例。"
		},
		{
			name: "BLEU",
			value: "B",
			description: "基于准确率判断两个句子的相似程度"
		},
		{
			name: "Distinct-2",
			value: "D",
			description: "反映文本生成的多样性"
		},
	];
</script>

<div class="flex flex-col bg-white p-6">
	{#each presets as index (index.value)}
		<label class="inline-flex items-center mt-3 border-b border-gray-200 pb-3">
			<input
				type="checkbox"
				class="form-checkbox h-5 w-5 text-gray-600 rounded checked:bg-blue-600 checked:border-blue-600"
				bind:group={indexes}
				value={index.value}
			/>
			<span class="ml-4 text-lg font-semibold text-gray-700">{index.name}</span>
			<span class="ml-2 text-gray-500 text-sm font-medium">{index.description}</span>
		</label>
	{/each}
</div>
