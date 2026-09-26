from langchain_text_splitters import RecursiveCharacterTextSplitter


from pathlib import PureWindowsPath


def generate_chunk_id(chunk):
    """Generatin IDs for each chunk using first letter of each directory part, page number, starting index."""

    path = PureWindowsPath(chunk.metadata["source"])

    initials = path.drive[0]  # E

    for part in path.parts[1:]:
        if part:
            initials += part[0]

    return f"{initials}-{chunk.metadata['page']}-{chunk.metadata['start_index']}"



def split_documents(docs):
    msg = "Splitting text & generating IDs..."
    print(msg)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )

    chunks = text_splitter.split_documents(docs)
    
    for chunk in chunks:
        chunk.metadata["id"] = generate_chunk_id(chunk)

    return chunks
