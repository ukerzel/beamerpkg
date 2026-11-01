import { chromium, expect } from '@playwright/test';
import assert from 'node:assert/strict';

const [endpoint, screenshot] = process.argv.slice(2);
const browser = await chromium.launch({ headless: true });
try {
    const page = await browser.newPage({ viewport: { width: 1360, height: 900 } });
    const outside = [],
        errors = [],
        mediaRanges = [];
    await page.route('**/*', (route) => {
        if (route.request().url().startsWith(endpoint)) return route.continue();
        outside.push(route.request().url());
        return route.abort();
    });
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('response', (response) => {
        if (response.url().includes('/runtime/asset-') && response.status() === 206)
            mediaRanges.push(response.status());
    });
    await page.goto(endpoint);
    await expect(page.getByTestId('detail')).toHaveAttribute('data-page', '0', { timeout: 15_000 });
    await page.getByRole('button', { name: 'Next', exact: true }).click();
    await expect(page.getByTestId('detail')).toHaveAttribute('data-page', '1');
    await page.keyboard.press('ArrowRight');
    await expect(page.getByTestId('detail')).toHaveAttribute('data-page', '2');
    await expect(page.getByTestId('position')).toContainText('overlay 2/3');
    await page.screenshot({ path: screenshot });
    async function focus(id) {
        await page.getByRole('button', { name: 'Views', exact: true }).click();
        await page
            .getByRole('complementary', { name: 'Viewpoints' })
            .getByRole('button', { name: id, exact: true })
            .click();
        await page.getByRole('button', { name: 'Views', exact: true }).click();
    }
    await focus('v5');
    await page.getByRole('button', { name: 'Play video', exact: true }).click();
    await expect
        .poll(() => page.locator('video').evaluate((v) => v.currentTime))
        .toBeGreaterThan(0.2);
    const duration = await page.locator('video').evaluate((v) => {
        window.__wheelVideo = v;
        v.currentTime = Math.min(1, v.duration / 2);
        return v.duration;
    });
    await focus('video-detail');
    assert(await page.locator('video').evaluate((v) => v === window.__wheelVideo));
    assert(!(await page.locator('video').evaluate((v) => v.paused)));
    await page.getByRole('button', { name: 'Overview', exact: true }).click();
    assert(await page.evaluate(() => window.__wheelVideo.paused));
    await page.keyboard.press('Escape');
    await expect(page.locator('video')).toHaveCount(1);
    assert(await page.locator('video').evaluate((v) => v.paused));
    assert.equal(outside.length, 0);
    assert.equal(errors.length, 0);
    assert(mediaRanges.length > 0);
    const canvases = await page
        .locator('canvas')
        .evaluateAll((nodes) => nodes.map((c) => [c.width, c.height]));
    console.log(
        JSON.stringify({
            version: browser.version(),
            viewport: page.viewportSize(),
            devicePixelRatio: await page.evaluate(() => devicePixelRatio),
            external_network_policy:
                'all non-loopback-endpoint requests aborted; not OS network isolation',
            external_attempts: outside,
            page_errors: errors,
            actual_mp4_duration_seconds: duration,
            media_206_responses: mediaRanges.length,
            same_video_after_detail: true,
            paused_after_overview_and_restore: true,
            visible_canvas_bytes: canvases.reduce((sum, [w, h]) => sum + w * h * 4, 0),
        }),
    );
} finally {
    await browser.close();
}
