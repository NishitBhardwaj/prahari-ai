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
    if 'import { use } from "react"\n"use client"' in content:
        print('Fixing use client order in', p)
        content = content.replace('import { use } from "react"\n"use client"', '"use client"\nimport { use } from "react"')
        open(p, 'w', encoding='utf-8').write(content)
