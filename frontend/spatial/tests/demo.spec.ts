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
        // Arrows on a backup frame step through its part, not back to the tour.
        const frame = (await page.getByTestId('object-a-potential').boundingBox())!;
        await page.mouse.click(frame.x + frame.width * 0.2, frame.y + frame.height * 0.2);
        await expect(position).toContainText(' a-potential ');
        await expect(page.getByText(/continues on the backup path/)).toBeVisible();
        await page.keyboard.press('ArrowRight');
        await expect(position).toContainText('guided step 4/13 a-expansion');
        await page.keyboard.press('ArrowRight');
        await expect(position).toContainText('guided step 5/13 a-numbers');
        await page.keyboard.press('ArrowLeft');
        await expect(position).toContainText('guided step 4/13 a-expansion');
        await page.getByRole('button', { name: 'Back to tour · step 15', exact: true }).click();
        await expect(position).toContainText('guided step 15/15 canvas');
        // A frame on the tour is still a plain detour: → resumes the tour. The
        // locator click waits until the restored camera has settled.
        await page.getByTestId('object-try').click({ position: { x: 25, y: 19 } });
        await expect(position).toContainText(' try ');
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
