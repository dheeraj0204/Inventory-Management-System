"""Tests for TQM Module: CTQ metrics, Pareto analysis, FMEA RPN, Fishbone, SIPOC, and PDCA."""

import pytest
from app.utils.validators import ValidationError


class TestTQMService:
    """Verifies statistical quality control calculations and TQM continuous improvement models."""

    def test_fmea_rpn_calculation(self, test_tqm_service):
        item = test_tqm_service.add_fmea_item(
            process_step="Inspection",
            failure_mode="Scale Drift",
            failure_effect="Inaccurate weight entry",
            potential_cause="Lack of weekly recalibration",
            existing_controls="Daily tare check",
            severity=8,
            occurrence=4,
            detection=5,
            recommended_action="Implement mandatory digital calibration schedule",
            owner="Dheeraj Khetwal",
        )
        # Expected RPN = 8 * 4 * 5 = 160
        assert item.rpn == 160
        assert item.risk_level == "Medium Risk"

    def test_fmea_score_range_validation(self, test_tqm_service):
        with pytest.raises(ValidationError) as exc:
            test_tqm_service.add_fmea_item(
                process_step="Receipt",
                failure_mode="Test",
                failure_effect="Test",
                potential_cause="Test",
                existing_controls="Test",
                severity=15,  # Out of range (> 10)
                occurrence=5,
                detection=5,
                recommended_action="Test",
                owner="Test",
            )
        assert "between 1 and 10" in exc.value.message.lower()

    def test_pareto_analysis_sorting_and_cumulative_percentages(self, test_tqm_service):
        pareto = test_tqm_service.calculate_pareto_data()
        assert len(pareto["categories"]) >= 4
        counts = pareto["counts"]

        # 1. Verify frequencies are sorted in descending order
        assert counts == sorted(counts, reverse=True)

        # 2. Verify cumulative counts sum to total defects
        assert pareto["cumulative_counts"][-1] == pareto["total_defects"]

        # 3. Verify cumulative percentages end at 100.0%
        assert pareto["cumulative_percentages"][-1] == 100.0

        # 4. Verify vital few categories identified
        assert len(pareto["vital_few"]) >= 1

    def test_ctq_scorecard_calculation(self, test_tqm_service):
        ctq_data = test_tqm_service.calculate_ctq_metrics()
        assert "metrics" in ctq_data
        metrics = ctq_data["metrics"]

        assert len(metrics) == 5
        # Verify all baseline seeded products pass CTQ-1, CTQ-2, CTQ-3, CTQ-4
        for m in metrics[:4]:
            assert m["status"] == "PASS"

    def test_defect_logging_and_resolution(self, test_tqm_service):
        defect = test_tqm_service.add_defect(
            category="Invalid Input",
            description="Operator attempted to enter negative stock",
            severity="High",
            occurrence_count=3,
        )
        assert defect.status == "Open"
        assert defect.defect_code.startswith("DEF-")

        # Resolve defect
        resolved = test_tqm_service.resolve_defect(
            defect_code=defect.defect_code,
            corrective_action="Added input validation mask and error modal",
        )
        assert resolved is True

        all_defects = test_tqm_service.get_all_defects()
        matched = [d for d in all_defects if d.defect_code == defect.defect_code][0]
        assert matched.status == "Resolved"
        assert matched.corrective_action == "Added input validation mask and error modal"

    def test_fishbone_and_sipoc_data_integrity(self, test_tqm_service):
        fishbone = test_tqm_service.get_fishbone_data()
        assert "categories" in fishbone
        assert set(fishbone["categories"].keys()) == {"People", "Process", "Software Code", "Infrastructure"}

        sipoc = test_tqm_service.get_sipoc_data()
        assert "stages" in sipoc
        assert len(sipoc["stages"]) == 5

    def test_pdca_lifecycle(self, test_tqm_service):
        record = test_tqm_service.add_pdca_record(
            title="Q07 Data Cleansing Project",
            stage="PLAN",
            problem_statement="High frequency of manual SKU duplicate clashes",
            plan_description="Implement SQLite UNIQUE constraint and pre-save query",
            owner="Dheeraj Khetwal",
        )
        assert record.stage == "PLAN"
        assert record.status == "Planned"

        # Advance stage
        updated = test_tqm_service.update_pdca_stage(
            record_id=record.id,
            stage="DO",
            status="In Progress",
            do_action="Implemented pre-save check_sku_exists query in ProductService",
        )
        assert updated is True
