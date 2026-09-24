"""The inference gate must fail closed and explain why."""

from __future__ import annotations

from cybersentinel_ml.contract.schema import FeatureSchema

from .conftest import make_frame, make_manifest, make_verified, provenance_for


def _failed(decision) -> set[str]:  # type: ignore[no-untyped-def]
    return {c["name"] for c in decision.checks if not c["passed"]}


def test_everything_correct_allows_inference(verified_a: FeatureSchema) -> None:
    manifest = make_manifest(verified_a)
    frame = make_frame(manifest.preprocessing.feature_order)
    d = evaluate(verified_a, manifest, provenance_for(verified_a, "pcap"), frame)
    assert d.allowed, d.reasons
    assert d.reasons == []


def test_committed_draft_schema_blocks_inference(schema_a: FeatureSchema) -> None:
    manifest = make_manifest(schema_a)
    frame = make_frame(manifest.preprocessing.feature_order)
    d = evaluate(schema_a, manifest, provenance_for(schema_a, "csv"), frame)
    assert not d.allowed
    assert {"schema_verified", "extractor_pinned"} <= _failed(d)
    assert "withheld" in d.explanation()
    assert "rule-based alerts are still available" in d.explanation()


def test_pcap_without_demonstrated_parity_is_withheld(schema_a: FeatureSchema) -> None:
    schema = make_verified(schema_a, parity="not_demonstrated")
    manifest = make_manifest(schema)
    frame = make_frame(manifest.preprocessing.feature_order)
    d = evaluate(schema, manifest, provenance_for(schema, "pcap"), frame)
    assert not d.allowed
    assert _failed(d) == {"pcap_parity_demonstrated"}
    assert any("parity" in r for r in d.reasons)


def test_csv_does_not_need_pcap_parity_but_warns_when_unverified(schema_a: FeatureSchema) -> None:
    schema = make_verified(schema_a, parity="not_demonstrated")
    manifest = make_manifest(schema)
    frame = make_frame(manifest.preprocessing.feature_order)
    d = evaluate(schema, manifest, provenance_for(schema, "csv", verified=False), frame)
    assert d.allowed
    assert any("asserted" in w for w in d.warnings)


def test_different_extractor_commit_is_withheld(verified_a: FeatureSchema) -> None:
    manifest = make_manifest(verified_a)
    frame = make_frame(manifest.preprocessing.feature_order)
    prov = provenance_for(verified_a, "pcap", commit="ffffffffffffffffffffffffffffffffffffffff")
    d = evaluate(verified_a, manifest, prov, frame)
    assert not d.allowed
    assert "extractor_matches_training" in _failed(d)


def test_different_timeouts_are_withheld(verified_a: FeatureSchema) -> None:
    manifest = make_manifest(verified_a)
    frame = make_frame(manifest.preprocessing.feature_order)
    prov = provenance_for(verified_a, "pcap", flow_timeout_us=60_000_000)
    d = evaluate(verified_a, manifest, prov, frame)
    assert not d.allowed
    assert "flow_timeout_us" in " ".join(d.reasons)


def test_unknown_extractor_is_withheld(verified_a: FeatureSchema) -> None:
    from cybersentinel_ml.contract.manifest import InputProvenance

    manifest = make_manifest(verified_a)
    frame = make_frame(manifest.preprocessing.feature_order)
    prov = InputProvenance(source_type="csv", extractor=None, provenance_verified=False)
    d = evaluate(verified_a, manifest, prov, frame)
    assert not d.allowed
    assert "extractor_known" in _failed(d)


def test_unverified_pcap_provenance_is_withheld(verified_a: FeatureSchema) -> None:
    manifest = make_manifest(verified_a)
    frame = make_frame(manifest.preprocessing.feature_order)
    d = evaluate(verified_a, manifest, provenance_for(verified_a, "pcap", verified=False), frame)
    assert not d.allowed
    assert "pcap_provenance_verified" in _failed(d)


def test_model_trained_on_other_schema_is_withheld(
    verified_a: FeatureSchema, schema_b: FeatureSchema
) -> None:
    other = make_verified(schema_b)
    manifest = make_manifest(other)
    frame = make_frame(manifest.preprocessing.feature_order)
    d = evaluate(verified_a, manifest, provenance_for(verified_a, "pcap"), frame)
    assert not d.allowed
    assert {"manifest_schema_match", "manifest_track"} <= _failed(d)


def test_preprocessing_version_mismatch_is_withheld(verified_a: FeatureSchema) -> None:
    good = make_manifest(verified_a)
    prep = good.preprocessing.model_copy(update={"preprocessing_version": "0.2.0"})
    manifest = good.model_copy(update={"preprocessing": prep})
    frame = make_frame(manifest.preprocessing.feature_order)
    d = evaluate(verified_a, manifest, provenance_for(verified_a, "pcap"), frame)
    assert not d.allowed
    assert "preprocessing_version_match" in _failed(d)


def test_wrong_feature_order_is_withheld(verified_a: FeatureSchema) -> None:
    manifest = make_manifest(verified_a)
    order = manifest.preprocessing.feature_order
    frame = make_frame(list(reversed(order)))
    d = evaluate(verified_a, manifest, provenance_for(verified_a, "pcap"), frame)
    assert not d.allowed
    assert "features_order" in _failed(d)


def test_missing_feature_is_withheld(verified_a: FeatureSchema) -> None:
    manifest = make_manifest(verified_a)
    frame = make_frame(manifest.preprocessing.feature_order).iloc[:, 1:]
    d = evaluate(verified_a, manifest, provenance_for(verified_a, "pcap"), frame)
    assert not d.allowed
    assert "features_no_missing" in _failed(d)


def evaluate(*args):  # type: ignore[no-untyped-def]
    from cybersentinel_ml.contract.gate import evaluate_inference_gate

    return evaluate_inference_gate(*args)


def test_track_b_with_undocumented_extractor_withholds_csv_and_pcap(schema_b: FeatureSchema) -> None:
    # ADR 0010: a verified Track B schema supports offline training and evaluation only.
    data = schema_b.model_dump(mode="json")
    data["status"] = "verified"
    data["extractor"]["commit_status"] = "not_documented"
    for f in data["features"]:
        f["status"] = "verified"
    schema = FeatureSchema.model_validate(data)
    manifest = make_manifest(schema, track="B", task="traffic_type_3class", classes=["TOR", "VPN", "REGULAR"])
    frame = make_frame(manifest.preprocessing.feature_order)
    for source in ("csv", "pcap"):
        d = evaluate(schema, manifest, provenance_for(schema, source), frame)
        assert not d.allowed
        assert "extractor_pinned" in _failed(d)
