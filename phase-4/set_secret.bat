@echo off
set PYTHONIOENCODING=utf-8
python -c "
import subprocess
import sys

# Run hf command with proper encoding
result = subprocess.run(
    ['python', '-m', 'huggingface_hub', 'cli', 'set-secret', 'ammaraak/todo-backend-new', 'GEMINI_API_KEY', 'AIzaSyCWV3opImJIT_KhSyti9qdGTnxC_pPnca4', '--token', 'YmvKbo1MdR024LGd9t8CVRLR'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    timeout=60
)

print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)
print('Return code:', result.returncode)
"
