from recoco.apps.demarches_simplifiees.utils import hash_data


def test_hash_data():
    assert (
        hash_data({"key1": "value1", "key2": "value2"})
        == "6366030fcfbc5e29da7855c8a2c2c0c48670a1cc067d7dbeb1481865105f9515"
    )
