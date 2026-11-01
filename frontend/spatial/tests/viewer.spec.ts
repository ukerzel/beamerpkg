import { test, expect, type Page } from '@playwright/test';
import { spawn, type ChildProcess } from 'node:child_process';
import { resolve } from 'node:path';
import { mkdirSync, writeFileSync } from 'node:fs';

let server: ChildProcess, endpoint: string;
test.beforeEach(async ({ page }) => {
    server = spawn(
        'poetry',
        ['run', 'beamerpkg', 'spatial', 'build/spatial-fixtures/science.beamerpkg', '--no-browser'],
        { cwd: resolve('../..'), stdio: ['pipe', 'pipe', 'pipe'] },
    );
    endpoint = await new Promise<string>((res, rej) => {
        let output = '';
        const timeout = setTimeout(
            () => rej(new Error(`server startup timeout: ${output}`)),
            20_000,
        );
        server.stdout!.on('data', (data) => {
            output += String(data);
            const url = output.match(/http:\/\/127\.0\.0\.1:\d+\//)?.[0];
            if (url) {
                clearTimeout(timeout);
                res(url);
            }
        });
        server.stderr!.on('data', (data) => {
            output += String(data);
        });
        server.once('exit', (code) => {
            clearTimeout(timeout);
            rej(new Error(`server exit ${code}: ${output}`));
        });
    });
    await page.route('**/*', (route) =>
        route.request().url().startsWith(endpoint) ? route.continue() : route.abort(),
    );
});
test.afterEach(async () => {
    if (!server || server.exitCode !== null) return;
    server.kill('SIGINT');
    await new Promise<void>((res) => {
        const timeout = setTimeout(() => {
            server.kill('SIGTERM');
            res();
        }, 5000);
        server.once('exit', () => {
            clearTimeout(timeout);
            res();
        });
    });
});
async function open(page: Page) {
    await page.goto(endpoint);
    await expect(page.getByTestId('position')).toContainText('guided', { timeout: 15_000 });
    await expect(page.getByTestId('detail')).toHaveAttribute('data-page', '0', { timeout: 15_000 });
}
async function focus(page: Page, id: string) {
    await page.getByRole('button', { name: 'Views', exact: true }).click();
    await page
        .getByRole('complementary', { name: 'Viewpoints' })
        .getByRole('button', { name: id, exact: true })
        .click();
    await page.getByRole('button', { name: 'Views', exact: true }).click();
}

test('guided overlays, detail detours and resize restoration on bundled assets', async ({
    page,
}) => {
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));
    await open(page);
    await page.getByRole('button', { name: 'Next', exact: true }).click();
    await expect(page.getByTestId('detail')).toHaveAttribute('data-page', '1');
    const pose = await page.getByTestId('world').getAttribute('style');
    await page.keyboard.press('ArrowRight');
    await expect(page.getByTestId('position')).toContainText('overlay 2/3');
    await expect(page.getByTestId('detail')).toHaveAttribute('data-page', '2');
    expect(await page.getByTestId('world').getAttribute('style')).toBe(pose);
    await focus(page, 'detail');
    await expect(page.getByTestId('position')).toContainText('exploring');
    await page.getByRole('button', { name: 'Overview', exact: true }).click();
    await page.keyboard.press('Escape');
    await expect(page.getByTestId('position')).toContainText('exploring');
    await page.keyboard.press('ArrowRight');
    await expect(page.getByTestId('position')).toContainText('guided');
    await expect(page.getByTestId('position')).toContainText('overlay 2/3');
    await page.setViewportSize({ width: 1100, height: 760 });
    await page.keyboard.press('ArrowLeft');
    await expect(page.getByTestId('position')).toContainText('overlay 1/3');
    await expect(page.getByTestId('detail')).toHaveAttribute('data-page', '1');
    await expect(page.getByTestId('detail')).toBeVisible();
    expect(
        await page.getByTestId('detail').evaluate((c: HTMLCanvasElement) => c.width),
    ).toBeGreaterThan(700);
    await expect(page.getByRole('alert')).toHaveCount(0);
    expect(errors).toEqual([]);
    mkdirSync('../../build/spatial-evidence/s3', { recursive: true });
    await page.screenshot({ path: '../../build/spatial-evidence/s3/science-viewer.png' });
    const canvases = await page
        .locator('canvas')
        .evaluateAll((nodes: HTMLCanvasElement[]) =>
            nodes.map((n) => ({ width: n.width, height: n.height })),
        );
    expect(canvases.reduce((sum, c) => sum + c.width * c.height * 4, 0)).toBeLessThan(
        128 * 1024 ** 2,
    );
    expect(canvases.every((c) => c.width <= 8192 && c.height <= 8192)).toBe(true);
    writeFileSync('../../build/spatial-evidence/s3/buffers.json', JSON.stringify(canvases));
});

test('real video survives pan/zoom; seek, overview stop and history restore paused', async ({
    page,
}) => {
    await open(page);
    await focus(page, 'v5');
    const video = page.locator('video');
    await page.getByRole('button', { name: 'Play video', exact: true }).click();
    await expect
        .poll(() => video.evaluate((v: HTMLVideoElement) => v.currentTime))
        .toBeGreaterThan(0.2);
    await video.evaluate((v: HTMLVideoElement) => {
        (window as any).__activeVideo = v;
        v.currentTime = Math.min(1, v.duration / 2);
    });
    const zoom = Number(await page.getByTestId('world').getAttribute('data-zoom'));
    await focus(page, 'video-detail');
    await expect
        .poll(async () => Number(await page.getByTestId('world').getAttribute('data-zoom')))
        .toBeGreaterThan(zoom * 1.2);
    await page.mouse.move(50, 100);
    await page.mouse.wheel(0, -250);
    expect(await video.evaluate((v: HTMLVideoElement) => v === (window as any).__activeVideo)).toBe(
        true,
    );
    await expect.poll(() => video.evaluate((v: HTMLVideoElement) => v.paused)).toBe(false);
    await page.getByRole('button', { name: 'Overview', exact: true }).click();
    await expect
        .poll(() => page.evaluate(() => ((window as any).__activeVideo as HTMLVideoElement).paused))
        .toBe(true);
    await page.keyboard.press('Escape');
    await expect(page.locator('video')).toHaveCount(1);
    await expect
        .poll(() => page.locator('video').evaluate((v: HTMLVideoElement) => v.paused))
        .toBe(true);
    await expect
        .poll(() => page.locator('video').evaluate((v: HTMLVideoElement) => v.currentTime))
        .toBeGreaterThan(0.1);
});

test('real pdfpc-requested autoplay follows browser policy and stops on page exit', async ({
    page,
}) => {
    await open(page);
    await focus(page, 'v6');
    await expect(page.getByRole('status')).toHaveText(/Playing|Playback blocked/);
    if ((await page.getByRole('status').textContent())!.includes('blocked'))
        await page.getByRole('button', { name: 'Play video' }).click();
    await expect
        .poll(() => page.locator('video').evaluate((v: HTMLVideoElement) => v.currentTime))
        .toBeGreaterThan(0.2);
    await page.locator('video').evaluate((v: HTMLVideoElement) => {
        (window as any).__oldAutostart = v;
    });
    await focus(page, 'v7');
    await expect
        .poll(() =>
            page.evaluate(() => ((window as any).__oldAutostart as HTMLVideoElement).paused),
        )
        .toBe(true);
    await expect(page.locator('video')).toHaveCount(0);
});

test('autostart rejection has a working manual fallback, no browser-policy override', async ({
    page,
}) => {
    await page.addInitScript(() => {
        const original = HTMLMediaElement.prototype.play;
        let reject = true;
        HTMLMediaElement.prototype.play = function () {
            if (reject) {
                reject = false;
                return Promise.reject(new DOMException('Injected blocked play', 'NotAllowedError'));
            }
            return original.call(this);
        };
    });
    await open(page);
    await focus(page, 'v6');
    await expect(page.getByRole('status')).toContainText('Playback blocked');
    await page.getByRole('button', { name: 'Play video', exact: true }).click();
    await expect
        .poll(() => page.locator('video').evaluate((v: HTMLVideoElement) => v.currentTime))
        .toBeGreaterThan(0.2);
    expect(await page.locator('video').evaluate((v: HTMLVideoElement) => v.loop)).toBe(true);
    // Visibility state is injected as a separate lifecycle control, not evidence of OS tab switching.
    await page.evaluate(() => {
        Object.defineProperty(document, 'hidden', { configurable: true, value: true });
        document.dispatchEvent(new Event('visibilitychange'));
    });
    await expect
        .poll(() => page.locator('video').evaluate((v: HTMLVideoElement) => v.paused))
        .toBe(true);
    await page.evaluate(() => {
        Object.defineProperty(document, 'hidden', { configurable: true, value: false });
        document.dispatchEvent(new Event('visibilitychange'));
    });
    expect(await page.locator('video').evaluate((v: HTMLVideoElement) => v.paused)).toBe(true);
});
