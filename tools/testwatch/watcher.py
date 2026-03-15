import json

try:
    from .parser import parse_line
except ImportError:
    from parser import parse_line


def watch_log(file_path, patterns, json_output=False):
    passed = 0
    failed = 0
    results = []

    with open(file_path, "r") as file:
        for line in file:
            result = parse_line(line, patterns)
            stripped_line = line.strip()

            if result == "FAIL":
                failed += 1
                if not json_output:
                    print(f"❌ {stripped_line}")
            else:
                passed += 1
                if not json_output:
                    print(f"✔ {stripped_line}")

            if json_output:
                results.append({"line": stripped_line, "status": result})

    if json_output:
        output = {"results": results, "summary": {"passed": passed, "failed": failed}}
        print(json.dumps(output, indent=4))
    else:
        print("\nSummary")
        print("Passed:", passed)
        print("Failed:", failed)
