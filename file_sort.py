import os

# Directory Definition
pdb_dir = "Protein-Analysis-1\pdb_files"
size_limit = 1500 * 1024  # kb --> byte conversion

# iterate over files in the directory
for filename in os.listdir(pdb_dir):
    file_path = os.path.join(pdb_dir, filename)
    
    # checks if tis valid file + gets size!
    if os.path.isfile(file_path):
        file_size = os.path.getsize(file_path)  # in bytes
        
        if file_size > size_limit:
            os.remove(file_path)
            print(f"🗑️ Deleted: {filename} ({file_size / 1024:.2f} KB)")
        else:
            print(f"✅ Kept: {filename} ({file_size / 1024:.2f} KB)")
