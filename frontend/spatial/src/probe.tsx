import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ReactFlow, type ReactFlowInstance, type NodeProps, type Node } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { openPdf, rectangle, thumbnail } from './pdf';

type PageData = { image: string; rect?: number[]; url?: string; height: number };
type PageNode = Node<PageData>;
let mounts = 0;
function Surface({ data }: { data: PageData }) {
  useEffect(() => { mounts++; }, []);
  return <div style={{ position: 'relative', width: 320, height: data.height }}>
    <img src={data.image} style={{ width: '100%', height: '100%' }} />
    {data.url && <video id="probe-video" controls loop src={data.url} className="nodrag nopan nowheel" style={{ position: 'absolute', left: `${data.rect![0] * 100}%`, top: `${data.rect![1] * 100}%`, width: `${data.rect![2] * 100}%`, height: `${data.rect![3] * 100}%` }} />}
  </div>;
}
function Page({ data }: NodeProps<PageNode>) { return <Surface data={data} />; }
const types = { page: Page };

function Probe() {
  const adapter = new URLSearchParams(location.search).get('adapter') ?? 'dom';
  const [nodes, setNodes] = useState<PageNode[]>([]);
  const [status, setStatus] = useState('loading');
  const [pose, setPose] = useState({ x: 10, y: 60, zoom: .5 });
  const [flow, setFlow] = useState<ReactFlowInstance<PageNode> | null>(null);
  const [drag, setDrag] = useState<{ x: number; y: number } | null>(null);
  useEffect(() => { void (async () => {
    const start = performance.now();
    const project = await (await fetch('/_probe/stress.json')).json();
    const pdf = await openPdf(project.pdf_url);
    const pages: PageNode[] = [];
    for (let i = 0; i < pdf.numPages; i++) {
      const page = await pdf.getPage(i + 1);
      const p = project.placements.find((p: { page_index: number }) => p.page_index === i);
      pages.push({ id: `p${i}`, type: 'page', position: { x: (i % 5) * 360, y: Math.floor(i / 5) * 220 }, data: { image: await thumbnail(page), height: 320 * page.getViewport({ scale: 1 }).height / page.getViewport({ scale: 1 }).width, ...(i === 17 && p ? { rect: rectangle(page, p.rect_pdf), url: p.url } : {}) } });
    }
    await pdf.loadingTask.destroy();
    setNodes(pages); setStatus('ready');
    (window as any).__probeLoadMs = performance.now() - start;
  })().catch(e => setStatus(String(e))); }, []);
  useEffect(() => {
    (window as any).__probe = {
      focus: async () => {
        if (adapter === 'flow') await flow?.fitBounds({ x: 720, y: 660, width: 320, height: 180 }, { padding: .1, duration: 0 });
        else setPose({ x: 640 - 880 * 2, y: 400 - 750 * 2, zoom: 2 });
      },
      move: async () => {
        if (adapter === 'flow') { const p = flow!.getViewport(); await flow!.setViewport({ x: p.x + 30, y: p.y + 20, zoom: p.zoom * 1.1 }); }
        else setPose(p => ({ x: p.x + 30, y: p.y + 20, zoom: p.zoom * 1.1 }));
      },
      overlay: (index: number) => setNodes(current => current.map(n => n.id === 'p14' ? { ...n, data: { ...n.data, image: nodes[14 + index].data.image } } : n)),
      metrics: () => ({ adapter, nodes: nodes.length, mounts, loadMs: (window as any).__probeLoadMs, thumbnailPixelBytes: nodes.reduce((n, p) => n + 320 * p.data.height * 4, 0) }),
      geometry: async () => {
        const pdf = await openPdf('/_probe/rotated.pdf'); const page = await pdf.getPage(1); const vp = page.getViewport({ scale: 1 });
        const r = rectangle(page, [100, 60, 300, 180]);
        const t = vp.transform; const x = t[0] * 100 + t[2] * 60 + t[4]; const y = t[1] * 100 + t[3] * 60 + t[5];
        const point = vp.convertToViewportPoint(100, 60); const error = Math.max(Math.abs(point[0] - x), Math.abs(point[1] - y));
        await pdf.loadingTask.destroy(); return { rotation: vp.rotation, rect: r, cornerError: error };
      },
      proof: async (rotated = false) => {
        const pdf = await openPdf(rotated ? '/_probe/rotated.pdf' : '/_probe/science.pdf');
        const page = await pdf.getPage(rotated ? 1 : 4);
        const vp = page.getViewport({ scale: Math.min(1200 / page.getViewport({ scale: 1 }).width, 740 / page.getViewport({ scale: 1 }).height) });
        const canvas = document.createElement('canvas'); canvas.id = 'proof';
        canvas.width = Math.ceil(vp.width); canvas.height = Math.ceil(vp.height);
        Object.assign(canvas.style, { position: 'fixed', top: '40px', left: '0', zIndex: '20' });
        document.querySelector('#proof')?.remove(); document.body.append(canvas);
        await page.render({ canvas, viewport: vp }).promise;
        const text = await page.getTextContent(); await pdf.loadingTask.destroy();
        return text.items.map(x => 'str' in x ? x.str : '').join(' ');
      },
    };
  }, [adapter, flow, nodes]);
  return <><div style={{ position: 'fixed', top: 0, zIndex: 5, background: 'white' }} data-testid="status">{adapter}: {status}</div>
    <div style={{ position: 'fixed', inset: 0, background: '#18232e', overflow: 'hidden' }}
      onPointerDown={e => { if (adapter === 'dom' && !(e.target instanceof HTMLVideoElement)) { e.currentTarget.setPointerCapture(e.pointerId); setDrag({ x: e.clientX, y: e.clientY }); } }}
      onPointerMove={e => { if (drag) { setPose(p => ({ ...p, x: p.x + e.clientX - drag.x, y: p.y + e.clientY - drag.y })); setDrag({ x: e.clientX, y: e.clientY }); } }}
      onPointerUp={() => setDrag(null)}
      onWheel={e => { if (adapter === 'dom' && !(e.target instanceof HTMLVideoElement)) setPose(p => { const z = Math.max(.05, Math.min(12, p.zoom * Math.exp(-e.deltaY * .001))); return { x: e.clientX - (e.clientX - p.x) * z / p.zoom, y: e.clientY - (e.clientY - p.y) * z / p.zoom, zoom: z }; }); }}>
    {adapter === 'flow' ? <ReactFlow<PageNode> nodes={nodes} nodeTypes={types} onInit={setFlow} nodesDraggable={false} nodesConnectable={false} panActivationKeyCode={null} deleteKeyCode={null} selectionKeyCode={null} minZoom={.05} maxZoom={12} /> : <div style={{ position: 'absolute', transformOrigin: '0 0', transform: `translate(${pose.x}px,${pose.y}px) scale(${pose.zoom})` }}>{nodes.map(n => <div key={n.id} style={{ position: 'absolute', left: n.position.x, top: n.position.y }}><Surface data={n.data} /></div>)}</div>}
    </div></>;
}
createRoot(document.getElementById('root')!).render(<Probe />);
