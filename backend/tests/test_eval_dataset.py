import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = REPO_ROOT / "sample-data" / "eval" / "retrieval-eval.json"
BUILT_IN_RAG_EVAL_DATASET_PATH = REPO_ROOT / "sample-data" / "eval" / "built-in-rag-eval-zh-invoices.json"
SAMPLE_DOCUMENTS_DIR = REPO_ROOT / "sample-data" / "documents"
REQUIRED_FIELDS = {
    "id",
    "query",
    "top_k",
    "expected_document_filenames",
    "expected_chunk_hints",
    "expected_terms",
    "tags",
}


def load_dataset() -> list[dict[str, object]]:
    with DATASET_PATH.open(encoding="utf-8") as dataset_file:
        dataset = json.load(dataset_file)

    assert isinstance(dataset, list)
    return dataset


def load_built_in_rag_eval_dataset() -> list[dict[str, object]]:
    with BUILT_IN_RAG_EVAL_DATASET_PATH.open(encoding="utf-8") as dataset_file:
        dataset = json.load(dataset_file)

    assert isinstance(dataset, list)
    return dataset


def test_retrieval_eval_dataset_follows_contract() -> None:
    dataset = load_dataset()

    assert len(dataset) >= 20
    assert len({case["id"] for case in dataset}) == len(dataset)

    covered_tags: set[str] = set()

    for case in dataset:
        assert REQUIRED_FIELDS.issubset(case)
        assert isinstance(case["id"], str)
        assert case["id"]
        assert isinstance(case["query"], str)
        assert case["query"]
        assert isinstance(case["top_k"], int)
        assert 1 <= case["top_k"] <= 10

        expected_filenames = case["expected_document_filenames"]
        assert isinstance(expected_filenames, list)
        assert expected_filenames
        for filename in expected_filenames:
            assert isinstance(filename, str)
            assert (SAMPLE_DOCUMENTS_DIR / filename).is_file()

        expected_chunk_hints = case["expected_chunk_hints"]
        assert isinstance(expected_chunk_hints, list)
        assert expected_chunk_hints
        assert all(isinstance(hint, str) and hint for hint in expected_chunk_hints)

        expected_terms = case["expected_terms"]
        assert isinstance(expected_terms, list)
        assert expected_terms
        assert all(isinstance(term, str) and term for term in expected_terms)

        tags = case["tags"]
        assert isinstance(tags, list)
        assert tags
        assert all(isinstance(tag, str) and tag for tag in tags)
        covered_tags.update(tags)

    assert "invoice" in covered_tags
    assert "contract" in covered_tags
    assert "support" in covered_tags
    phase_16_tags = {
        "lexical_mismatch",
        "multi_evidence",
        "near_duplicate",
        "cross_document_ambiguity",
        "numeric_table_lookup",
    }
    assert phase_16_tags.issubset(covered_tags)
    phase_20_tags = {
        "demo_safe_trace",
        "incident",
        "numeric_lookup",
        "data_processing",
    }
    assert phase_20_tags.issubset(covered_tags)


def test_sample_documents_include_interview_mvp_text_fixtures() -> None:
    sample_text_files = sorted(SAMPLE_DOCUMENTS_DIR.glob("*.txt"))

    assert len(sample_text_files) >= 5


def test_retrieval_eval_expected_terms_are_backed_by_sample_documents() -> None:
    dataset = load_dataset()

    for case in dataset:
        source_text = "\n".join(
            (SAMPLE_DOCUMENTS_DIR / filename).read_text(encoding="utf-8")
            for filename in case["expected_document_filenames"]
        ).casefold()

        for term in case["expected_terms"]:
            assert term.casefold() in source_text


def test_built_in_rag_eval_dataset_has_expected_invoice_distribution() -> None:
    dataset = load_built_in_rag_eval_dataset()

    assert len(dataset) == 10
    assert len({case["id"] for case in dataset}) == len(dataset)

    filenames = [
        filename
        for case in dataset
        for filename in case["expected_document_filenames"]
    ]
    assert len(filenames) == 10
    assert len(set(filenames)) == 10

    vendor_counts: dict[str, int] = {}
    dates: set[str] = set()
    amounts: set[str] = set()

    for case in dataset:
        assert REQUIRED_FIELDS.issubset(case)
        assert case["top_k"] == 5
        vendor_tags = [
            str(tag).removeprefix("vendor:")
            for tag in case["tags"]
            if str(tag).startswith("vendor:")
        ]
        assert len(vendor_tags) == 1
        vendor_counts[vendor_tags[0]] = vendor_counts.get(vendor_tags[0], 0) + 1

        filename = case["expected_document_filenames"][0]
        document_text = (SAMPLE_DOCUMENTS_DIR / filename).read_text(encoding="utf-8")
        assert "Synthetic demo invoice" in document_text
        assert "幣別: TWD" in document_text
        assert "台幣" in document_text
        assert "真實" not in document_text

        date_terms = [term for term in case["expected_terms"] if str(term).startswith("2026-05-")]
        amount_terms = [term for term in case["expected_terms"] if str(term).startswith("NT$")]
        assert date_terms
        assert amount_terms
        dates.add(date_terms[0])
        amounts.add(amount_terms[0])

    assert vendor_counts == {
        "DocuRAG": 4,
        "GOOGLE": 1,
        "Intel": 3,
        "NVDLA": 1,
        "OpenAI": 1,
    }
    assert len(dates) == 10
    assert len(amounts) == 10


def test_built_in_rag_eval_expected_terms_are_backed_by_invoice_fixtures() -> None:
    dataset = load_built_in_rag_eval_dataset()

    for case in dataset:
        source_text = "\n".join(
            (SAMPLE_DOCUMENTS_DIR / filename).read_text(encoding="utf-8")
            for filename in case["expected_document_filenames"]
        ).casefold()

        for hint in case["expected_chunk_hints"]:
            assert hint.casefold() in source_text
        for term in case["expected_terms"]:
            assert term.casefold() in source_text
