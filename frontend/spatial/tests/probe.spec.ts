import { test, expect } from '@playwright/test';
import { mkdirSync, writeFileSync } from 'node:fs';

for (const adapter of ['dom', 'flow']) {
    test(`real PDF and media with ${adapter}`, async ({ page }) => {
        const cdp = await page.context().newCDPSession(page);
        await cdp.send('Performance.enable');
        const initialMetrics = await cdp.send('Performance.getMetrics');
        const external: string[] = [];
        page.on('request', (request) => {
            if (!/^(http:\/\/127\.0\.0\.1:5173|blob:|data:)/.test(request.url()))
                external.push(request.url());
        });
        await page.goto(`http://127.0.0.1:5173/probe.html?adapter=${adapter}`);
        await expect(page.getByTestId('status')).toHaveText(`${adapter}: ready`, {
            timeout: 45_000,
        });
        await page.evaluate(async () => {
            await (window as any).__probe.focus();
        });
        const video = page.locator('#probe-video');
        await video.evaluate((v: HTMLVideoElement) => {
            (window as any).__originalVideo = v;
        });
        await video.click();
        await video.evaluate((v: HTMLVideoElement) => v.play());
        await expect
            .poll(() => video.evaluate((v: HTMLVideoElement) => v.currentTime))
            .toBeGreaterThan(0.2);
        const before = await video.evaluate((v: HTMLVideoElement) => v.currentTime);
        const movementStart = performance.now();
        for (let n = 0; n < 10; n++)
            await page.evaluate(async () => {
                await (window as any).__probe.move();
            });
        const tenCommandRoundtripMs = performance.now() - movementStart;
        expect(await video.evaluate((v) => v === (window as any).__originalVideo)).toBe(true);
        await expect
            .poll(() => video.evaluate((v: HTMLVideoElement) => v.currentTime))
            .toBeGreaterThan(before);
        for (const index of [1, 2, 1, 0])
            await page.evaluate((i) => (window as any).__probe.overlay(i), index);
        expect(await video.evaluate((v) => v === (window as any).__originalVideo)).toBe(true);
        const geometry = await page.evaluate(() => (window as any).__probe.geometry());
        expect(geometry.rotation).toBe(90);
        expect(geometry.cornerError).toBeLessThanOrEqual(1);
        for (const [i, expected] of [0.2, 0.2, 120 / 225, 0.5].entries())
            expect(geometry.rect[i]).toBeCloseTo(expected, 8);
        expect(geometry.rect.every((x: number) => Number.isFinite(x))).toBe(true);
        expect(external).toEqual([]);
        const metrics = await page.evaluate(() => (window as any).__probe.metrics());
        const finalMetrics = await cdp.send('Performance.getMetrics');
        const metric = (list: { name: string; value: number }[], key: string) =>
            list.find((m) => m.name === key)!.value;
        const diagnostic = {
            mainThreadTaskSeconds:
                metric(finalMetrics.metrics, 'TaskDuration') -
                metric(initialMetrics.metrics, 'TaskDuration'),
            jsHeapUsedBytes: metric(finalMetrics.metrics, 'JSHeapUsedSize'),
            tenCommandRoundtripMs,
            cacheState: 'fresh browser context; shared OS and Vite caches uncontrolled',
        };
        expect(metrics.nodes).toBe(40);
        expect(metrics.mounts).toBe(40);
        mkdirSync('../../build/spatial-evidence/s2', { recursive: true });
        writeFileSync(
            `../../build/spatial-evidence/s2/${adapter}.json`,
            JSON.stringify(
                {
                    ...metrics,
                    diagnostic,
                    geometry,
                    external,
                    browser: await page.context().browser()!.version(),
                    viewport: page.viewportSize(),
                    devicePixelRatio: await page.evaluate(() => devicePixelRatio),
                },
                null,
                2,
            ),
        );
        await page.screenshot({ path: `../../build/spatial-evidence/s2/${adapter}.png` });
        if (adapter === 'dom') {
            const text = await page.evaluate(() => (window as any).__probe.proof());
            expect(text).toContain('Scattering model');
            await page
                .locator('#proof')
                .screenshot({ path: '../../build/spatial-evidence/s2/science.png' });
            await page.evaluate(() => (window as any).__probe.proof(true));
            await page
                .locator('#proof')
                .screenshot({ path: '../../build/spatial-evidence/s2/rotated.png' });
        }
    });
}
