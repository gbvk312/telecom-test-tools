def calculate_kpis(events):

    total = len(events)
    failures = events.count("FAILURE")

    success_rate = ((total - failures) / total) * 100

    return {
        "total_events": total,
        "failures": failures,
        "success_rate": round(success_rate, 2),
    }
