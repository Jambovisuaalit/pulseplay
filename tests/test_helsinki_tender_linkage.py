import unittest
from workers.evaluate_helsinki_tender_linkage import assess, evaluate

def row(case_id):
    return {"case_id":case_id, "required_building_lot_documents":[
        {"name":"tender","status":"PUBLIC_FULL_TEXT_VERIFIED"},
        {"name":"annex","status":"NOT_FOUND"}],
        "notice_id":None,"notice_link_status":"NOT_VERIFIED",
        "verified_individual_lot_value_eur":None,"value_source_status":"NOT_VERIFIED"}

class HelsinkiTenderLinkageTests(unittest.TestCase):
    def test_missing_zip_or_ru_tender_blocks(self):
        result=assess(row("HELSINKI_POHJOLA_4F_2020"))
        self.assertFalse(result["complete_package"])
        self.assertEqual(result["gold_label"],"UNREVIEWED")
        self.assertIsNone(result["precision_at_30"])

    def test_unlinked_notice_and_missing_value_block_even_with_documents(self):
        x=row("HELSINKI_USPENSKI_INTERIOR")
        x["required_building_lot_documents"][1]["status"]="PUBLIC_FULL_TEXT_VERIFIED"
        result=assess(x)
        self.assertFalse(result["complete_package"])
        self.assertFalse(result["verified_original_notice_link"])

    def test_verified_notice_and_value_still_require_independent_gold(self):
        x=row("HELSINKI_POHJOLA_4F_2020")
        x["required_building_lot_documents"][1]["status"]="PUBLIC_FULL_TEXT_VERIFIED"
        x.update(notice_id="123",notice_link_status="VERIFIED_ORIGINAL_NOTICE_ID",
                 verified_individual_lot_value_eur=50000,value_source_status="VERIFIED_PRIMARY_SOURCE")
        result=assess(x)
        self.assertTrue(result["complete_package"])
        self.assertEqual(result["gold_label"],"UNREVIEWED")
        self.assertEqual(result["eligibility_decision"],"REQUIRES_INDEPENDENT_REVIEW")

    def test_both_cases_required(self):
        with self.assertRaises(ValueError):
            evaluate({"candidates":[row("HELSINKI_POHJOLA_4F_2020")]})

if __name__=="__main__":
    unittest.main()
