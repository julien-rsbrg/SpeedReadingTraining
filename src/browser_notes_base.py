import os

def parse_all_files(folder_path:str, kept_extension:str|None = None):
    if (folder_path == "") or (folder_path is None) or not(os.path.exists(folder_path)) :
        return []
    
    else:
        all_file_paths = []
        for fname in os.listdir(folder_path):
            fpath = os.path.join(folder_path,fname)
            
            if os.path.isfile(fpath):
                extension = os.path.splitext(fpath)[1]
                if kept_extension is None or extension == kept_extension:
                    all_file_paths.append(fpath)

            elif os.path.isdir(fpath):
                subfile_paths = parse_all_files(fpath,kept_extension=kept_extension)
                all_file_paths += subfile_paths
        return all_file_paths

if __name__ == "__main__":

    print(parse_all_files(folder_path = "test", kept_extension=None))

    print(parse_all_files(folder_path = "test", kept_extension=".txt"))

    print(parse_all_files(folder_path = "test", kept_extension=".py"))

    print(parse_all_files(folder_path = "test", kept_extension=".md"))

    f = open("test/single_note.md", "r")
    text = f.read()
    print(text, type(text), len(text), len(text.split(" ")))
    f.close()