import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
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
} from './model';
import { initial, navigate, type Action, type Bookmark, type Camera } from './navigation';
import { openPdf, rectangle } from './pdf';
import { Renderer } from './rendering';
import { MediaController } from './media';
import './style.css';

type Size = { width: number; height: number };
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
function Thumbnail({
    id,
    page,
    pdf,
    renderer,
}: {
    id: string;
    page: number;
    pdf: PDFDocumentProxy;
    renderer: Renderer;
}) {
    const ref = useRef<HTMLCanvasElement>(null);
    const [ready, setReady] = useState(false);
    useEffect(() => {
        let current = true;
        setReady(false);
        void pdf.getPage(page + 1).then((p) => {
            if (current && ref.current)
                renderer.request(
                    id,
                    page,
                    ref.current,
                    320 / p.getViewport({ scale: 1 }).width,
                    [0, 0, 1, 1],
                    () => {
                        if (current) setReady(true);
                    },
                );
        });
        return () => {
            current = false;
        };
    }, [id, page, pdf, renderer]);
    return (
        <>
            <canvas
                ref={ref}
                width={1}
                height={1}
                className="thumbnail"
                data-object={id}
                aria-label={`PDF page ${page + 1}`}
            />
            {!ready && <span className="loading">Loading page {page + 1}…</span>}
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
    return (
        <div
            className="movie"
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
            <div className="movie-controls">
                <button
                    onClick={() => {
                        if (selected) void controller.play();
                        else choose();
                    }}
                    aria-label="Play video"
                >
                    Play
                </button>
                <button onClick={() => controller.pause()} aria-label="Pause video">
                    Pause
                </button>
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

function Viewer({ project, pdf }: { project: Project; pdf: PDFDocumentProxy }) {
    const [state, setState] = useState(() => initial(project.layout));
    const [camera, setCamera] = useState<Camera>({ cx: 0, cy: 0, zoom: 1 });
    const cameraRef = useRef(camera);
    cameraRef.current = camera;
    const [size, setSize] = useState<Size>({ width: 1, height: 1 });
    const stage = useRef<HTMLDivElement>(null),
        detail = useRef<HTMLCanvasElement>(null);
    const [error, setError] = useState(''),
        [status, setStatus] = useState('Ready');
    const [viewsOpen, setViewsOpen] = useState(false),
        [help, setHelp] = useState(false);
    const [chosen, setChosen] = useState<Record<string, number>>({});
    const [renderer] = useState(() => new Renderer(pdf, setError));
    const [media] = useState(() => new MediaController(setStatus));
    const motion = useRef(0),
        request = useRef(-1);
    const animating = useRef(false),
        pendingRestore = useRef<Camera | null>(null);
    const drag = useRef<{ x: number; y: number; moved: boolean } | null>(null);
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
        const target =
            pendingRestore.current ??
            fit(
                state.mode === 'overview' ? worldBox(project) : viewBox(project, view),
                size,
                view.padding,
            );
        cancelAnimationFrame(motion.current);
        if (!size.width || size.width <= 1) return;
        const from = cameraRef.current,
            start = performance.now();
        const duration =
            matchMedia('(prefers-reduced-motion: reduce)').matches ||
            (!currentRequest && !continuing)
                ? 0
                : 240;
        animating.current = duration > 0;
        const tick = (now: number) => {
            const t = duration ? Math.min(1, (now - start) / duration) : 1;
            const k = t * t * (3 - 2 * t);
            setCamera({
                cx: from.cx + (target.cx - from.cx) * k,
                cy: from.cy + (target.cy - from.cy) * k,
                zoom: from.zoom + (target.zoom - from.zoom) * k,
            });
            if (t < 1) motion.current = requestAnimationFrame(tick);
            else animating.current = false;
        };
        motion.current = requestAnimationFrame(tick);
        return () => cancelAnimationFrame(motion.current);
    }, [state.cameraRequest, size, project]);
    useEffect(() => {
        const handler = (e: KeyboardEvent) => {
            if (
                e.target instanceof HTMLElement &&
                (e.target.closest('select,input,textarea,video') ||
                    (e.key === ' ' && e.target.closest('button')))
            )
                return;
            const command = (
                {
                    ArrowRight: 'next',
                    ' ': 'next',
                    ArrowLeft: 'previous',
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
    }, [act, media]);
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
    const activeGeneration = useRef(0);
    useEffect(() => {
        renderer.cancelDetail();
        const generation = ++activeGeneration.current;
        if (!activeObject || !activeBox || !clip || !detail.current) {
            setDetailBox(null);
            if (detail.current) detail.current.width = detail.current.height = 1;
            return;
        }
        const timer = setTimeout(() => {
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
                        if (generation === activeGeneration.current)
                            setDetailBox([
                                activeBox[0] + clip[0] * activeBox[2],
                                activeBox[1] + clip[1] * activeBox[3],
                                clip[2] * activeBox[2],
                                clip[3] * activeBox[3],
                            ]);
                    },
                );
            });
        }, 100);
        return () => {
            clearTimeout(timer);
            renderer.cancelDetail();
        };
    }, [activePage, activeObject?.id, camera, size, renderer, pdf]);
    // A detail tile for a previous physical page must never cover the new overlay.
    const detailMatchesPage = detail.current?.dataset.page === String(activePage);
    const path = project.layout.paths.find((p) => p.id === state.pathId)!;
    const beginGesture = () => {
        cancelAnimationFrame(motion.current);
        animating.current = false;
        pendingRestore.current = null;
        if (stateRef.current.mode !== 'exploring') act('pan');
    };
    return (
        <div className="app">
            <header>
                <strong>beamerpkg spatial</strong>
                <button onClick={() => act('previous')} aria-label="Previous">
                    ←
                </button>
                <button onClick={() => act('next')} aria-label="Next">
                    →
                </button>
                <button onClick={() => act('overview')}>Overview</button>
                <button onClick={() => act('escape')} disabled={!state.history.length}>
                    Return
                </button>
                <label>
                    Path{' '}
                    <select value={state.pathId} onChange={(e) => act('path', e.target.value)}>
                        {project.layout.paths.map((p) => (
                            <option key={p.id}>{p.id}</option>
                        ))}
                    </select>
                </label>
                <span data-testid="position">
                    {state.mode} · {state.step + 1}/{path.steps.length} · {state.viewId}
                    {activeObject
                        ? ` · overlay ${state.overlays[activeObject.id] + 1}/${frame!.page_indices.length}`
                        : ''}
                </span>
                <button onClick={() => setViewsOpen((v) => !v)}>Views</button>
                <button onClick={() => setHelp((v) => !v)}>Help</button>
            </header>
            {help && (
                <div className="help">
                    Arrow keys / Space: overlays then path. Drag or wheel: explore. O: overview.
                    Escape / Return: back one detour. Use Views to focus a detail. Layout editing is
                    not included in this prototype.
                </div>
            )}
            {(error || state.notice) && (
                <div role="alert" className="alert">
                    {error || state.notice}
                </div>
            )}
            <div className="workspace">
                <div
                    ref={stage}
                    className="stage"
                    tabIndex={0}
                    aria-label="Presentation canvas"
                    onPointerDown={(e) => {
                        if (
                            e.button !== 0 ||
                            (e.target as HTMLElement).closest('button,select,video,a')
                        )
                            return;
                        e.currentTarget.focus();
                        drag.current = { x: e.clientX, y: e.clientY, moved: false };
                        e.currentTarget.setPointerCapture(e.pointerId);
                    }}
                    onPointerMove={(e) => {
                        const d = drag.current;
                        if (!d || (!d.moved && Math.hypot(e.clientX - d.x, e.clientY - d.y) < 3))
                            return;
                        if (!d.moved) beginGesture();
                        setCamera((c) => ({
                            ...c,
                            cx: c.cx - (e.clientX - d.x) / c.zoom,
                            cy: c.cy - (e.clientY - d.y) / c.zoom,
                        }));
                        drag.current = { x: e.clientX, y: e.clientY, moved: true };
                    }}
                    onPointerUp={() => {
                        drag.current = null;
                    }}
                    onPointerCancel={() => {
                        drag.current = null;
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
                        style={{
                            transform: `translate(${size.width / 2 - camera.cx * camera.zoom}px,${size.height / 2 - camera.cy * camera.zoom}px) scale(${camera.zoom})`,
                        }}
                    >
                        {project.layout.objects.map((obj) => {
                            const b = objectBox(project, obj),
                                f = project.layout.frames.find((f) => f.id === obj.frame_id)!,
                                page = f.page_indices[state.overlays[obj.id]];
                            return (
                                <div
                                    key={obj.id}
                                    className="surface"
                                    data-testid={`object-${obj.id}`}
                                    style={{ left: b[0], top: b[1], width: b[2], height: b[3] }}
                                    onDoubleClick={() => {
                                        const v = project.layout.viewpoints.find(
                                            (v) =>
                                                v.target.kind === 'object' &&
                                                v.target.object_id === obj.id,
                                        );
                                        if (v) act('focus', v.id);
                                    }}
                                >
                                    <Thumbnail
                                        id={obj.id}
                                        page={page}
                                        pdf={pdf}
                                        renderer={renderer}
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
                {viewsOpen && (
                    <aside aria-label="Viewpoints">
                        {project.layout.viewpoints.map((v) => (
                            <button key={v.id} onClick={() => act('focus', v.id)}>
                                {v.id}
                            </button>
                        ))}
                    </aside>
                )}
            </div>
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
        <main role="alert">{error}</main>
    ) : loaded ? (
        <Viewer {...loaded} />
    ) : (
        <main role="status">Loading presentation…</main>
    );
}
createRoot(document.getElementById('root')!).render(<App />);
