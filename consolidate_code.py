import os

def consolidate_apps_code(app_dirs, output_file):
    # List of files to include
    target_files = ['models.py', 'serializers.py', 'views.py', 'urls.py', 'tasks.py']
    
    with open(output_file, 'w') as outfile:
        for app_dir in app_dirs:
            if os.path.exists(app_dir):  # Check if the app directory exists
                app_name = os.path.basename(app_dir)  # Get the app name
                outfile.write(f"# App: {app_name}\n")
                
                # Process each target file in the app directory
                for file in target_files:
                    file_path = os.path.join(app_dir, file)
                    if os.path.exists(file_path):  # Check if the file exists
                        outfile.write(f"# File: {file_path}\n")
                        with open(file_path, 'r') as infile:
                            outfile.write(infile.read())
                        outfile.write("\n\n")
                outfile.write("#" * 50 + "\n\n")  # Separator between apps
            else:
                print(f"Warning: Directory '{app_dir}' does not exist.")

# List of app directories to consolidate
app_directories = [
    # 'admin_portal',
    # 'authusers',
    # 'banners',
    # 'cart_orders',
    # 'commission_and_calculations',
    # 'customer',
    # 'ecommerce_platform',
    'products',
    #'vendors',
    
]

# Output file
output_file = 'consolidated_code.txt'

# Consolidate code from all specified apps
consolidate_apps_code(app_directories, output_file)