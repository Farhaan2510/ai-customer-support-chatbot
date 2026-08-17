from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def load_documents():
    with open("data/company_policy.txt", "r", encoding="utf-8") as file:
        return file.read()


def split_into_chunks(text):
    return text.split("\n\n")


def create_embeddings(chunks):
    return model.encode(chunks)


def build_index(embeddings):
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings, dtype="float32"))

    return index


def search(query, index, chunks):
    query_embedding = model.encode([query])

    distances, indices = index.search(
        np.array(query_embedding, dtype="float32"),
        k=3
    )

    seen = set()
    results = []

    for i in indices[0]:
        chunk = chunks[i]

        if chunk not in seen:
            seen.add(chunk)
            results.append(chunk)

    return "\n\n".join(results)


if __name__ == "__main__":
    docs = load_documents()
    chunks = split_into_chunks(docs)
    embeddings = create_embeddings(chunks)
    index = build_index(embeddings)

    print(search("Can I return my purchase after a month?", index, chunks))