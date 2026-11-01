import { getDocument, GlobalWorkerOptions, type PDFDocumentProxy, type PDFPageProxy } from 'pdfjs-dist';
import worker from 'pdfjs-dist/build/pdf.worker.min.mjs?url';

GlobalWorkerOptions.workerSrc = worker;
export async function openPdf(url: string): Promise<PDFDocumentProxy> {
  return getDocument({ url, cMapUrl: '/pdfjs/cmaps/', cMapPacked: true, standardFontDataUrl: '/pdfjs/standard_fonts/', iccUrl: '/pdfjs/iccs/', wasmUrl: '/pdfjs/wasm/' }).promise;
}
export function rectangle(page: PDFPageProxy, rect: number[]): number[] {
  const vp = page.getViewport({ scale: 1 });
  const a = vp.convertToViewportPoint(rect[0], rect[1]);
  const b = vp.convertToViewportPoint(rect[2], rect[3]);
  return [Math.min(a[0], b[0]) / vp.width, Math.min(a[1], b[1]) / vp.height, Math.abs(a[0] - b[0]) / vp.width, Math.abs(a[1] - b[1]) / vp.height];
}
export async function thumbnail(page: PDFPageProxy): Promise<string> {
  const scale = 320 / page.getViewport({ scale: 1 }).width;
  const vp = page.getViewport({ scale });
  const canvas = document.createElement('canvas');
  canvas.width = Math.ceil(vp.width); canvas.height = Math.ceil(vp.height);
  await page.render({ canvas, viewport: vp }).promise;
  const url = URL.createObjectURL(await new Promise<Blob>(resolve => canvas.toBlob(b => resolve(b!), 'image/png')));
  canvas.width = canvas.height = 0;
  return url;
}
