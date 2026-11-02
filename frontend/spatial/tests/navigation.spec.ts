import { test, expect } from '@playwright/test';
import { initial, navigate } from '../src/navigation';
import type { Layout } from '../src/model';

const layout: Layout = {
    format: 'beamerpkg-spatial',
    schema_version: 1,
    source: { pdf_path: 'talk.pdf', pdf_sha256: 'a'.repeat(64) },
    frames: [
        { id: 'f', page_indices: [0, 1, 2] },
        { id: 'g', page_indices: [3] },
    ],
    objects: [
        { id: 'a', frame_id: 'f', x: 0, y: 0, width: 960 },
        { id: 'duplicate', frame_id: 'f', x: 1120, y: 0, width: 960 },
        { id: 'b', frame_id: 'g', x: 2240, y: 0, width: 960 },
    ],
    viewpoints: [
        { id: 'frame', target: { kind: 'object', object_id: 'a', region: [0, 0, 1, 1] } },
        { id: 'detail', target: { kind: 'object', object_id: 'a', region: [0.1, 0.2, 0.3, 0.4] } },
        { id: 'other', target: { kind: 'object', object_id: 'b', region: [0, 0, 1, 1] } },
    ],
    paths: [
        {
            id: 'main',
            steps: [
                { id: 's0', viewpoint_id: 'frame', overlay_policy: 'all' },
                { id: 's1', viewpoint_id: 'detail', overlay_policy: 'fixed', overlay_index: 2 },
                { id: 's2', viewpoint_id: 'other', overlay_policy: 'all' },
            ],
        },
    ],
    media_overrides: [],
};
const context = { camera: { cx: 500, cy: 300, zoom: 2 }, media: { id: 'a:0:0', time: 12 } };
test('overlays are symmetric, fixed steps atomic, and duplicate objects independent', () => {
    let state = initial(layout),
        cameraRequest = state.cameraRequest;
    for (const expected of [1, 2]) {
        state = navigate(layout, state, { ...context, type: 'next' });
        expect(state.overlays.a).toBe(expected);
        expect(state.cameraRequest).toBe(cameraRequest);
    }
    expect(state.overlays.duplicate).toBe(0);
    state = navigate(layout, state, { ...context, type: 'next' });
    expect(state.step).toBe(1);
    expect(state.overlays.a).toBe(2);
    state = navigate(layout, state, { ...context, type: 'next' });
    expect(state.step).toBe(2);
    state = navigate(layout, state, { ...context, type: 'previous' });
    expect(state.step).toBe(1);
    state = navigate(layout, state, { ...context, type: 'previous' });
    expect(state.step).toBe(0);
    expect(state.overlays.a).toBe(2);
    state = navigate(layout, state, { ...context, type: 'previous' });
    expect(state.overlays.a).toBe(1);
});
test('nested detours, overview, exact paused bookmark restore, direct guided resume', () => {
    let state = navigate(layout, initial(layout), { ...context, type: 'next' });
    state = navigate(layout, state, { ...context, type: 'focus', id: 'detail' });
    state = navigate(layout, state, { ...context, type: 'overview' });
    state = navigate(layout, state, { ...context, type: 'focus', id: 'other' });
    expect(state.history).toHaveLength(3);
    state = navigate(layout, state, { ...context, type: 'escape' });
    expect(state.mode).toBe('overview');
    state = navigate(layout, state, { ...context, type: 'escape' });
    expect(state.mode).toBe('exploring');
    state = navigate(layout, state, { ...context, type: 'next' });
    expect(state.mode).toBe('guided');
    expect(state.step).toBe(0);
    expect(state.overlays.a).toBe(1);
    expect(state.restoreCamera).toEqual(context.camera);
    expect(state.restoreMedia).toEqual(context.media);
    expect(state.history).toHaveLength(0);
});
test('detour bound preserves the guided anchor', () => {
    let state = initial(layout);
    for (let i = 0; i < 33; i++)
        state = navigate(layout, state, {
            ...context,
            type: 'focus',
            id: i % 2 ? 'detail' : 'other',
        });
    expect(state.history).toHaveLength(32);
    expect(state.notice).toContain('limit');
    state = navigate(layout, state, { ...context, type: 'previous' });
    expect(state.mode).toBe('guided');
    expect(state.step).toBe(0);
});
test('overview step jump enters guided step and drops detours; invalid index is ignored', () => {
    let state = navigate(layout, initial(layout), { ...context, type: 'focus', id: 'other' });
    state = navigate(layout, state, { ...context, type: 'overview' });
    expect(state.history.length).toBe(2);
    const request = state.cameraRequest;
    state = navigate(layout, state, { ...context, type: 'step', id: '1' });
    expect(state.mode).toBe('guided');
    expect(state.step).toBe(1);
    expect(state.viewId).toBe('detail');
    expect(state.overlays.a).toBe(2);
    expect(state.history).toEqual([]);
    expect(state.anchor).toBeNull();
    expect(state.cameraRequest).toBeGreaterThan(request);
    for (const id of ['3', '-1', '1.5', 'x'])
        expect(navigate(layout, state, { ...context, type: 'step', id })).toBe(state);
});
