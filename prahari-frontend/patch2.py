import os, re

# Traverse directory manually
pages = []
base_dir = r"src\app\(admin)\cases\[id]"
for root, _, files in os.walk(base_dir):
    for f in files:
        if f.endswith("page.tsx") or f.endswith("layout.tsx"):
            pages.append(os.path.join(root, f))

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
