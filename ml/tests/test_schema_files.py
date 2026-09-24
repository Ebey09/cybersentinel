"""Lint the committed schema files. These tests encode the leakage and vocabulary rules."""

from __future__ import annotations

import pytest

from cybersentinel_ml.contract.schema import FeatureSchema, SchemaStatus

LEAKY_NAMES = {"flow_id", "src_ip", "dst_ip", "src_port", "timestamp", "label"}


@pytest.mark.parametrize("fixture", ["schema_a", "schema_b"])
def test_schema_loads_and_is_consistent(fixture: str, request: pytest.FixtureRequest) -> None:
    schema: FeatureSchema = request.getfixturevalue(fixture)
    assert schema.features
    assert len(schema.sha256()) == 64


@pytest.mark.parametrize("fixture", ["schema_a", "schema_b"])
def test_identifiers_and_labels_are_never_model_inputs(fixture: str, request: pytest.FixtureRequest) -> None:
    schema: FeatureSchema = request.getfixturevalue(fixture)
    inputs = set(schema.input_feature_names())
    assert not inputs & LEAKY_NAMES
    label_sources = {lab.source_column for lab in schema.label_columns}
    assert not {f.source_column for f in schema.features} & label_sources


@pytest.mark.parametrize("fixture", ["schema_a", "schema_b"])
def test_every_feature_is_documented(fixture: str, request: pytest.FixtureRequest) -> None:
    schema: FeatureSchema = request.getfixturevalue(fixture)
    for f in schema.features + schema.excluded_features:
        assert f.meaning and f.missing_values and f.source and f.pcap_available
    for f in schema.excluded_features:
        assert f.notes, f"excluded feature {f.name} must say why"


def test_phase1_schemas_are_drafts(schema_a: FeatureSchema, schema_b: FeatureSchema) -> None:
    # Neither schema has been compared with the real CSV yet. Flip to verified only
    # after `cybersentinel-ml check-header` passes on the downloaded data.
    assert schema_a.status == SchemaStatus.DRAFT
    assert schema_b.status == SchemaStatus.DRAFT


def test_tracks_have_separate_schemas(schema_a: FeatureSchema, schema_b: FeatureSchema) -> None:
    assert schema_a.schema_id != schema_b.schema_id
    assert schema_a.extractor.repository != schema_b.extractor.repository
    # The Engelen fork emits columns the upstream tool does not.
    fork_only = set(schema_a.raw_columns) - set(schema_b.raw_columns)
    assert {"Fwd RST Flags", "Bwd RST Flags", "ICMP Code"} <= fork_only


def test_track_b_excludes_features_affected_by_upstream_bugs(schema_b: FeatureSchema) -> None:
    excluded = {f.name for f in schema_b.excluded_features}
    for name in ["active_mean", "idle_max", "fwd_psh_flags", "bwd_urg_flags"]:
        assert name in excluded


def test_track_b_has_no_pcap_parity(schema_b: FeatureSchema) -> None:
    assert schema_b.parity.status.value == "not_demonstrated"
    assert not schema_b.extractor.is_pinned
    assert all(f.pcap_available == "unverified" for f in schema_b.features)


def test_track_b_vocabulary_forbids_harm_terms(schema_b: FeatureSchema) -> None:
    forbidden = {t.lower() for t in schema_b.output_vocabulary.forbidden_terms}
    assert {"malicious", "attack", "malware", "threat"} <= forbidden
    joined = " ".join(schema_b.output_vocabulary.allowed_terms).lower()
    assert not any(t in joined for t in forbidden)


def test_schema_hash_changes_with_content(schema_a: FeatureSchema) -> None:
    data = schema_a.model_dump(mode="json")
    data["preprocessing"]["version"] = "9.9.9"
    changed = FeatureSchema.model_validate(data)
    assert changed.sha256() != schema_a.sha256()


def test_inconsistent_schema_is_rejected(schema_a: FeatureSchema) -> None:
    data = schema_a.model_dump(mode="json")
    data["raw_columns"].append("Mystery Column")  # a raw column with no role
    with pytest.raises(ValueError, match="no role"):
        FeatureSchema.model_validate(data)


def test_unknown_yaml_key_is_rejected(schema_a: FeatureSchema) -> None:
    data = schema_a.model_dump(mode="json")
    data["featurez"] = []
    with pytest.raises(ValueError):
        FeatureSchema.model_validate(data)


def test_verified_schema_requires_pinned_commit(schema_a: FeatureSchema) -> None:
    data = schema_a.model_dump(mode="json")
    data["status"] = "verified"
    for f in data["features"]:
        f["status"] = "verified"
    with pytest.raises(ValueError, match="pinned extractor commit"):
        FeatureSchema.model_validate(data)


def _verified_data(schema: FeatureSchema, commit_status: str) -> dict:  # type: ignore[type-arg]
    data = schema.model_dump(mode="json")
    data["status"] = "verified"
    data["extractor"]["commit_status"] = commit_status
    for f in data["features"]:
        f["status"] = "verified"
    return data


def test_pinned_status_needs_a_real_commit(schema_a: FeatureSchema) -> None:
    data = schema_a.model_dump(mode="json")
    data["extractor"]["commit_status"] = "pinned"  # commit is still the [VERIFY] placeholder
    with pytest.raises(ValueError, match="needs a real commit"):
        FeatureSchema.model_validate(data)


def test_verified_schema_accepts_an_extractor_confirmed_as_not_documented(schema_b: FeatureSchema) -> None:
    # ADR 0010: the data itself can be verified even when the authors never documented the extractor.
    schema = FeatureSchema.model_validate(_verified_data(schema_b, "not_documented"))
    assert schema.status == SchemaStatus.VERIFIED
    assert not schema.extractor.is_pinned


def test_not_documented_extractor_rules_out_parity(schema_b: FeatureSchema) -> None:
    data = _verified_data(schema_b, "not_documented")
    data["parity"]["status"] = "demonstrated"
    with pytest.raises(ValueError, match="parity cannot be demonstrated"):
        FeatureSchema.model_validate(data)


def test_track_a_extractor_is_never_marked_not_documented(schema_a: FeatureSchema) -> None:
    # Track A's extractor is knowable: pin the release's commit, or regenerate with a pinned
    # build (V8, ADR 0006). 'not_documented' is only for a dataset whose authors never said.
    assert schema_a.extractor.commit_status != "not_documented"


def test_positional_rename_must_point_at_its_resolved_name(schema_b: FeatureSchema) -> None:
    data = schema_b.model_dump(mode="json")
    data["positional_renames"][0]["position"] = 0  # raw_columns[0] is 'Flow ID', not the resolved name
    with pytest.raises(ValueError, match="must be the resolved name"):
        FeatureSchema.model_validate(data)


def test_track_a_matches_the_published_cns2022_layout(schema_a: FeatureSchema) -> None:
    # ADR 0012: the schema describes CICIDS2017_improved.zip as published (91 columns).
    assert len(schema_a.raw_columns) == 91
    assert schema_a.raw_columns[0] == "id"
    assert schema_a.raw_columns[-3:] == ["Total TCP Flow Time", "Label", "Attempted Category"]
    later_fork_columns = {
        "Bwd Act Data Pkts",
        "Bwd Seg Size Min",
        "Fwd TCP Retrans. Count",
        "Bwd TCP Retrans. Count",
        "Total TCP Retrans. Count",
        "Total Connection Flow Time",
    }
    assert not later_fork_columns & set(schema_a.raw_columns)
    # Columns added by the labelling notebook, and the undefined duration field, are never model inputs.
    inputs = {f.source_column for f in schema_a.features}
    assert not {"id", "Attempted Category", "Total TCP Flow Time", "Label"} & inputs
    # The generation commit is not documented, so it must not look pinned.
    assert schema_a.extractor.commit_status == "to_verify"
    assert not schema_a.extractor.is_pinned
