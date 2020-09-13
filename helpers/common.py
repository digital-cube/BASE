def missing_keys(source, expected_keys: list):
    if not source:
        return expected_keys

    missing = []
    for key in expected_keys:
        if key not in source:
            missing.append(key)

    return missing
