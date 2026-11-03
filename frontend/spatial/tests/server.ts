import type { Page } from '@playwright/test';
import { spawn, type ChildProcess } from 'node:child_process';
import { resolve } from 'node:path';

/** Starts `beamerpkg spatial` on a fixture archive and blocks non-loopback requests. */
export async function startServer(archive: string, page: Page) {
    const server: ChildProcess = spawn(
        'poetry',
        ['run', 'beamerpkg', 'spatial', archive, '--no-browser'],
        { cwd: resolve('../..'), stdio: ['pipe', 'pipe', 'pipe'] },
    );
    const endpoint = await new Promise<string>((res, rej) => {
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
    const stop = async () => {
        if (server.exitCode !== null) return;
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
    };
    return { endpoint, stop };
}
