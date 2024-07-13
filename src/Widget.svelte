<script lang="ts">
    import HorizontalSplit from "./components/Layout/HorizontalSplit.svelte";
    import VerticalSplit from "./components/Layout/VerticalSplit.svelte";
    import { isHsplit, isVsplit, type BaseWidgetType } from "./utils/layout_types";
    import { getWidget } from "./utils/widgetFactory";

    export let backingData: BaseWidgetType;
</script>

{#if backingData}
    {#if isHsplit(backingData)}
        <HorizontalSplit>
            <svelte:self backingData={backingData.props.left} slot="left" />
            <svelte:self backingData={backingData.props.right} slot="right" />
        </HorizontalSplit>
    {:else if isVsplit(backingData)}
        <VerticalSplit>
            <svelte:self backingData={backingData.props.top} slot="top" />
            <svelte:self backingData={backingData.props.bottom} slot="bottom" />
        </VerticalSplit>
    {:else}
        <svelte:component this={getWidget(backingData.type)} {...backingData.props} />
    {/if}
{/if}