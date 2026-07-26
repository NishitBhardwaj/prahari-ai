import os, re

pages = []
base_dir = r"src\app\(admin)\cases\[id]"
for root, _, files in os.walk(base_dir):
    for f in files:
        if f.endswith("page.tsx") or f.endswith("layout.tsx"):
            pages.append(os.path.join(root, f))

for p in pages:
    content = open(p, 'r', encoding='utf-8').read()
    if '"use client"' in content:
        # Remove all instances of "use client" (with or without semicolons or quotes)
        content = re.sub(r'[\'"]use client[\'"][;\n]*', '', content).strip()
        # Prepend exactly once
        content = '"use client"\n\n' + content
        open(p, 'w', encoding='utf-8').write(content)
        print('Fixed use client in', p)
