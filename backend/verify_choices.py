
import json

def check_choices():
    try:
        with open('final_system_test.json', 'rb') as f:
            content = f.read().decode('utf-16')
            s = json.loads(content)
        
        for col in s.get('columns', []):
            name = col.get('name')
            choices = col.get('choices')
            if choices:
                print(f"{name}: {choices}")
            else:
                # print(f"{name}: -")
                pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_choices()
