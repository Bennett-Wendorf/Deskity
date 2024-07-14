export interface BaseWidgetType {
    type: string;
    props: any;
}

export interface HSplitLayout extends BaseWidgetType {
    props: {
        left: BaseWidgetType;
        right: BaseWidgetType;
    };
}

export function isHsplit(widget: BaseWidgetType): widget is HSplitLayout {
    return widget.type === 'hsplit';
}

export interface VSplitLayout extends BaseWidgetType {
    props: {
        top: BaseWidgetType;
        bottom: BaseWidgetType;
    }
}

export function isVsplit(widget: BaseWidgetType): widget is VSplitLayout {
    return widget.type === 'vsplit';
}