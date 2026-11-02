import type { Camera } from './navigation';

export type Size = { width: number; height: number };
export type Flight = { at: (t: number) => Camera; duration: number };

const RHO = Math.SQRT2;
/** Smooth zoom-and-pan camera path (van Wijk & Nuij, "Smooth and efficient
 * zooming and panning", InfoVis 2003): far moves zoom out, travel, zoom in.
 * The final sample is the exact target so restores remain bit-identical.
 */
export function flight(from: Camera, to: Camera, size: Size): Flight {
    const extent = Math.max(size.width, size.height);
    const w0 = extent / from.zoom,
        w1 = extent / to.zoom;
    const dx = to.cx - from.cx,
        dy = to.cy - from.cy,
        d2 = dx * dx + dy * dy;
    let path: (t: number) => [number, number, number];
    let S: number;
    if (d2 < 1e-9 * w0 * w0) {
        S = Math.log(w1 / w0) / RHO;
        path = (t) => [from.cx + t * dx, from.cy + t * dy, w0 * Math.exp(RHO * t * S)];
    } else {
        const d1 = Math.sqrt(d2),
            r2 = RHO * RHO,
            r4 = r2 * r2;
        const b0 = (w1 * w1 - w0 * w0 + r4 * d2) / (2 * w0 * r2 * d1),
            b1 = (w1 * w1 - w0 * w0 - r4 * d2) / (2 * w1 * r2 * d1);
        const z0 = Math.log(Math.sqrt(b0 * b0 + 1) - b0),
            z1 = Math.log(Math.sqrt(b1 * b1 + 1) - b1);
        S = (z1 - z0) / RHO;
        const c0 = Math.cosh(z0);
        path = (t) => {
            const s = t * S,
                u = (w0 / (r2 * d1)) * (c0 * Math.tanh(RHO * s + z0) - Math.sinh(z0));
            return [from.cx + u * dx, from.cy + u * dy, (w0 * c0) / Math.cosh(RHO * s + z0)];
        };
    }
    const raw = (Math.abs(S) * 1000 * RHO) / Math.SQRT2;
    // No travel (e.g. two steps on one view that differ only in overlay) is instant.
    const duration =
        Number.isFinite(raw) && raw >= 1 ? Math.max(380, Math.min(1500, raw * 0.85)) : 0;
    return {
        duration,
        at: (t) => {
            if (t >= 1) return { ...to };
            const k = t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2;
            const [cx, cy, w] = path(k);
            return { cx, cy, zoom: extent / w };
        },
    };
}
