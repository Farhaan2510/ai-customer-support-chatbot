def load_documents():

    with open("data/company_policy.txt", "r") as file:
        return file.read()
    
def split_into_chunks(text):
    chunks = text.split("\n\n")
    return chunks

if __name__ == "__main__":
    print(load_documents())

if __name__ == "__main__":

    docs = load_documents()

    chunks = split_into_chunks(docs)

    for chunk in chunks:
        print(chunk)
        print("-----")