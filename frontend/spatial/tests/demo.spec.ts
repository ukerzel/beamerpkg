import { test, expect } from '@playwright/test';
import { startServer } from './server';

// The authored demo layout ends its tour on a whole-canvas (world_rect) step.
test('whole-canvas finale shows the route, flies into a clicked frame and restarts', async ({
    page,
}) => {
    const { endpoint, stop } = await startServer('build/spatial-fixtures/demo.beamerpkg', page);
    try {
        await page.emulateMedia({ reducedMotion: 'reduce' });
        await page.goto(endpoint);
        const position = page.getByTestId('position');
        await expect(position).toContainText('step 1/15 title', { timeout: 15_000 });
        await page.getByRole('button', { name: 'Overview', exact: true }).click();
        await page.getByRole('button', { name: 'Go to step 15', exact: true }).click();
        await expect(position).toContainText('guided step 15/15 canvas');
        // Previously the route and frame clicks were overview-only: a dead end.
        await expect(
            page.getByRole('button', { name: 'Go to step 14', exact: true }),
        ).toBeVisible();
        await expect(page.getByText(/End of tour/)).toBeVisible();
        const frame = (await page.getByTestId('object-try').boundingBox())!;
        await page.mouse.click(frame.x + frame.width * 0.15, frame.y + frame.height * 0.2);
        await expect(position).toContainText('exploring');
        await expect(position).toContainText(' try ');
        await page.keyboard.press('ArrowRight');
        await expect(position).toContainText('guided step 15/15 canvas');
        await page.getByRole('button', { name: 'Start over', exact: true }).click();
        await expect(position).toContainText('guided step 1/15 title');
    } finally {
        await stop();
    }
});

// Backup frames sit off the tour in their own clusters, reachable from the
// finale, from the Views drawer, and through the separate backup path.
test('backup clusters are off the tour but reachable from finale, views and path', async ({
    page,
}) => {
    const { endpoint, stop } = await startServer('build/spatial-fixtures/demo.beamerpkg', page);
    try {
        await page.emulateMedia({ reducedMotion: 'reduce' });
        await page.goto(endpoint);
        const position = page.getByTestId('position');
        await expect(position).toContainText('step 1/15 title', { timeout: 15_000 });
        await page.getByRole('button', { name: 'Overview', exact: true }).click();
        await page.getByRole('button', { name: 'Go to step 15', exact: true }).click();
        await expect(position).toContainText('guided step 15/15 canvas');
        const frame = (await page.getByTestId('object-b-paths').boundingBox())!;
        await page.mouse.click(frame.x + frame.width * 0.2, frame.y + frame.height * 0.2);
        await expect(position).toContainText(' b-paths ');
        await page.keyboard.press('ArrowRight');
        await expect(position).toContainText('guided step 15/15 canvas');

        await page.getByRole('button', { name: 'Views', exact: true }).click();
        await page
            .getByRole('complementary', { name: 'Viewpoints' })
            .getByRole('button', { name: 'backup-canvas', exact: true })
            .click();
        await expect(position).toContainText('backup-canvas');

        await page.locator('select').selectOption('backup');
        await expect(position).toContainText('guided step 1/13 backup');
        await page.keyboard.press('ArrowRight');
        await expect(position).toContainText('guided step 2/13 backup-physics');
        await page.keyboard.press('ArrowRight');
        await expect(position).toContainText('guided step 3/13 a-potential');
    } finally {
        await stop();
    }
});
