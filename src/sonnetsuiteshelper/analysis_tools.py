

def read_data_from_csv(file_exists, file_path=""):
    """

    """

    live_file = os.path.join(file_path, file_name)

    file_exists = os.path.isfile(live_file)

    if not file_exists:
        raise(FileNotFoundError)


