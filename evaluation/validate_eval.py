import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_PATH = ROOT / "evaluation" / "questions.json"
MANIFEST_PATH = ROOT / "knowledge_base" / "manifest.json"

with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
    questions = json.load(f)

with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
    manifest = json.load(f)

assert len(questions) >= 40, f"Expected at least 40 questions, got {len(questions)}"

ids = [q["id"] for q in questions]
texts = [q["question"] for q in questions]

assert len(ids) == len(set(ids)), "Duplicate question IDs found"
assert len(texts) == len(set(texts)), "Duplicate question texts found"

manifest_paths = {doc["path"] for doc in manifest["documents"]}

valid_types = {"single_source", "multi_source", "issue_incident", "unanswerable"}

for q in questions:
    assert {"id", "question", "type", "expected_sources",
            "reference_answer", "answerable"} <= q.keys(), (
        f"Missing required field in {q['id']}"
    )

    assert q["type"] in valid_types, f"Invalid type in {q['id']}: {q['type']}"

    sources = q["expected_sources"]

    assert len(sources) == len(set(sources)), (
        f"Repeated source in {q['id']}"
    )

    if q["type"] == "unanswerable":
        assert q["answerable"] is False, (
            f"{q['id']}: unanswerable must have answerable=false"
        )
        assert sources == [], (
            f"{q['id']}: unanswerable question must have no expected sources"
        )
    else:
        assert q["answerable"] is True, (
            f"{q['id']}: answerable type must have answerable=true"
        )

    if q["type"] == "single_source":
        assert len(sources) == 1, (
            f"{q['id']}: single_source must have exactly 1 source"
        )

    if q["type"] == "multi_source":
        assert len(sources) >= 2, (
            f"{q['id']}: multi_source must have at least 2 sources"
        )

    missing = [path for path in sources if path not in manifest_paths]
    assert not missing, (
        f"{q['id']}: source path(s) missing from manifest: {missing}"
    )

print(f"Questions: {len(questions)}")
print(f"Answerable: {sum(q['answerable'] for q in questions)}")
print(f"Unanswerable: {sum(not q['answerable'] for q in questions)}")
print(f"Manifest documents: {len(manifest['documents'])}")
print("VALIDATION PASSED")
