import type { PDFDocumentProxy, RenderTask } from 'pdfjs-dist';
import type { Box } from './model';

type Job = {
    key: string;
    page: number;
    canvas: HTMLCanvasElement;
    scale: number;
    clip: Box;
    pixels: number;
    done?: () => void;
};
/** One render at a time. All thumbnails together stay within 18.5M pixels
 * (`thumbnailBudget`: at most 1M each, sharper flights for small decks) and
 * three <=4M-pixel buffers exist at most: detail, its offscreen replacement and
 * the overlay crossfade ghost. At most 48 viewpoint previews add <=1M pixels. This bounds
 * canvas RGBA below 128 MiB. It does not bound browser/worker total RAM.
 */
export function thumbnailBudget(objects: number): number {
    return Math.max(1, Math.min(1_000_000, Math.floor(18_500_000 / Math.max(1, objects))));
}
export class Renderer {
    private queue = new Map<string, Job>();
    private current: { job: Job; task: RenderTask | null; cancelled: boolean } | null = null;
    private stopped = false;
    constructor(
        private pdf: PDFDocumentProxy,
        private error: (message: string) => void,
        private thumbnailPixels = 60_000,
    ) {}
    request(
        key: string,
        page: number,
        canvas: HTMLCanvasElement,
        scale: number,
        clip: Box = [0, 0, 1, 1],
        done?: () => void,
    ): void {
        const job = {
            key,
            page,
            canvas,
            scale,
            clip,
            pixels: key === 'detail' ? 4_000_000 : this.thumbnailPixels,
            done,
        };
        this.queue.set(key, job);
        if (this.current?.job.key === key) {
            this.current.cancelled = true;
            this.current.task?.cancel();
        }
        void this.pump();
    }
    cancelDetail(): void {
        this.queue.delete('detail');
        if (this.current?.job.key === 'detail') {
            this.current.cancelled = true;
            this.current.task?.cancel();
        }
    }
    stop(): void {
        this.stopped = true;
        this.queue.clear();
        this.current?.task?.cancel();
    }
    private async pump(): Promise<void> {
        if (this.current || this.stopped || !this.queue.size) return;
        const job = this.queue.get('detail') ?? this.queue.values().next().value!;
        this.queue.delete(job.key);
        this.current = { job, task: null, cancelled: false };
        let buffer: HTMLCanvasElement | null = null;
        try {
            const page = await this.pdf.getPage(job.page + 1),
                base = page.getViewport({ scale: 1 });
            let scale = job.scale;
            scale = Math.min(
                scale,
                Math.sqrt(job.pixels / (base.width * job.clip[2] * base.height * job.clip[3])),
                8192 / (base.width * job.clip[2]),
                8192 / (base.height * job.clip[3]),
            );
            const viewport = page.getViewport({ scale });
            buffer = document.createElement('canvas');
            buffer.width = Math.max(1, Math.floor(viewport.width * job.clip[2]));
            buffer.height = Math.max(1, Math.floor(viewport.height * job.clip[3]));
            if (this.stopped || this.current.cancelled || this.queue.has(job.key)) return;
            const task = page.render({
                canvas: buffer,
                viewport,
                transform: [
                    1,
                    0,
                    0,
                    1,
                    -viewport.width * job.clip[0],
                    -viewport.height * job.clip[1],
                ],
            });
            this.current.task = task;
            await task.promise;
            if (
                !this.stopped &&
                !this.current.cancelled &&
                !this.queue.has(job.key) &&
                job.canvas.isConnected
            ) {
                job.canvas.width = buffer.width;
                job.canvas.height = buffer.height;
                job.canvas.getContext('2d')!.drawImage(buffer, 0, 0);
                job.canvas.dataset.page = String(job.page);
                job.done?.();
            }
            page.cleanup();
        } catch (e) {
            if (!(e instanceof Error && e.name === 'RenderingCancelledException'))
                this.error(String(e));
        } finally {
            if (buffer) buffer.width = buffer.height = 0;
            this.current = null;
            void this.pump();
        }
    }
}
