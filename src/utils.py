
import os

def make_directory_recursively(folder_path: str):
    """Create a directory recursively to create all the parents of
    the directory if they are missing

    Parameters
    ----------
    folder_path : str
        -- path of the folder to create if necessary along with its parents
    """
    if folder_path in ["", ".."] or folder_path is None:
        return
    
    elif not (os.path.exists(folder_path)):
        parent_folder_path = os.path.dirname(folder_path)
        if os.path.exists(parent_folder_path):
            os.mkdir(folder_path)
        else:
            make_directory_recursively(parent_folder_path)
            os.mkdir(folder_path)




def save_file_json(file, folder_path, file_name):
    if file_name[-4:] != ".pkl":
        file_name = file_name+".pkl"
    if not (os.path.exists(folder_path)):
        os.mkdir(folder_path)

    file_path = os.path.join(folder_path, file_name)

    with open(file_path, 'wb') as fp:
        pickle.dump(file, fp)


def read_file_json(file_path):
    with open(file_path, 'rb') as fp:
        file = pickle.load(fp)
    return file


if __name__ == "__main__":
    pass