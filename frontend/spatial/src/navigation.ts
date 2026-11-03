import type { Layout } from './model';

export type Camera = { cx: number; cy: number; zoom: number };
export type Bookmark = { id: string; time: number } | null;
type Snapshot = {
    pathId: string;
    step: number;
    overlays: Record<string, number>;
    viewId: string;
    mode: Mode;
    camera: Camera;
    media: Bookmark;
};
type Mode = 'guided' | 'exploring' | 'overview';
export type Navigation = Omit<Snapshot, 'camera' | 'media'> & {
    history: Snapshot[];
    anchor: Snapshot | null;
    /** Guided position to return to from a side trip along another path. */
    home: Snapshot | null;
    cameraRequest: number;
    restoreCamera: Camera | null;
    restoreMedia: Bookmark;
    notice: string;
};
export type Action = {
    type: 'next' | 'previous' | 'escape' | 'overview' | 'pan' | 'focus' | 'path' | 'step';
    id?: string;
    camera: Camera;
    media: Bookmark;
};

export function initial(layout: Layout): Navigation {
    const path = layout.paths[0];
    const state: Navigation = {
        pathId: path.id,
        step: 0,
        overlays: Object.fromEntries(layout.objects.map((o) => [o.id, 0])),
        viewId: path.steps[0].viewpoint_id,
        mode: 'guided',
        history: [],
        anchor: null,
        home: null,
        cameraRequest: 1,
        restoreCamera: null,
        restoreMedia: null,
        notice: '',
    };
    return enter(layout, state, 0, 1);
}
function enter(m: Layout, state: Navigation, index: number, direction: number): Navigation {
    const step = m.paths.find((p) => p.id === state.pathId)!.steps[index];
    const view = m.viewpoints.find((v) => v.id === step.viewpoint_id)!;
    const overlays = { ...state.overlays };
    if (view.target.kind === 'object') {
        const obj = m.objects.find(
            (o) => view.target.kind === 'object' && o.id === view.target.object_id,
        )!;
        const frame = m.frames.find((f) => f.id === obj.frame_id)!;
        overlays[obj.id] =
            step.overlay_policy === 'fixed'
                ? (step.overlay_index ?? 0)
                : direction > 0
                  ? 0
                  : frame.page_indices.length - 1;
    }
    return {
        ...state,
        step: index,
        viewId: step.viewpoint_id,
        overlays,
        mode: 'guided',
        cameraRequest: state.cameraRequest + 1,
        restoreCamera: null,
        restoreMedia: null,
        notice: '',
    };
}
/** The shortest other path holding a view that the current path lacks, e.g.
 * the backup path for a backup frame reached from the tour; null otherwise. */
export function sidePath(m: Layout, pathId: string, viewId: string): string | null {
    const holds = (p: Layout['paths'][number]) => p.steps.some((s) => s.viewpoint_id === viewId);
    if (holds(m.paths.find((p) => p.id === pathId)!)) return null;
    const others = m.paths.filter((p) => p.id !== pathId && holds(p));
    return others.length
        ? others.reduce((a, b) => (b.steps.length < a.steps.length ? b : a)).id
        : null;
}
export function navigate(m: Layout, state: Navigation, action: Action): Navigation {
    const snap = (): Snapshot => ({
        pathId: state.pathId,
        step: state.step,
        overlays: { ...state.overlays },
        viewId: state.viewId,
        mode: state.mode,
        camera: { ...action.camera },
        media: action.media ? { ...action.media } : null,
    });
    const restore = (
        saved: Snapshot,
        history: Snapshot[],
        anchor: Snapshot | null,
    ): Navigation => ({
        ...state,
        ...saved,
        overlays: { ...saved.overlays },
        history,
        anchor,
        cameraRequest: state.cameraRequest + 1,
        restoreCamera: saved.camera,
        restoreMedia: saved.media,
        notice: '',
    });
    if (action.type === 'path')
        return enter(
            m,
            { ...state, pathId: action.id!, history: [], anchor: null, home: null },
            0,
            1,
        );
    if (action.type === 'step') {
        // Jump to a guided step chosen in the overview; detours are discarded.
        const index = Number(action.id);
        const path = m.paths.find((p) => p.id === state.pathId)!;
        if (!Number.isInteger(index) || index < 0 || index >= path.steps.length) return state;
        return enter(m, { ...state, history: [], anchor: null }, index, 1);
    }
    if (
        action.type === 'escape' ||
        (state.mode === 'overview' && (action.type === 'next' || action.type === 'previous'))
    ) {
        const saved = state.history.at(-1);
        if (saved)
            return restore(
                saved,
                state.history.slice(0, -1),
                saved.mode === 'guided' ? null : state.anchor,
            );
        // Outermost Esc on a side trip goes back to where it left the path.
        return state.home && action.type === 'escape'
            ? { ...restore(state.home, [], null), home: null }
            : state;
    }
    if ((action.type === 'next' || action.type === 'previous') && state.mode === 'exploring') {
        // A frame off the current path continues along the path that holds it
        // (a side trip); Esc later returns to the guided position left behind.
        const holder = sidePath(m, state.pathId, state.viewId);
        if (holder) {
            const steps = m.paths.find((p) => p.id === holder)!.steps;
            const trip: Navigation = {
                ...state,
                pathId: holder,
                step: steps.findIndex((s) => s.viewpoint_id === state.viewId),
                mode: 'guided',
                history: [],
                anchor: null,
                home: state.home ?? state.anchor,
                cameraRequest: state.cameraRequest + 1,
                restoreCamera: null,
                restoreMedia: null,
            };
            return navigate(m, trip, action);
        }
        return state.anchor ? restore(state.anchor, [], null) : state;
    }
    if (action.type === 'overview' || action.type === 'focus' || action.type === 'pan') {
        if (
            (action.type === 'overview' && state.mode === 'overview') ||
            (action.type === 'pan' && state.mode === 'exploring')
        )
            return state;
        if (state.history.length >= 32)
            return { ...state, notice: 'Detour limit reached. Return before exploring further.' };
        const saved = snap();
        return {
            ...state,
            mode: action.type === 'overview' ? 'overview' : 'exploring',
            viewId: action.type === 'focus' ? action.id! : state.viewId,
            history: [...state.history, saved],
            anchor: state.mode === 'guided' ? saved : state.anchor,
            cameraRequest: state.cameraRequest + (action.type === 'pan' ? 0 : 1),
            restoreCamera: null,
            restoreMedia: null,
            notice: '',
        };
    }
    if (action.type === 'next' || action.type === 'previous') {
        const direction = action.type === 'next' ? 1 : -1;
        const path = m.paths.find((p) => p.id === state.pathId)!,
            step = path.steps[state.step];
        const view = m.viewpoints.find((v) => v.id === state.viewId)!;
        if (step.overlay_policy === 'all' && view.target.kind === 'object') {
            const obj = m.objects.find(
                (o) => view.target.kind === 'object' && o.id === view.target.object_id,
            )!;
            const frame = m.frames.find((f) => f.id === obj.frame_id)!;
            const index = state.overlays[obj.id] + direction;
            if (index >= 0 && index < frame.page_indices.length)
                return {
                    ...state,
                    overlays: { ...state.overlays, [obj.id]: index },
                    restoreMedia: null,
                };
        }
        const index = state.step + direction;
        if (index >= 0 && index < path.steps.length) return enter(m, state, index, direction);
    }
    return state;
}
