"""Locate Rscript without requiring Windows users to edit PATH."""
import os
from pathlib import Path
import re
import shutil
import sys

def find_rscript():
    configured = os.environ.get('RSCRIPT', '').strip().strip('"')
    if configured:
        result = shutil.which(configured)
        if result: return result
        if Path(configured).is_file(): return str(Path(configured).resolve())
        raise RuntimeError('RSCRIPT points to a missing file: ' + configured)
    result = shutil.which('Rscript')
    if result: return result
    if os.name == 'nt':
        candidates = []
        try:
            import winreg
            for hive in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
                for key in [r'SOFTWARE\R-core\R', r'SOFTWARE\R-core\R64']:
                    try:
                        with winreg.OpenKey(hive, key) as h:
                            install = Path(winreg.QueryValueEx(h, 'InstallPath')[0])
                            candidates += [install / 'bin/Rscript.exe', install / 'bin/x64/Rscript.exe']
                    except OSError: pass
        except ImportError: pass
        roots = [Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'R',
                 Path(os.environ.get('LOCALAPPDATA', 'C:/Users/Public/AppData/Local')) / 'Programs/R']
        installations = [p for root in roots if root.exists() for p in root.glob('R-*')]
        installations.sort(key=lambda p: tuple(int(x) for x in re.findall(r'\d+',p.name)), reverse=True)
        for p in installations: candidates += [p / 'bin/Rscript.exe', p / 'bin/x64/Rscript.exe']
        for candidate in candidates:
            if candidate.is_file(): return str(candidate.resolve())
    raise RuntimeError('Rscript was not found. Install R 4.3 or newer, or set RSCRIPT to the full Rscript path.')

if __name__ == '__main__':
    try: print(find_rscript())
    except RuntimeError as exc:
        print(str(exc),file=sys.stderr)
        sys.exit(1)
