import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { parseProject } from '../src/model';

function raw() {
    const data = JSON.parse(readFileSync('public/_probe/science.json', 'utf8'));
    data.pdf_url = '/runtime/document.pdf';
    for (const [i, p] of data.placements.entries()) p.url = `/runtime/asset-${i}`;
    return data;
}
test('browser runtime validates the actual fixture payload', () => {
    expect(parseProject(raw()).pages).toHaveLength(8);
});
for (const kind of [
    'unknown',
    'reference',
    'region',
    'overlap',
    'hash',
    'nonfinite',
    'boolean-index',
    'remote-url',
]) {
    test(`browser contract rejects ${kind}`, () => {
        const data = raw();
        if (kind === 'unknown') data.layout.arbitrary_url = 'https://example.org';
        if (kind === 'reference') data.layout.objects[0].frame_id = 'missing';
        if (kind === 'region') data.layout.viewpoints[0].target.region = [0.9, 0, 0.5, 1];
        if (kind === 'overlap') data.layout.frames[1].page_indices = [0];
        if (kind === 'hash') data.layout.source.pdf_sha256 = '0'.repeat(64);
        if (kind === 'nonfinite') data.layout.objects[0].x = Infinity;
        if (kind === 'boolean-index') data.layout.frames[0].page_indices = [true];
        if (kind === 'remote-url') data.placements[0].url = 'https://example.org/video.mp4';
        expect(() => parseProject(data)).toThrow();
    });
}
