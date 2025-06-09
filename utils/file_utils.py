def remove_extension(file_name):
    """
    Remove the extension from a file name.

    Args:
        file_name (str): The file name with extension

    Returns:
        str: The file name without extension
    """
    return file_name.split('.')[0]
