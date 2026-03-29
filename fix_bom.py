import os
import codecs

paths = [
    'CT255H-NexConflict/backend/src/main/java/com/example/backend/entity',
    'CT255H-NexConflict/backend/src/main/java/com/example/backend/repository',
    'CT255H-NexConflict/backend/src/main/java/com/example/backend/service',
    'CT255H-NexConflict/backend/src/main/java/com/example/backend/controller',
    'CT255H-NexConflict/backend/src/main/java/com/example/backend/config',
    'CT255H-NexConflict/backend/src/main/java/com/example/backend/security',
    'CT255H-NexConflict/backend/src/main/java/com/example/backend/dto',
]

print("Checking for BOM...")
count = 0
for p in paths: 
    if os.path.exists(p):
        for root, dirs, files in os.walk(p): 
            for f in files: 
                if f.endswith('.java'): 
                    fp = os.path.join(root, f)
                    try:
                        with open(fp, 'rb') as file: 
                            content = file.read()
                        
                        # Check for UTF-8 BOM
                        if content.startswith(codecs.BOM_UTF8):
                            print(f'Removing BOM from {fp}')
                            with open(fp, 'wb') as file: 
                                file.write(content[3:])
                            count += 1
                        else:
                            # Sometimes editor saves as UTF-16 BOM or others, but typically create_file makes UTF-8 or ASCII.
                            pass
                    except Exception as e:
                        print(f'Error processing {fp}: {e}')

print(f"Fixed {count} files.")
