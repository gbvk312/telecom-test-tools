def detect_failures(events):

    failures = []

    for event in events:
        if event == "FAILURE":
            failures.append("Generic Failure Detected")

    return failures
