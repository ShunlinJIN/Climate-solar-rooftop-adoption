import csv, shutil
from _paths import package_paths
ROOT, DATA, OUT = package_paths(__file__)
T=OUT/"tables"; T.mkdir(parents=True,exist_ok=True)
ready=[1,2,3,4,5,6,8,9,10,11,16,17,19,20,21,22,23,24,26,27,30,31,35]
for n in ready:
    matches=sorted(DATA.glob(f"supp_table{n:02d}*.csv"))
    if not matches: raise FileNotFoundError(f"No source CSV for Supplementary Table {n}")
    for src in matches:
        with open(src,encoding="utf-8-sig",newline="") as f:
            rd=csv.reader(f); header=next(rd,None); first=next(rd,None)
        if not header or first is None: raise ValueError(f"Invalid/empty CSV: {src.name}")
        shutil.copy2(src,T/src.name.replace("supp_table","Supplementary_Table_"))
print(f"Validated/exported aggregate source CSVs for {len(ready)} Supplementary Tables.")
