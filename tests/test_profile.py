from nutrition.profile import load_profile, Profile

def test_load_profile_reads_targets_and_flags():
    p = load_profile("data/profile.json")
    assert isinstance(p, Profile)
    assert p.diet_type == "lacto-vegetarian"
    assert p.eggs is False
    assert p.targets["fiber_g"] == 35
    assert p.flags["ldl_high"] is True
    assert "Vitamin B12 (methylcobalamin)" in [s["name"] for s in p.supplements]

def test_load_profile_rejects_missing_targets(tmp_path):
    import json, pytest
    bad = tmp_path / "p.json"
    bad.write_text(json.dumps({"diet": {"type": "x"}}))
    with pytest.raises(ValueError):
        load_profile(str(bad))
