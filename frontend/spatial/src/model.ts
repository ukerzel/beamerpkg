import { z } from 'zod';

const id = z.string().regex(/^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$/);
const finite = z.number().finite();
const rect = z.tuple([finite, finite, finite.positive(), finite.positive()]);
const target = z.discriminatedUnion('kind', [
    z.object({ kind: z.literal('object'), object_id: id, region: rect }).strict(),
    z.object({ kind: z.literal('world_rect'), rect }).strict(),
]);
const layoutSchema = z
    .object({
        format: z.literal('beamerpkg-spatial'),
        schema_version: z.literal(1),
        source: z
            .object({ pdf_path: z.string(), pdf_sha256: z.string().regex(/^[a-f0-9]{64}$/) })
            .strict(),
        frames: z
            .array(
                z
                    .object({ id, page_indices: z.array(z.number().int().min(0)).min(1).max(200) })
                    .strict(),
            )
            .min(1)
            .max(200),
        objects: z
            .array(
                z
                    .object({
                        id,
                        frame_id: id,
                        x: finite.min(-1e6).max(1e6),
                        y: finite.min(-1e6).max(1e6),
                        width: finite.positive().max(1e5),
                    })
                    .strict(),
            )
            .min(1)
            .max(400),
        viewpoints: z
            .array(z.object({ id, target, padding: finite.min(0).max(0.45).optional() }).strict())
            .min(1)
            .max(800),
        paths: z
            .array(
                z
                    .object({
                        id,
                        steps: z
                            .array(
                                z
                                    .object({
                                        id,
                                        viewpoint_id: id,
                                        overlay_policy: z.enum(['all', 'fixed']),
                                        overlay_index: z.number().int().min(0).optional(),
                                    })
                                    .strict(),
                            )
                            .min(1)
                            .max(2000),
                    })
                    .strict(),
            )
            .min(1)
            .max(32),
        media_overrides: z.array(z.never()).max(0),
    })
    .strict();
const pageSchema = z
    .object({
        width: finite.positive(),
        height: finite.positive(),
        rotation: z.union([z.literal(0), z.literal(90), z.literal(180), z.literal(270)]),
        box: z.tuple([finite, finite, finite, finite]),
    })
    .strict();
const placementSchema = z
    .object({
        page_index: z.number().int().min(0),
        annotation_index: z.number().int().min(0),
        asset_path: z.string().max(4096),
        rect_pdf: z.tuple([finite, finite, finite, finite]),
        kind: z.enum(['movie', 'pdfpc_launch']),
        autostart: z.boolean().nullable(),
        loop: z.boolean().nullable(),
        controls: z.boolean().nullable(),
        url: z.string().regex(/^\/runtime\/asset-[0-9]+$/),
    })
    .strict();
const projectSchema = z
    .object({
        source: layoutSchema.shape.source,
        pages: z.array(pageSchema).min(1).max(200),
        placements: z.array(placementSchema).max(2000),
        layout: layoutSchema,
        authored_layout: z.boolean(),
        pdf_url: z.literal('/runtime/document.pdf'),
    })
    .strict();

export type Layout = z.infer<typeof layoutSchema>;
export type Project = z.infer<typeof projectSchema>;
export type Placement = Project['placements'][number];
export type View = Layout['viewpoints'][number];
export type CanvasObject = Layout['objects'][number];
export type Box = [number, number, number, number];

export function parseProject(raw: unknown): Project {
    const project = projectSchema.parse(raw),
        m = project.layout;
    const fail = (message: string): never => {
        throw new Error(`Spatial project: ${message}`);
    };
    function unique<T extends { id: string }>(items: T[]): Map<string, T> {
        const result = new Map(items.map((v) => [v.id, v]));
        if (result.size !== items.length) fail('duplicate IDs');
        return result;
    }
    // Compare fields explicitly: JSON key order is not part of the contract.
    if (
        project.source.pdf_path !== m.source.pdf_path ||
        project.source.pdf_sha256 !== m.source.pdf_sha256
    )
        fail('PDF binding mismatch');
    const frames = unique(m.frames),
        objects = unique(m.objects),
        views = unique(m.viewpoints);
    unique(m.paths);
    const used = new Set<number>();
    for (const f of frames.values())
        for (const [n, p] of f.page_indices.entries()) {
            if (p >= project.pages.length || used.has(p) || p !== f.page_indices[0] + n)
                fail('invalid/overlapping frame pages');
            if (
                JSON.stringify(project.pages[p]) !==
                JSON.stringify(project.pages[f.page_indices[0]])
            )
                fail('group geometry differs');
            used.add(p);
        }
    for (const obj of objects.values()) if (!frames.has(obj.frame_id)) fail('unknown frame');
    for (const v of views.values()) {
        const t = v.target,
            r = t.kind === 'object' ? t.region : t.rect;
        if (t.kind === 'object') {
            if (!objects.has(t.object_id)) fail('unknown object');
            if (r.some((x) => x < 0 || x > 1) || r[0] + r[2] > 1 || r[1] + r[3] > 1)
                fail('invalid region');
        } else if (r.some((x) => Math.abs(x) > 1e6)) fail('world bounds');
    }
    let total = 0;
    for (const path of m.paths) {
        unique(path.steps);
        total += path.steps.length;
        for (const s of path.steps) {
            const v = views.get(s.viewpoint_id) ?? fail('unknown viewpoint');
            if (v.target.kind === 'world_rect') {
                if (s.overlay_policy !== 'fixed' || s.overlay_index !== undefined)
                    fail('world overlay');
            } else {
                const obj = objects.get(v.target.object_id)!;
                if (
                    (s.overlay_index ?? 0) >= frames.get(obj.frame_id)!.page_indices.length ||
                    (s.overlay_policy === 'all' && s.overlay_index !== undefined)
                )
                    fail('invalid overlay');
            }
        }
    }
    if (total > 2000) fail('step limit');
    for (const p of project.placements)
        if (
            p.page_index >= project.pages.length ||
            p.rect_pdf[0] === p.rect_pdf[2] ||
            p.rect_pdf[1] === p.rect_pdf[3]
        )
            fail('invalid placement');
    return project;
}

export function objectBox(project: Project, obj: CanvasObject): Box {
    const frame = project.layout.frames.find((f) => f.id === obj.frame_id)!;
    const page = project.pages[frame.page_indices[0]];
    return [obj.x, obj.y, obj.width, (obj.width * page.height) / page.width];
}
export function worldBox(project: Project): Box {
    const boxes = project.layout.objects.map((o) => objectBox(project, o));
    const x = Math.min(...boxes.map((b) => b[0])),
        y = Math.min(...boxes.map((b) => b[1]));
    return [
        x,
        y,
        Math.max(...boxes.map((b) => b[0] + b[2])) - x,
        Math.max(...boxes.map((b) => b[1] + b[3])) - y,
    ];
}
export function viewBox(project: Project, view: View): Box {
    if (view.target.kind === 'world_rect') return view.target.rect;
    const t = view.target,
        box = objectBox(
            project,
            project.layout.objects.find((o) => o.id === t.object_id)!,
        );
    return [
        box[0] + t.region[0] * box[2],
        box[1] + t.region[1] * box[3],
        box[2] * t.region[2],
        box[3] * t.region[3],
    ];
}
