import {
    useCallback,
    useEffect,
    useLayoutEffect,
    useMemo,
    useRef,
    useState,
    type CSSProperties,
} from 'react';
import { createRoot } from 'react-dom/client';
import type { PDFDocumentProxy } from 'pdfjs-dist';
import {
    objectBox,
    parseProject,
    viewBox,
    worldBox,
    type Box,
    type Placement,
    type Project,
    type View,
} from './model';
import { initial, navigate, type Action, type Bookmark, type Camera } from './navigation';
import { openPdf, rectangle } from './pdf';
import { Renderer, thumbnailBudget } from './rendering';
import { MediaController } from './media';
import { flight, type Size } from './flight';
import { Icon, PlayGlyph } from './icons';
import './style.css';

const boundZoom = (z: number) => Math.max(0.0001, Math.min(64, z));
function fit(box: Box, size: Size, padding = 0.06): Camera {
    return {
        cx: box[0] + box[2] / 2,
        cy: box[1] + box[3] / 2,
        zoom: boundZoom(
            Math.min(
                (size.width * (1 - 2 * padding)) / box[2],
                (size.height * (1 - 2 * padding)) / box[3],
            ),
        ),
    };
}
/** World -> stage pixel transform for overlays drawn in screen space. */
function project2screen(c: Camera, size: Size) {
    return (x: number, y: number) => [
        (x - c.cx) * c.zoom + size.width / 2,
        (y - c.cy) * c.zoom + size.height / 2,
    ];
}
/** Two dot-grid layers at power-of-four world spacings: the fine one fades as
 * it gets dense, so zooming feels continuous across any scale. */
function gridStyle(c: Camera, size: Size): CSSProperties {
    const k = Math.ceil(Math.log(22 / c.zoom) / Math.log(4));
    const fine = 4 ** k * c.zoom,
        coarse = fine * 4;
    const ox = size.width / 2 - c.cx * c.zoom,
        oy = size.height / 2 - c.cy * c.zoom;
    const a = Math.min(1, (fine - 22) / 60) * 0.32;
    return {
        backgroundImage: `radial-gradient(circle at 1px 1px, rgba(165,180,252,${a.toFixed(3)}) 1px, transparent 1.4px), radial-gradient(circle at 1.25px 1.25px, rgba(165,180,252,0.34) 1.25px, transparent 1.7px)`,
        backgroundSize: `${fine}px ${fine}px, ${coarse}px ${coarse}px`,
        backgroundPosition: `${ox}px ${oy}px, ${ox}px ${oy}px`,
    };
}

function Thumbnail({
    id,
    page,
    renderer,
    onReady,
}: {
    id: string;
    page: number;
    renderer: Renderer;
    onReady: () => void;
}) {
    const ref = useRef<HTMLCanvasElement>(null);
    const [ready, setReady] = useState(false);
    useEffect(() => {
        let current = true;
        // The renderer clamps the scale to this deck's per-thumbnail pixel budget.
        if (ref.current)
            renderer.request(id, page, ref.current, 16, [0, 0, 1, 1], () => {
                if (!current) return;
                setReady(true);
                onReady();
            });
        return () => {
            current = false;
        };
    }, [id, page, renderer, onReady]);
    return (
        <>
            <canvas
                ref={ref}
                width={1}
                height={1}
                className={`thumbnail${ready ? ' ready' : ''}`}
                data-object={id}
                aria-label={`PDF page ${page + 1}`}
            />
            {!ready && <span className="shimmer" aria-hidden="true" />}
        </>
    );
}

function Movie({
    placement,
    objectId,
    selected,
    choose,
    controller,
    restore,
    pdf,
    status,
}: {
    placement: Placement;
    objectId: string;
    selected: boolean;
    choose: () => void;
    controller: MediaController;
    restore: Bookmark;
    pdf: PDFDocumentProxy;
    status: string;
}) {
    const ref = useRef<HTMLVideoElement>(null);
    const [rect, setRect] = useState<number[] | null>(null);
    const [shown, setShown] = useState(false);
    const id = `${objectId}:${placement.page_index}:${placement.annotation_index}`;
    useEffect(() => {
        let current = true;
        void pdf.getPage(placement.page_index + 1).then((p) => {
            if (current) setRect(rectangle(p, placement.rect_pdf));
        });
        return () => {
            current = false;
        };
    }, [pdf, placement]);
    useEffect(() => {
        if (!selected || !rect || !ref.current) return;
        controller.activate(id, ref.current, placement, restore);
        return () => controller.deactivate();
    }, [selected, rect, id, placement, controller, restore]);
    if (!rect) return null;
    const playing = selected && status === 'Playing';
    const startable =
        !selected || ['Ready', 'Paused'].includes(status) || status.includes('blocked');
    const start = () => {
        if (selected) void controller.play();
        else choose();
    };
    return (
        <div
            className={`movie${playing ? ' playing' : ''}`}
            style={{
                left: `${rect[0] * 100}%`,
                top: `${rect[1] * 100}%`,
                width: `${rect[2] * 100}%`,
                height: `${rect[3] * 100}%`,
            }}
            onPointerDown={(e) => e.stopPropagation()}
            onWheel={(e) => e.stopPropagation()}
        >
            <video
                ref={ref}
                src={placement.url}
                preload="metadata"
                controls={placement.controls === true}
                loop={placement.loop === true}
                playsInline
                style={{ visibility: selected && shown ? 'visible' : 'hidden' }}
                onPlaying={() => setShown(true)}
                onSeeked={() => {
                    if (selected && ref.current && ref.current.currentTime > 0) setShown(true);
                }}
                onLoadedData={() => {
                    if (selected && restore?.id === id) setShown(true);
                }}
            />
            {!playing && startable && (
                <div className="bigplay" aria-hidden="true" onClick={start}>
                    <PlayGlyph playing={false} size={34} />
                </div>
            )}
            <div className="movie-controls">
                {playing ? (
                    <button
                        className="round"
                        onClick={() => controller.pause()}
                        aria-label="Pause video"
                    >
                        <PlayGlyph playing />
                    </button>
                ) : (
                    <button className="round" onClick={start} aria-label="Play video">
                        <PlayGlyph playing={false} />
                    </button>
                )}
                <span role="status">{selected ? status : 'Select video'}</span>
                <MediaError video={ref.current} />
            </div>
        </div>
    );
}
function MediaError({ video }: { video: HTMLVideoElement | null }) {
    const [error, setError] = useState('');
    useEffect(() => {
        if (!video) return;
        const update = () => setError('Video unavailable: unsupported format or decode error.');
        video.addEventListener('error', update);
        if (video.error) update();
        return () => video.removeEventListener('error', update);
    }, [video]);
    return error ? <span role="alert">{error}</span> : null;
}

type StepPoint = { index: number; id: string; x: number; y: number };
/** The guided path drawn as a flowing route with numbered stops (overview). */
function Route({
    points,
    camera,
    size,
    current,
    visible,
    jump,
}: {
    points: StepPoint[];
    camera: Camera;
    size: Size;
    current: number;
    visible: boolean;
    jump: (index: number) => void;
}) {
    const toScreen = project2screen(camera, size);
    const screen = points.map((p) => {
        const [x, y] = toScreen(p.x, p.y);
        return { ...p, sx: x, sy: y };
    });
    // Stops sharing a location fan out so each number stays clickable.
    const seen = new Map<string, number>();
    for (const p of screen) {
        const key = `${Math.round(p.sx / 8)}:${Math.round(p.sy / 8)}`;
        const n = seen.get(key) ?? 0;
        seen.set(key, n + 1);
        p.sx += n * 30;
    }
    let d = '';
    screen.forEach((p, i) => {
        if (!i) return void (d += `M${p.sx},${p.sy}`);
        const a = screen[i - 1],
            mx = (a.sx + p.sx) / 2,
            my = (a.sy + p.sy) / 2,
            dx = p.sx - a.sx,
            dy = p.sy - a.sy;
        d += ` Q${mx - dy * 0.12},${my + dx * 0.12} ${p.sx},${p.sy}`;
    });
    return (
        <div className={`route${visible ? ' visible' : ''}`} aria-hidden={!visible}>
            <svg width={size.width} height={size.height}>
                <defs>
                    <linearGradient id="route-gradient" x1="0" x2="1">
                        <stop offset="0" stopColor="#67e8f9" />
                        <stop offset="0.5" stopColor="#818cf8" />
                        <stop offset="1" stopColor="#e879f9" />
                    </linearGradient>
                </defs>
                <path d={d} className="route-glow" />
                <path d={d} className="route-line" />
            </svg>
            {screen.map((p) => (
                <button
                    key={p.id}
                    className={`stop${p.index === current ? ' current' : ''}${p.index < current ? ' done' : ''}`}
                    style={{ left: p.sx, top: p.sy, animationDelay: `${p.index * 45}ms` }}
                    onClick={() => jump(p.index)}
                    tabIndex={visible ? 0 : -1}
                    aria-label={`Go to step ${p.index + 1}`}
                    data-tip={p.id}
                >
                    {p.index + 1}
                </button>
            ))}
        </div>
    );
}

function Minimap({
    project,
    camera,
    size,
    activeId,
    points,
    pick,
}: {
    project: Project;
    camera: Camera;
    size: Size;
    activeId: string | undefined;
    points: StepPoint[];
    pick: (objectId: string) => void;
}) {
    const world = worldBox(project);
    const margin = Math.max(world[2], world[3]) * 0.06;
    const box: Box = [
        world[0] - margin,
        world[1] - margin,
        world[2] + 2 * margin,
        world[3] + 2 * margin,
    ];
    const width = 200,
        height = Math.max(70, Math.min(150, (width * box[3]) / box[2]));
    const view: Box = [
        camera.cx - size.width / (2 * camera.zoom),
        camera.cy - size.height / (2 * camera.zoom),
        size.width / camera.zoom,
        size.height / camera.zoom,
    ];
    return (
        <nav className="minimap" aria-label="Minimap">
            <svg
                width={width}
                height={height}
                viewBox={box.join(' ')}
                preserveAspectRatio="xMidYMid meet"
            >
                <polyline
                    points={points.map((p) => `${p.x},${p.y}`).join(' ')}
                    className="mini-route"
                />
                {project.layout.objects.map((o) => {
                    const b = objectBox(project, o);
                    return (
                        <rect
                            key={o.id}
                            x={b[0]}
                            y={b[1]}
                            width={b[2]}
                            height={b[3]}
                            rx={b[2] * 0.02}
                            className={o.id === activeId ? 'mini-obj active' : 'mini-obj'}
                            onClick={() => pick(o.id)}
                        >
                            <title>{o.id}</title>
                        </rect>
                    );
                })}
                <rect
                    x={view[0]}
                    y={view[1]}
                    width={view[2]}
                    height={view[3]}
                    className="mini-view"
                />
            </svg>
        </nav>
    );
}

/** Crops a viewpoint preview from the already rendered object thumbnail; no
 * additional PDF rendering happens for previews. */
function ViewPreview({ view, version }: { view: View; version: number }) {
    const ref = useRef<HTMLCanvasElement>(null);
    useEffect(() => {
        const canvas = ref.current,
            t = view.target;
        if (!canvas || t.kind !== 'object') return;
        const source = document.querySelector<HTMLCanvasElement>(
            `canvas.thumbnail[data-object="${CSS.escape(t.object_id)}"]`,
        );
        if (!source || source.width <= 1) return;
        const [rx, ry, rw, rh] = t.region,
            sw = source.width * rw,
            sh = source.height * rh;
        const scale = Math.min(canvas.width / sw, canvas.height / sh),
            w = sw * scale,
            h = sh * scale;
        const g = canvas.getContext('2d')!;
        g.clearRect(0, 0, canvas.width, canvas.height);
        g.imageSmoothingQuality = 'high';
        g.drawImage(
            source,
            source.width * rx,
            source.height * ry,
            sw,
            sh,
            (canvas.width - w) / 2,
            (canvas.height - h) / 2,
            w,
            h,
        );
    }, [view, version]);
    return view.target.kind === 'object' ? (
        <canvas ref={ref} width={192} height={108} />
    ) : (
        <span className="schematic" />
    );
}

function ViewsDrawer({
    project,
    pathSteps,
    currentView,
    version,
    focus,
}: {
    project: Project;
    pathSteps: { viewpoint_id: string }[];
    currentView: string;
    version: number;
    focus: (id: string) => void;
}) {
    return (
        <aside aria-label="Viewpoints" className="drawer">
            <h2>
                <Icon name="views" size={16} /> Views
            </h2>
            <div className="drawer-list">
                {project.layout.viewpoints.map((v, i) => {
                    const steps = pathSteps.flatMap((s, n) =>
                        s.viewpoint_id === v.id ? [n + 1] : [],
                    );
                    const t = v.target;
                    const meta =
                        t.kind === 'object'
                            ? t.region.join() === '0,0,1,1'
                                ? `Whole frame · ${t.object_id}`
                                : `Detail · ${Math.round(t.region[2] * 100)}% of ${t.object_id}`
                            : 'Canvas region';
                    return (
                        <button
                            key={v.id}
                            aria-label={v.id}
                            className={`card${v.id === currentView ? ' current' : ''}`}
                            onClick={() => focus(v.id)}
                            style={{ animationDelay: `${Math.min(i, 12) * 30}ms` }}
                        >
                            <span className="preview">
                                {i < 48 ? (
                                    <ViewPreview view={v} version={version} />
                                ) : (
                                    <span className="schematic" />
                                )}
                            </span>
                            <span className="meta">
                                <strong>{v.id}</strong>
                                <small>{meta}</small>
                            </span>
                            {steps.length > 0 && (
                                <span className="chips">
                                    {steps.slice(0, 3).map((n) => (
                                        <em key={n}>{n}</em>
                                    ))}
                                </span>
                            )}
                        </button>
                    );
                })}
            </div>
        </aside>
    );
}

const SHORTCUTS: [string[], string][] = [
    [['→', 'Space', 'PgDn'], 'Next overlay, then next step'],
    [['←', 'PgUp'], 'Previous overlay or step'],
    [['O'], 'Overview of the whole canvas'],
    [['Esc'], 'Step back out of a detour'],
    [['V'], 'Views drawer'],
    [['M'], 'Minimap'],
    [['F'], 'Fullscreen'],
    [['?'], 'This sheet'],
];
function HelpSheet({ close }: { close: () => void }) {
    return (
        <div className="scrim" onClick={close}>
            <div
                className="sheet"
                role="dialog"
                aria-modal="true"
                aria-label="Keyboard shortcuts"
                onClick={(e) => e.stopPropagation()}
            >
                <button className="ghost close" onClick={close} aria-label="Close help">
                    <Icon name="close" />
                </button>
                <h2>Presenting on an infinite canvas</h2>
                <p>
                    Drag to pan, scroll to zoom, double-click a frame to focus it. Exploring never
                    loses your place: the next arrow returns to the guided step.
                </p>
                <dl>
                    {SHORTCUTS.map(([keys, label]) => (
                        <div key={label}>
                            <dt>
                                {keys.map((k) => (
                                    <kbd key={k}>{k}</kbd>
                                ))}
                            </dt>
                            <dd>{label}</dd>
                        </div>
                    ))}
                </dl>
                <p className="fine">
                    Slides are the unchanged PDF, rendered locally. Layout editing is not part of
                    this prototype.
                </p>
            </div>
        </div>
    );
}

function Viewer({ project, pdf }: { project: Project; pdf: PDFDocumentProxy }) {
    const [state, setState] = useState(() => initial(project.layout));
    const [camera, setCamera] = useState<Camera>({ cx: 0, cy: 0, zoom: 1 });
    const cameraRef = useRef(camera);
    cameraRef.current = camera;
    const [size, setSize] = useState<Size>({ width: 1, height: 1 });
    const stage = useRef<HTMLDivElement>(null),
        detail = useRef<HTMLCanvasElement>(null),
        ghost = useRef<HTMLCanvasElement>(null);
    const [error, setError] = useState(''),
        [status, setStatus] = useState('Ready');
    const [viewsOpen, setViewsOpen] = useState(false),
        [help, setHelp] = useState(false),
        [minimapPref, setMinimapPref] = useState<boolean | null>(null),
        [idle, setIdle] = useState(false),
        [dragging, setDragging] = useState(false),
        [thumbs, setThumbs] = useState(0);
    const [chosen, setChosen] = useState<Record<string, number>>({});
    const [renderer] = useState(
        () => new Renderer(pdf, setError, thumbnailBudget(project.layout.objects.length)),
    );
    const [media] = useState(() => new MediaController(setStatus));
    const motion = useRef(0),
        request = useRef(-1),
        opening = useRef(true),
        idleTimer = useRef(0);
    const animating = useRef(false),
        pendingRestore = useRef<Camera | null>(null);
    const drag = useRef<{ x: number; y: number; moved: boolean; object?: string } | null>(null);
    const stateRef = useRef(state);
    stateRef.current = state;
    const view = project.layout.viewpoints.find((v) => v.id === state.viewId)!;
    const activeObject =
        state.mode !== 'overview' && view.target.kind === 'object'
            ? project.layout.objects.find(
                  (o) => view.target.kind === 'object' && o.id === view.target.object_id,
              )!
            : null;
    const frame = activeObject
        ? project.layout.frames.find((f) => f.id === activeObject.frame_id)!
        : null;
    const activePage =
        activeObject && frame ? frame.page_indices[state.overlays[activeObject.id]] : -1;
    const activeBox = activeObject ? objectBox(project, activeObject) : null;
    const placements = project.placements.filter((p) => p.page_index === activePage);
    const objectPage = activeObject ? `${activeObject.id}:${activePage}` : '';
    const restoredAnnotation = state.restoreMedia?.id.startsWith(objectPage + ':')
        ? Number(state.restoreMedia.id.split(':').at(-1))
        : undefined;
    const autostart = placements.filter((p) => p.autostart);
    const selected =
        restoredAnnotation ??
        chosen[objectPage] ??
        (autostart.length <= 1 ? (autostart[0] ?? placements[0])?.annotation_index : undefined);
    const act = useCallback(
        (type: Action['type'], id?: string) => {
            setState((s) =>
                navigate(project.layout, s, {
                    type,
                    id,
                    camera: cameraRef.current,
                    media: media.bookmark(),
                }),
            );
        },
        [project, media],
    );
    const bumpThumbs = useCallback(() => setThumbs((n) => n + 1), []);
    const toggleFullscreen = useCallback(() => {
        if (document.fullscreenElement) void document.exitFullscreen().catch(() => undefined);
        else void document.documentElement.requestFullscreen?.().catch(() => undefined);
    }, []);
    const wake = useCallback(() => {
        setIdle(false);
        clearTimeout(idleTimer.current);
        idleTimer.current = window.setTimeout(() => setIdle(true), 2600);
    }, []);
    useEffect(() => {
        wake();
        window.addEventListener('pointermove', wake);
        window.addEventListener('pointerdown', wake);
        return () => {
            clearTimeout(idleTimer.current);
            window.removeEventListener('pointermove', wake);
            window.removeEventListener('pointerdown', wake);
        };
    }, [wake]);
    useLayoutEffect(() => {
        const observer = new ResizeObserver((entries) => {
            const r = entries[0].contentRect;
            setSize({ width: r.width, height: r.height });
        });
        observer.observe(stage.current!);
        return () => observer.disconnect();
    }, []);
    useEffect(() => {
        const currentRequest = state.cameraRequest !== request.current;
        const continuing = animating.current;
        if (!currentRequest && state.mode === 'exploring' && !continuing) return;
        request.current = state.cameraRequest;
        if (currentRequest) pendingRestore.current = state.restoreCamera;
        cancelAnimationFrame(motion.current);
        if (!size.width || size.width <= 1) return;
        const target =
            pendingRestore.current ??
            fit(
                state.mode === 'overview' ? worldBox(project) : viewBox(project, view),
                size,
                view.padding,
            );
        const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
        // The first valid size opens on the whole canvas, then flies to step one.
        const intro = opening.current && !reduced;
        opening.current = false;
        const from = intro ? fit(worldBox(project), size, 0.1) : cameraRef.current;
        const path = flight(from, target, size);
        const duration =
            reduced || (!currentRequest && !continuing && !intro)
                ? 0
                : intro
                  ? Math.max(1300, path.duration)
                  : path.duration;
        const hold = intro ? 450 : 0;
        animating.current = duration > 0;
        const start = performance.now() + hold;
        const tick = (now: number) => {
            const t = duration ? Math.max(0, Math.min(1, (now - start) / duration)) : 1;
            setCamera(path.at(t));
            if (t < 1) motion.current = requestAnimationFrame(tick);
            else animating.current = false;
        };
        motion.current = requestAnimationFrame(tick);
        return () => cancelAnimationFrame(motion.current);
    }, [state.cameraRequest, size, project]);
    useEffect(() => {
        const handler = (e: KeyboardEvent) => {
            if (e.ctrlKey || e.metaKey || e.altKey) return;
            if (
                e.target instanceof HTMLElement &&
                (e.target.closest('select,input,textarea,video') ||
                    (e.key === ' ' && e.target.closest('button')))
            )
                return;
            if (help && (e.key === 'Escape' || e.key === '?')) {
                e.preventDefault();
                setHelp(false);
                return;
            }
            const local: Record<string, () => void> = {
                '?': () => setHelp((v) => !v),
                h: () => setHelp((v) => !v),
                f: toggleFullscreen,
                m: () => setMinimapPref((v) => !(v ?? stateRef.current.mode !== 'guided')),
                v: () => setViewsOpen((v) => !v),
            };
            const toggle = local[e.key.length === 1 ? e.key.toLowerCase() : e.key];
            if (toggle) {
                e.preventDefault();
                toggle();
                return;
            }
            const command = (
                {
                    ArrowRight: 'next',
                    ArrowDown: 'next',
                    PageDown: 'next',
                    ' ': 'next',
                    ArrowLeft: 'previous',
                    ArrowUp: 'previous',
                    PageUp: 'previous',
                    Escape: 'escape',
                    o: 'overview',
                    O: 'overview',
                } as const
            )[e.key as 'ArrowRight'];
            if (command) {
                e.preventDefault();
                act(command);
            }
        };
        const visibility = () => {
            if (document.hidden) media.pause();
        };
        window.addEventListener('keydown', handler);
        document.addEventListener('visibilitychange', visibility);
        return () => {
            window.removeEventListener('keydown', handler);
            document.removeEventListener('visibilitychange', visibility);
        };
    }, [act, media, help, toggleFullscreen]);
    useEffect(() => {
        if (activePage < 0) media.deactivate();
    }, [activePage, media]);
    useEffect(
        () => () => {
            cancelAnimationFrame(motion.current);
            renderer.stop();
            media.deactivate();
        },
        [renderer, media],
    );
    const clip: Box | null = activeBox
        ? (() => {
              const x = Math.max(
                  0,
                  (camera.cx - size.width / (2 * camera.zoom) - activeBox[0]) / activeBox[2],
              );
              const y = Math.max(
                  0,
                  (camera.cy - size.height / (2 * camera.zoom) - activeBox[1]) / activeBox[3],
              );
              const right = Math.min(
                  1,
                  (camera.cx + size.width / (2 * camera.zoom) - activeBox[0]) / activeBox[2],
              );
              const bottom = Math.min(
                  1,
                  (camera.cy + size.height / (2 * camera.zoom) - activeBox[1]) / activeBox[3],
              );
              return right > x && bottom > y ? [x, y, right - x, bottom - y] : null;
          })()
        : null;
    const [detailBox, setDetailBox] = useState<Box | null>(null);
    const [ghostBox, setGhostBox] = useState<{ box: Box; fading: boolean } | null>(null);
    const clearGhost = useCallback(() => {
        if (ghost.current) ghost.current.width = ghost.current.height = 1;
        setGhostBox(null);
    }, []);
    // Overlay crossfade: hold the sharp previous overlay until the new one is
    // rendered, then dissolve it. The PDF pages themselves are unchanged.
    const shown = useRef<{ page: number; object?: string }>({ page: -1 });
    useLayoutEffect(() => {
        const previous = shown.current;
        shown.current = { page: activePage, object: activeObject?.id };
        const d = detail.current,
            g = ghost.current;
        if (previous.object !== activeObject?.id) {
            if (ghostBox) clearGhost();
            return;
        }
        if (
            !d ||
            !g ||
            !detailBox ||
            previous.page === activePage ||
            d.dataset.page !== String(previous.page) ||
            matchMedia('(prefers-reduced-motion: reduce)').matches
        )
            return;
        g.width = d.width;
        g.height = d.height;
        g.getContext('2d')!.drawImage(d, 0, 0);
        setGhostBox({ box: detailBox, fading: false });
    }, [activePage, activeObject?.id]);
    useEffect(() => {
        if (!ghostBox?.fading) return;
        const timer = setTimeout(clearGhost, 320);
        return () => clearTimeout(timer);
    }, [ghostBox?.fading, clearGhost]);
    const activeGeneration = useRef(0);
    const lastDetailCamera = useRef<Camera | null>(null);
    useEffect(() => {
        renderer.cancelDetail();
        const generation = ++activeGeneration.current;
        const cameraMoved = lastDetailCamera.current !== camera;
        lastDetailCamera.current = camera;
        if (!activeObject || !activeBox || !clip || !detail.current) {
            setDetailBox(null);
            if (ghostBox) clearGhost();
            if (detail.current) detail.current.width = detail.current.height = 1;
            return;
        }
        // Overlay-only changes render at once; camera motion is debounced.
        const timer = setTimeout(
            () => {
                void pdf.getPage(activePage + 1).then((p) => {
                    if (generation !== activeGeneration.current || !detail.current) return;
                    const base = p.getViewport({ scale: 1 });
                    renderer.request(
                        'detail',
                        activePage,
                        detail.current,
                        (activeBox[2] * camera.zoom * devicePixelRatio) / base.width,
                        clip,
                        () => {
                            if (generation !== activeGeneration.current) return;
                            setDetailBox([
                                activeBox[0] + clip[0] * activeBox[2],
                                activeBox[1] + clip[1] * activeBox[3],
                                clip[2] * activeBox[2],
                                clip[3] * activeBox[3],
                            ]);
                            setGhostBox((g) => (g ? { ...g, fading: true } : g));
                        },
                    );
                });
            },
            cameraMoved ? 100 : 0,
        );
        return () => {
            clearTimeout(timer);
            renderer.cancelDetail();
        };
    }, [activePage, activeObject?.id, camera, size, renderer, pdf]);
    // A detail tile for a previous physical page must never cover the new overlay.
    const detailMatchesPage = detail.current?.dataset.page === String(activePage);
    const path = project.layout.paths.find((p) => p.id === state.pathId)!;
    const stepPoints = useMemo<StepPoint[]>(
        () =>
            path.steps.map((s, index) => {
                const b = viewBox(
                    project,
                    project.layout.viewpoints.find((v) => v.id === s.viewpoint_id)!,
                );
                return { index, id: s.id, x: b[0] + b[2] / 2, y: b[1] + b[3] / 2 };
            }),
        [path, project],
    );
    const focusObject = (objectId: string) => {
        const views = project.layout.viewpoints.filter(
            (v) => v.target.kind === 'object' && v.target.object_id === objectId,
        );
        const v =
            views.find((v) => v.target.kind === 'object' && v.target.region.join() === '0,0,1,1') ??
            views[0];
        if (v && !(stateRef.current.mode === 'exploring' && stateRef.current.viewId === v.id))
            act('focus', v.id);
    };
    const beginGesture = () => {
        cancelAnimationFrame(motion.current);
        animating.current = false;
        pendingRestore.current = null;
        if (stateRef.current.mode !== 'exploring') act('pan');
    };
    const overlayCount = frame?.page_indices.length ?? 1;
    const overlayIndex = activeObject ? state.overlays[activeObject.id] : 0;
    const progress =
        path.steps.length > 0
            ? (state.step + (overlayIndex + 1) / overlayCount) / path.steps.length
            : 0;
    const quiet = idle && state.mode === 'guided' && !viewsOpen && !help;
    const showMinimap = minimapPref ?? state.mode !== 'guided';
    const anchorStep = state.anchor ? state.anchor.step + 1 : null;
    const segmented = path.steps.length <= 24;
    return (
        <div className={`app${quiet ? ' quiet' : ''}`}>
            <div className="progress" aria-hidden="true">
                <span style={{ transform: `scaleX(${progress})` }} />
            </div>
            <div className="workspace">
                <div className="viewport">
                    <div
                        ref={stage}
                        className={`stage mode-${state.mode}${dragging ? ' dragging' : ''}`}
                        tabIndex={0}
                        aria-label="Presentation canvas"
                        style={gridStyle(camera, size)}
                        onPointerDown={(e) => {
                            if (
                                e.button !== 0 ||
                                (e.target as HTMLElement).closest('button,select,video,a')
                            )
                                return;
                            e.currentTarget.focus();
                            const surface = (e.target as HTMLElement).closest<HTMLElement>(
                                '[data-object-id]',
                            );
                            drag.current = {
                                x: e.clientX,
                                y: e.clientY,
                                moved: false,
                                object: surface?.dataset.objectId,
                            };
                            e.currentTarget.setPointerCapture(e.pointerId);
                        }}
                        onPointerMove={(e) => {
                            const d = drag.current;
                            if (
                                !d ||
                                (!d.moved && Math.hypot(e.clientX - d.x, e.clientY - d.y) < 3)
                            )
                                return;
                            if (!d.moved) {
                                beginGesture();
                                setDragging(true);
                            }
                            setCamera((c) => ({
                                ...c,
                                cx: c.cx - (e.clientX - d.x) / c.zoom,
                                cy: c.cy - (e.clientY - d.y) / c.zoom,
                            }));
                            drag.current = { x: e.clientX, y: e.clientY, moved: true };
                        }}
                        onPointerUp={() => {
                            const d = drag.current;
                            drag.current = null;
                            setDragging(false);
                            // In the overview, a plain click on a frame flies into it.
                            if (d && !d.moved && d.object && stateRef.current.mode === 'overview')
                                focusObject(d.object);
                        }}
                        onPointerCancel={() => {
                            drag.current = null;
                            setDragging(false);
                        }}
                        onWheel={(e) => {
                            if ((e.target as HTMLElement).closest('video,button')) return;
                            beginGesture();
                            const r = e.currentTarget.getBoundingClientRect(),
                                x = e.clientX - r.left - size.width / 2,
                                y = e.clientY - r.top - size.height / 2;
                            setCamera((c) => {
                                const z = boundZoom(c.zoom * Math.exp(-e.deltaY * 0.001));
                                return {
                                    cx: c.cx + x / c.zoom - x / z,
                                    cy: c.cy + y / c.zoom - y / z,
                                    zoom: z,
                                };
                            });
                        }}
                    >
                        <div
                            className="world"
                            data-testid="world"
                            data-cx={camera.cx}
                            data-cy={camera.cy}
                            data-zoom={camera.zoom}
                            style={
                                {
                                    transform: `translate(${size.width / 2 - camera.cx * camera.zoom}px,${size.height / 2 - camera.cy * camera.zoom}px) scale(${camera.zoom})`,
                                    '--z': camera.zoom,
                                } as CSSProperties
                            }
                        >
                            {project.layout.objects.map((obj, i) => {
                                const b = objectBox(project, obj),
                                    f = project.layout.frames.find((f) => f.id === obj.frame_id)!,
                                    page = f.page_indices[state.overlays[obj.id]];
                                const role = !activeObject
                                    ? ''
                                    : obj.id === activeObject.id
                                      ? ' active'
                                      : state.mode === 'guided'
                                        ? ' dim'
                                        : ' soft';
                                return (
                                    <div
                                        key={obj.id}
                                        className={`surface${role}`}
                                        data-testid={`object-${obj.id}`}
                                        data-object-id={obj.id}
                                        style={
                                            {
                                                left: b[0],
                                                top: b[1],
                                                width: b[2],
                                                height: b[3],
                                                '--i': i,
                                            } as CSSProperties
                                        }
                                        onDoubleClick={() => focusObject(obj.id)}
                                    >
                                        <Thumbnail
                                            id={obj.id}
                                            page={page}
                                            renderer={renderer}
                                            onReady={bumpThumbs}
                                        />
                                    </div>
                                );
                            })}
                            <canvas
                                ref={detail}
                                width={1}
                                height={1}
                                className="detail"
                                data-testid="detail"
                                style={{
                                    display: detailBox && detailMatchesPage ? 'block' : 'none',
                                    left: detailBox?.[0],
                                    top: detailBox?.[1],
                                    width: detailBox?.[2],
                                    height: detailBox?.[3],
                                }}
                            />
                            <canvas
                                ref={ghost}
                                width={1}
                                height={1}
                                className={`ghost-layer${ghostBox?.fading ? ' fading' : ''}`}
                                aria-hidden="true"
                                style={{
                                    display: ghostBox ? 'block' : 'none',
                                    left: ghostBox?.box[0],
                                    top: ghostBox?.box[1],
                                    width: ghostBox?.box[2],
                                    height: ghostBox?.box[3],
                                }}
                            />
                            {activeObject && activeBox && (
                                <div
                                    className="media-surface"
                                    style={{
                                        left: activeBox[0],
                                        top: activeBox[1],
                                        width: activeBox[2],
                                        height: activeBox[3],
                                    }}
                                >
                                    {placements.map((p) => (
                                        <Movie
                                            key={`${activeObject.id}:${p.page_index}:${p.annotation_index}`}
                                            placement={p}
                                            objectId={activeObject.id}
                                            selected={selected === p.annotation_index}
                                            choose={() =>
                                                setChosen((s) => ({
                                                    ...s,
                                                    [objectPage]: p.annotation_index,
                                                }))
                                            }
                                            controller={media}
                                            restore={state.restoreMedia}
                                            pdf={pdf}
                                            status={status}
                                        />
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                    <Route
                        points={stepPoints}
                        camera={camera}
                        size={size}
                        current={state.anchor?.step ?? state.step}
                        visible={state.mode === 'overview'}
                        jump={(index) => act('step', String(index))}
                    />
                    <div className="hud" data-testid="position">
                        <span className={`mode ${state.mode}`}>{state.mode}</span>{' '}
                        <span>
                            step {state.step + 1}/{path.steps.length}
                        </span>{' '}
                        <span className="view-id">{state.viewId}</span>
                        {activeObject ? (
                            <>
                                {' '}
                                <span>
                                    overlay {state.overlays[activeObject.id] + 1}/
                                    {frame!.page_indices.length}
                                </span>
                            </>
                        ) : null}
                    </div>
                    {state.mode !== 'guided' && (
                        <div className="detour">
                            {state.mode === 'overview' ? (
                                <span>Click a number to jump · a frame to look closer</span>
                            ) : (
                                <span>
                                    Exploring
                                    {anchorStep ? ` · → resumes step ${anchorStep}` : ''}
                                </span>
                            )}
                            {state.mode === 'exploring' && state.anchor ? (
                                <button onClick={() => act('next')}>Resume</button>
                            ) : state.history.length ? (
                                <button onClick={() => act('escape')}>Back</button>
                            ) : null}
                        </div>
                    )}
                    {(error || state.notice) && (
                        <div role="alert" className="toast">
                            {error || state.notice}
                        </div>
                    )}
                    {showMinimap && (
                        <Minimap
                            project={project}
                            camera={camera}
                            size={size}
                            activeId={activeObject?.id}
                            points={stepPoints}
                            pick={focusObject}
                        />
                    )}
                    <nav className="dock" aria-label="Presentation controls">
                        <button
                            className="nav"
                            onClick={() => act('previous')}
                            aria-label="Previous"
                            data-tip="Previous  ←"
                        >
                            <Icon name="prev" size={22} />
                        </button>
                        <div className="counter">
                            <div className="count">
                                <b>{state.step + 1}</b>
                                <span>/ {path.steps.length}</span>
                            </div>
                            {segmented ? (
                                <div className="segments">
                                    {path.steps.map((s, i) => (
                                        <i
                                            key={s.id}
                                            className={i < state.step ? 'done' : ''}
                                            style={
                                                i === state.step
                                                    ? ({
                                                          '--fill':
                                                              (overlayIndex + 1) / overlayCount,
                                                      } as CSSProperties)
                                                    : undefined
                                            }
                                            data-current={i === state.step || undefined}
                                        />
                                    ))}
                                </div>
                            ) : (
                                <div className="segments">
                                    <i
                                        data-current
                                        style={{ '--fill': progress } as CSSProperties}
                                    />
                                </div>
                            )}
                        </div>
                        <button
                            className="nav"
                            onClick={() => act('next')}
                            aria-label="Next"
                            data-tip="Next  →"
                        >
                            <Icon name="next" size={22} />
                        </button>
                        <span className="divider" />
                        <button
                            onClick={() => act('overview')}
                            aria-label="Overview"
                            aria-pressed={state.mode === 'overview'}
                            data-tip="Overview  O"
                        >
                            <Icon name="overview" />
                        </button>
                        <button
                            onClick={() => act('escape')}
                            disabled={!state.history.length}
                            aria-label="Return"
                            data-tip="Return  Esc"
                        >
                            <Icon name="back" />
                            {state.history.length > 0 && (
                                <span className="badge">{state.history.length}</span>
                            )}
                        </button>
                        <span className="divider" />
                        <button
                            onClick={() => setViewsOpen((v) => !v)}
                            aria-label="Views"
                            aria-pressed={viewsOpen}
                            data-tip="Views  V"
                        >
                            <Icon name="views" />
                        </button>
                        <button
                            onClick={() => setMinimapPref(!showMinimap)}
                            aria-label="Minimap"
                            aria-pressed={showMinimap}
                            data-tip="Minimap  M"
                        >
                            <Icon name="map" />
                        </button>
                        {project.layout.paths.length > 1 && (
                            <label className="path" data-tip="Path">
                                <Icon name="route" />
                                <select
                                    value={state.pathId}
                                    onChange={(e) => act('path', e.target.value)}
                                    aria-label="Path"
                                >
                                    {project.layout.paths.map((p) => (
                                        <option key={p.id}>{p.id}</option>
                                    ))}
                                </select>
                            </label>
                        )}
                        <button
                            onClick={toggleFullscreen}
                            aria-label="Fullscreen"
                            data-tip="Fullscreen  F"
                        >
                            <Icon name="expand" />
                        </button>
                        <button
                            onClick={() => setHelp((v) => !v)}
                            aria-label="Help"
                            aria-pressed={help}
                            data-tip="Shortcuts  ?"
                        >
                            <Icon name="help" />
                        </button>
                    </nav>
                </div>
                {viewsOpen && (
                    <ViewsDrawer
                        project={project}
                        pathSteps={path.steps}
                        currentView={state.viewId}
                        version={thumbs}
                        focus={(id) => act('focus', id)}
                    />
                )}
            </div>
            {help && <HelpSheet close={() => setHelp(false)} />}
        </div>
    );
}

function App() {
    const [loaded, setLoaded] = useState<{ project: Project; pdf: PDFDocumentProxy } | null>(null),
        [error, setError] = useState('');
    useEffect(() => {
        void (async () => {
            const response = await fetch('/api/project');
            if (!response.ok) throw new Error('Could not load presentation');
            const project = parseProject(await response.json());
            const pdf = await openPdf(project.pdf_url);
            if (pdf.numPages !== project.pages.length)
                throw new Error('PDF page inventory mismatch');
            setLoaded({ project, pdf });
        })().catch((e) => setError(String(e)));
    }, []);
    return error ? (
        <main role="alert" className="splash error">
            <div className="splash-card">
                <strong>Could not open this presentation</strong>
                <p>{error}</p>
            </div>
        </main>
    ) : loaded ? (
        <Viewer {...loaded} />
    ) : (
        <main role="status" className="splash">
            <div className="logo" aria-hidden="true">
                <i />
                <i />
                <i />
            </div>
            <p>Loading presentation…</p>
        </main>
    );
}
createRoot(document.getElementById('root')!).render(<App />);
