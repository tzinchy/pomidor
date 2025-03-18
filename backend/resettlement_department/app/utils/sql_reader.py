def read_sql_query(file_path: str, encoding: str = 'utf-8') -> str:
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return ''
    except UnicodeDecodeError:
        print(f"Error decoding file {file_path} with encoding {encoding}")
        return ''
