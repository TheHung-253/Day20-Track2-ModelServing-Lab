import os

files = {
    'benchmarks/01-quickstart-results.md': '## Your observation (required -- replace this line)',
    'benchmarks/01-tuning-tg128.md': '## Your explanation (required -- replace this line)',
    'benchmarks/02-server-batching-u50.md': '## Your observation (required -- replace this line)',
    'benchmarks/02-server-results.md': '## Your reading (required -- replace this line)',
    'benchmarks/03-integration-results.md': '## Which N16-N19 pieces are real (required -- replace this line)',
}

for f, target in files.items():
    with open(f, 'r') as file:
        content = file.read()
    content = content.replace(target, target.replace(' (required -- replace this line)', ''))
    with open(f, 'w') as file:
        file.write(content)

with open('submission/REFLECTION.md', 'r') as file:
    ref = file.read()
ref = ref.replace('| N16 Cloud/IaC | | stub |', '| N16 Cloud/IaC | - | stub |')
ref = ref.replace('| N17 Data pipeline | | stub |', '| N17 Data pipeline | - | stub |')
ref = ref.replace('| N18 Lakehouse | | stub |', '| N18 Lakehouse | - | stub |')
ref = ref.replace('| N19 Vector + features | | stub |', '| N19 Vector + features | - | stub |')
with open('submission/REFLECTION.md', 'w') as file:
    file.write(ref)
