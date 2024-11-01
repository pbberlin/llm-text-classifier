<script lang="ts">
    import { onMount } from 'svelte';

    export let prompt: string;
    export let models: string[];

    let results = [];

    // Function to fetch data for a single model
    async function fetchModelResult(model: string) {
        try {
            const response = await fetch('/chatCompletionJsonH', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ beliefStatement: prompt, speech: model })
            });
            const result = await response.json();
            return { ident: model, ...result };
        } catch (error) {
            return { ident: model, error: error.message };
        }
    }

    // Fetch results for each model
    onMount(async () => {
        results = await Promise.all(models.map(fetchModelResult));
    });
</script>

<div>
    {#each results as { ident, jsonResult, error }}
        <div>
            <h4>{ident}</h4>
            {#if error}
                <p>Error: {error}</p>
            {:else}
                <p>Agreement: {jsonResult.agreement}</p>
                <p>Alignment: {jsonResult.alignment}</p>
                <p>Textual Analysis: {jsonResult.textual_analysis}</p>
            {/if}
        </div>
    {/each}
</div>
