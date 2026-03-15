

def parse_log(file_path):
    events = []

    with open(file_path, "r") as f:
        for line in f:
            if "RRC Setup" in line:
                events.append("RRC_SETUP")

            elif "Registration Accept" in line:
                events.append("REGISTRATION_SUCCESS")

            elif "PDU Session" in line:
                events.append("PDU_SESSION")

            elif "FAIL" in line or "ERROR" in line:
                events.append("FAILURE")

    return events
