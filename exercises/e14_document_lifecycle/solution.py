## Assume prepare(text) returns searchable text or raises an error.

from uuid import uuid4


class DocumentStore:
    def __init__(self, prepare):
        self.prepare = prepare
        self.documents = {}
        self.index = {}

    def upload(self, customer_id, name, text):
        try:
            searchable = self.prepare(text)
        except Exception as error:
            return {"status": "failed", "error": str(error)}

        document_id = uuid4().hex
        self.documents[document_id] = {
            "customer_id": customer_id,
            "name": name,
            "text": text,
        }
        self.index[document_id] = searchable

        return {"status": "success", "document_id": document_id}

    def replace(self, customer_id, document_id, text):
        document = self.documents.get(document_id)

        if document is None or document["customer_id"] != customer_id:
            return {"status": "failed", "error": "Document not found"}

        try:
            searchable = self.prepare(text)
        except Exception as error:
            return {"status": "failed", "error": str(error)}

        document["text"] = text
        self.index[document_id] = searchable

        return {"status": "success", "document_id": document_id}

    def delete(self, customer_id, document_id):
        document = self.documents.get(document_id)

        if document is not None and document["customer_id"] != customer_id:
            return {"status": "failed", "error": "Document not found"}

        self.documents.pop(document_id, None)
        self.index.pop(document_id, None)

        return {"status": "success", "document_id": document_id}

    def search(self, customer_id, query):
        query = query.lower()

        return [
            {"document_id": document_id, "name": document["name"]}
            for document_id, document in self.documents.items()
            if document["customer_id"] == customer_id
            and query in self.index[document_id].lower()
        ]
