import csv
import io
import json
from typing import Dict, Any, List

class ReportService:
    @staticmethod
    def generate_json_report(session_data: Dict[str, Any]) -> str:
        return json.dumps(session_data, indent=2, default=str)

    @staticmethod
    def generate_csv_attendance(attendance_records: List[Dict[str, Any]]) -> str:
        output = io.StringIO()
        fieldnames = [
            "anonymous_track_id",
            "participant_name",
            "roll_number",
            "status",
            "observed_pct",
            "total_observed_sec",
            "evidence_quality",
            "is_manual_override",
            "override_notes"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for rec in attendance_records:
            writer.writerow({
                "anonymous_track_id": rec.get("anonymous_track_id"),
                "participant_name": rec.get("participant_name", "Unassigned"),
                "roll_number": rec.get("roll_number", "N/A"),
                "status": rec.get("status"),
                "observed_pct": f"{rec.get('observed_pct', 0.0)}%",
                "total_observed_sec": rec.get("total_observed_sec", 0.0),
                "evidence_quality": rec.get("evidence_quality"),
                "is_manual_override": rec.get("is_manual_override", False),
                "override_notes": rec.get("override_notes", "")
            })

        return output.getvalue()
