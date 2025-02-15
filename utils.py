
def save_response_to_file(markdown_content, file_name):
    # Scrie conținutul Markdown într-un fișier
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(markdown_content)