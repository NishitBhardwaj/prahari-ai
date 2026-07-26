import os, glob, re

pages = glob.glob('src/app/(admin)/cases/[id]/**/page.tsx', recursive=True) + ['src/app/(admin)/cases/[id]/layout.tsx']

for p in pages:
    content = open(p, 'r', encoding='utf-8').read()
    if 'params: { id: string }' in content:
        print('Patching', p)
        if 'use client' in content or p.endswith('layout.tsx'):
            if 'import { use } from "react"' not in content:
                content = 'import { use } from "react"\n' + content
            content = content.replace('params: { id: string }', 'params: Promise<{ id: string }>')
            content = re.sub(r'params\.id', r'use(params).id', content)
        else:
            content = content.replace('params: { id: string }', 'params: Promise<{ id: string }>')
            content = content.replace('export default function', 'export default async function')
            content = re.sub(r'params\.id', r'(await params).id', content)
        open(p, 'w', encoding='utf-8').write(content)
