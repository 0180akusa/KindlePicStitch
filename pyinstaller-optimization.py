import os
import sys
from PyInstaller.__main__ import run

def read_file_content(file_path):
    encodings = ['utf-8', 'gbk', 'iso-8859-1']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    print(f"Error: Unable to read the file {file_path} with any of the attempted encodings.")
    return None

if __name__ == "__main__":
    script_name = input("Enter the name of your main script (e.g., your_script.py): ").strip()
    
    if not os.path.exists(script_name):
        print(f"Error: The file {script_name} does not exist.")
        sys.exit(1)

    # 基本配置
    args = [
        script_name,
        '--onefile',
        '--windowed',
        '--name=EPUBtoPicOne',
        
        # 排除不必要的模块
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        
        # 仅包含必要的 tkinter 模块
        '--collect-submodules=tkinter',
        '--collect-data=tkinter',
        
        # 针对特定库的优化
        '--collect-submodules=PIL',
        
        # 清理
        '--clean',
    ]
    
    # 读取文件内容
    content = read_file_content(script_name)
    if content is None:
        sys.exit(1)

    # 检查是否使用了 tkinterdnd2
    if 'tkinterdnd2' in content:
        tkinterdnd2_path = os.path.join(sys.prefix, 'Lib', 'site-packages', 'tkinterdnd2')
        if os.path.exists(tkinterdnd2_path):
            args.extend(['--add-data', f'{tkinterdnd2_path}:tkinterdnd2'])
        else:
            print("Warning: tkinterdnd2 is used in the script but not found in the expected location.")

    # 运行 PyInstaller
    print("Starting PyInstaller with the following arguments:")
    print(" ".join(args))
    run(args)

print("PyInstaller process completed. Check the 'dist' folder for your executable.")