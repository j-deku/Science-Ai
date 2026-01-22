# scripts/seed_knowledge.py
from app.core.embedding_loader import add_documents
import uuid

from app.core import ai_knowledge as ak  # reuse your existing dict format

docs = []
for topic, facts in ak.SCIENCE_KNOWLEDGE.items():
    for f in facts:
        docs.append({"id": str(uuid.uuid4()), "topic": topic, "text": f})

print("Adding", len(docs), "documents...")
res = add_documents(docs)
print("Done:", res)
