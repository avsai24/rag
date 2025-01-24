def file(file_name, data):
     with open(file_name, 'w', encoding='utf-8') as file:
            file.write(data)