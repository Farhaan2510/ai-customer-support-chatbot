def load_documents():

    with open("data/company_policy.txt", "r") as file:
        return file.read()
    
if __name__ == "__main__":
    print(load_documents())