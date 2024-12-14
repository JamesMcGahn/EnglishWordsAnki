import os


class PathManager:
    """
    A utility class to manage file and directory paths. It includes methods for checking
    if paths exist, creating directories, handling duplicates, and parsing file paths.
    """

    @staticmethod
    def path_exists(path: str, makepath: bool, raiseError: bool = False) -> bool:
        """
        Check if a path exists, optionally create the path if it doesn't exist, and raise an error if needed.

        Args:
            path (str): The path to check.
            makepath (bool): If True, create the path if it doesn't exist.
            raiseError (bool, optional): If True, raise a ValueError if the path doesn't exist and makepath is False.

        Returns:
            bool: True if the path exists or was successfully created, False otherwise.

        Raises:
            ValueError: If the path doesn't exist and raiseError is True.
        """
        if os.path.exists(path):
            return True
        elif not os.path.exists(path) and makepath:
            os.makedirs(path)
            return True
        else:
            if raiseError:
                raise ValueError("Filepath does not exist")
            else:
                return False

    @staticmethod
    def regex_path(path: str) -> dict:
        """
        Splits a file path into its directory, filename, and extension components.

        Args:
            path (str): The full file path.

        Returns:
            dict: A dictionary containing the directory, filename, and extension.
        """
        directory = os.path.dirname(path)
        filename = os.path.basename(path)
        name, ext = os.path.splitext(filename)

        return {"path": directory, "filename": name, "ext": ext}

    @staticmethod
    def check_dup(folderpath: str, filename: str, ext: str) -> str:
        """
        Checks for duplicate filenames in a folder and appends a number to the filename if necessary.

        Args:
            folderpath (str): The path to the folder where the file is saved.
            filename (str): The base filename (without extension).
            ext (str): The file extension.

        Returns:
            str: The final unique file path.
        """
        # if folder path doesnt exist - create it
        PathManager.path_exists(folderpath, True)
        # remove linux illegal characters
        if isinstance(filename, int):
            filename = str(filename)
        filename = filename.replace("/", "-").replace("\0", "")
        path = f"{folderpath}{filename}{ext}"
        # check if filename exists
        if PathManager.path_exists(path, False):
            count = 1
            newpath = f"{folderpath}{filename}-({count}){ext}"
            # if filename exists append -(count) to make unique filename
            # check to see if filename already exists - if it does increase count in filename
            while PathManager.path_exists(newpath, False):
                newpath = f"{folderpath}{filename}-({count}){ext}"
                count += 1
            path = newpath
        return path
