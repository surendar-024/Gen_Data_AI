
import json

def verify():
    try:
        with open('final_system_test.json', 'rb') as f:
            content = f.read().decode('utf-16')
            s = json.loads(content)
        
        cols = s.get('columns', [])
        print(f"{'COLUMN':<15} | {'MIN':<7} | {'MAX':<7} | {'DIST':<8} | {'PREFIX':<10} | {'SUFFIX':<10} | {'PATTERN':<15} | {'NULL':<5}")
        print("-" * 110)
        for col in cols:
            name = col.get('name', 'N/A')
            mi = col.get('min', '-')
            ma = col.get('max', '-')
            di = col.get('distribution', '-')
            pre = col.get('prefix', '-')
            su = col.get('suffix', '-')
            pa = col.get('pattern_sample', '-')
            nu = col.get('null_chance', '-')
            print(f"{name:<15} | {mi:<7} | {ma:<7} | {di:<8} | {pre:<10} | {su:<10} | {pa:<15} | {nu:<5}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
