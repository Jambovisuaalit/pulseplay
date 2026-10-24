import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'workers'))
from relevance_v2 import area_signal, size_signal, scope_signal, classify_notice
from fetch_hilma import construction_query_groups
from hilma_cpv import TIER1, search_expression

class SourceBoundaries(unittest.TestCase):
 def notice(self, **changes):
  notice={'id':'synthetic-only','title':'Huoneistosaneeraus','description':'Työmaa sijaitsee Espoossa. Urakan ennakoitu arvo on 80 000 euroa.','estimated_value':80000,'verified_single_contract_value':True,'contract_value_evidence':'Urakan ennakoitu arvo on 80 000 euroa.'}
  notice.update(changes)
  return notice
 def test_buyer_address_is_not_structured_worksite_evidence(self):
  n=self.notice(description='Tilaajan toimisto sijaitsee Helsingissä.',worksite_municipality='helsinki',worksite_location_evidence='Tilaajan toimisto sijaitsee Helsingissä.')
  self.assertEqual(area_signal(n).status,'UNKNOWN')
  self.assertNotEqual(classify_notice(n)['model_label'],'Relevantti')
 def test_conflicting_worksites_do_not_silently_select_the_allowed_city(self):
  n=self.notice(description='Työmaa sijaitsee Espoossa. Toinen työmaa sijaitsee Turussa.',worksite_municipality='espoo',worksite_location_evidence='Työmaa sijaitsee Espoossa.')
  self.assertEqual(area_signal(n).status,'UNKNOWN')
 def test_boolean_and_fabricated_or_mismatching_value_quote_never_verify_size(self):
  for changes in [{'estimated_value':True},{'contract_value_evidence':'Invented confirmation'},{'contract_value_evidence':'Urakan ennakoitu arvo on 90 000 euroa.'}]:
   self.assertEqual(size_signal(self.notice(**changes)).status,'UNKNOWN')
 def test_source_bound_unit_value_and_exact_bounds_are_recognised(self):
  for value in [10000,80000,250000]:
   quote=f'Urakan arvo on {value} euroa.'
   self.assertEqual(size_signal(self.notice(estimated_value=value,description='Työmaa sijaitsee Espoossa. '+quote,contract_value_evidence=quote)).status,'IN')
 def test_negated_work_and_consulting_are_not_renovation_positives(self):
  for phrase in ['Urakkaan ei kuulu pintaremontti.','Pintaremontti ei kuulu sopimukseen.']:
   self.assertEqual(scope_signal(self.notice(title='Huoltopalvelu',description=phrase)).status,'UNKNOWN')
  self.assertEqual(scope_signal(self.notice(title='Pintaremontin suunnittelu')).status,'OUT')
 def test_non_negated_later_clause_still_counts(self):
  n=self.notice(title='Sisätilojen työt',description='Urakkaan ei kuulu maalaustyöt. Urakkaan kuuluu lattiatyöt.')
  self.assertEqual(scope_signal(n).status,'MATCH')
 def test_actual_acquisition_query_excludes_maintenance_and_consulting_roots(self):
  tree=[{'id':code,'label':'Synthetic vocabulary','children':[]} for code in TIER1]
  self.assertEqual(search_expression(construction_query_groups(tree)),'45000000')

if __name__=='__main__': unittest.main()
