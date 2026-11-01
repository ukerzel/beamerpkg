import type { Bookmark } from './navigation';
import type { Placement } from './model';

export class MediaController {
    private current: { id: string; video: HTMLVideoElement } | null = null;
    private positions = new Map<string, number>();
    private epoch = 0;
    private events: AbortController | null = null;
    constructor(private status: (value: string) => void) {}
    bookmark(): Bookmark {
        return this.current ? { id: this.current.id, time: this.current.video.currentTime } : null;
    }
    pause(): void {
        if (this.current) {
            this.current.video.pause();
            this.positions.set(this.current.id, this.current.video.currentTime);
            this.status('Paused');
        }
    }
    deactivate(): void {
        this.pause();
        this.events?.abort();
        this.events = null;
        this.epoch++;
        this.current = null;
    }
    activate(id: string, video: HTMLVideoElement, placement: Placement, restore: Bookmark): void {
        if (this.current?.id === id && this.current.video === video && !restore) return;
        this.deactivate();
        this.current = { id, video };
        this.events = new AbortController();
        const options = { signal: this.events.signal };
        video.addEventListener(
            'playing',
            () => {
                if (document.hidden) this.pause();
                else this.status('Playing');
            },
            options,
        );
        video.addEventListener('pause', () => this.status('Paused'), options);
        video.addEventListener(
            'error',
            () => this.status('Video unavailable: unsupported format or decode error.'),
            options,
        );
        const time =
            restore?.id === id
                ? restore.time
                : placement.autostart
                  ? 0
                  : (this.positions.get(id) ?? 0);
        const epoch = this.epoch;
        const seek = () => {
            if (epoch === this.epoch && this.current?.video === video) video.currentTime = time;
        };
        if (video.readyState) seek();
        else video.addEventListener('loadedmetadata', seek, { once: true });
        this.status('Ready');
        if (placement.autostart && !restore && !document.hidden) void this.play();
        else video.pause();
    }
    async play(): Promise<void> {
        const current = this.current,
            epoch = this.epoch;
        if (!current || document.hidden) return;
        try {
            await current.video.play();
            if (epoch !== this.epoch || document.hidden) current.video.pause();
            else this.status('Playing');
        } catch (e) {
            if (epoch === this.epoch)
                this.status(
                    e instanceof DOMException && e.name === 'NotAllowedError'
                        ? 'Playback blocked. Press Play.'
                        : `Playback unavailable. ${e instanceof Error ? e.message : String(e)}`,
                );
        }
    }
}
