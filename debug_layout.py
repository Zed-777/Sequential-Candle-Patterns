"""Debug: Check if button and callback are properly registered."""
import sys
sys.path.insert(0, 'src')

from candle_patterns.dashboard import app

print("\n" + "="*80)
print("DASHBOARD CALLBACK REGISTRATION CHECK")
print("="*80)

# Get the layout
layout = app.layout
print(f"\n1. Layout type: {type(layout)}")

# Check callbacks on the app object
print(f"\n2. Callbacks on app object:")
if hasattr(app, '_callback_map'):
    print(f"   Found _callback_map: {len(app._callback_map)} callbacks")
    for cb in list(app._callback_map.keys())[:10]:
        print(f"   - {cb}")
else:
    print(f"   No _callback_map found")

# Check for load-sample-btn in layout
print(f"\n3. Searching layout for 'load-sample-btn'...")

def find_id_in_layout(obj, target_id, depth=0, path=""):
    """Recursively search for component with given ID."""
    if depth > 15:  # Prevent infinite recursion
        return False
    
    try:
        if hasattr(obj, 'id') and obj.id == target_id:
            print(f"   ✅ FOUND: {target_id}")
            print(f"      Path: {path}")
            print(f"      Type: {type(obj).__name__}")
            return True
        
        if hasattr(obj, 'children') and obj.children:
            children = obj.children if isinstance(obj.children, (list, tuple)) else [obj.children]
            for i, child in enumerate(children):
                if find_id_in_layout(child, target_id, depth + 1, f"{path}[{i}]"):
                    return True
    except Exception as e:
        pass
    
    return False

found = find_id_in_layout(layout, 'load-sample-btn')
if not found:
    print(f"   ❌ NOT FOUND in layout")

# Try to access the button directly if it exists
try:
    # Find all components with IDs
    print(f"\n4. Components with IDs found in layout:")
    
    def collect_ids(obj, depth=0, max_depth=8):
        """Collect all component IDs."""
        ids = []
        if depth > max_depth:
            return ids
        
        try:
            if hasattr(obj, 'id') and obj.id:
                ids.append(obj.id)
            
            if hasattr(obj, 'children') and obj.children:
                children = obj.children if isinstance(obj.children, (list, tuple)) else [obj.children]
                for child in children:
                    ids.extend(collect_ids(child, depth + 1, max_depth))
        except:
            pass
        
        return ids
    
    all_ids = collect_ids(layout)
    button_ids = [id for id in all_ids if 'btn' in id.lower() or 'button' in id.lower()]
    
    if button_ids:
        print(f"   Found {len(button_ids)} button IDs:")
        for bid in button_ids:
            print(f"   - {bid}")
    else:
        print(f"   ⚠️  No buttons found!")
    
    if 'load-sample-btn' in all_ids:
        print(f"\n   ✅ load-sample-btn IS in the layout!")
    else:
        print(f"\n   ❌ load-sample-btn NOT in the layout")
        
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*80)
