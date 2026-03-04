# check_views.py
import os
import re

views_file = r"C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py"

print(f"Checking: {views_file}")
print("=" * 60)

# Check if file exists
if not os.path.exists(views_file):
    print("❌ views.py file NOT found!")
    exit()

# Read the file
with open(views_file, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"✅ File exists. Size: {len(content)} characters")

# Check for PlanSelectionView
if 'class PlanSelectionView' in content:
    print("✅ 'PlanSelectionView' class found in file")
    
    # Find the line number
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'class PlanSelectionView' in line:
            print(f"   Found at line: {i+1}")
            # Show context
            for j in range(max(0, i-2), min(len(lines), i+3)):
                print(f"   {j+1:3}: {lines[j]}")
            break
else:
    print("❌ 'PlanSelectionView' class NOT found in file")

print("\n" + "=" * 60)

# Check for other important views
check_views = [
    'SelectPlanView',
    'ItineraryDetailView',
    'AddActivityView',
    'RemoveActivityView',
    'DownloadItineraryPDFView'
]

print("\nChecking for other required views:")
for view in check_views:
    if f'class {view}' in content:
        print(f"✅ {view}")
    else:
        print(f"❌ {view}")

print("\n" + "=" * 60)

# Count total classes in file
classes = re.findall(r'class (\w+)[(:]', content)
print(f"\nTotal classes found in views.py: {len(classes)}")
for i, cls in enumerate(classes[:20]):  # Show first 20
    print(f"  {i+1}. {cls}")

if len(classes) > 20:
    print(f"  ... and {len(classes)-20} more")

# Check if PlanSelectionView is in the list
if 'PlanSelectionView' in classes:
    print("\n✅ Excellent! PlanSelectionView is defined in views.py")
else:
    print("\n❌ Problem: PlanSelectionView is NOT defined in views.py")
    print("\nPlease add it to the end of your views.py file.")