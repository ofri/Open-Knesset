import json
from django.test import TestCase
from knesset.annotations.models import DictField
from knesset.annotations.models import CommaDelimitedStringListField

class AnnotationModelTest(TestCase):
    def test_dict_field_to_python(self):
        field = DictField()
        result = field.to_python('{ "key": "value", "listkey": ["item1", "item2"] }')
        self.assertEqual("value", result["key"])

    def test_dict_field_to_db(self):
        field = DictField()
        obj = {"key": "value", "listkey": ["item1", "item2"]}
        result = field.get_db_prep_save(obj)
        self.assertEqual(obj, json.loads(result))

    def test_comma_delimited_string_list_field_to_python(self):
        field = CommaDelimitedStringListField()
        result = field.to_python('word1,word2,word3')
        self.assertEqual("word1", result[0])

    def test_comma_delimited_string_list_field_to_db(self):
        field = CommaDelimitedStringListField()
        result = field.get_db_prep_save(['word1', 'word2', 'word3'])
        self.assertEqual('word1,word2,word3', result)
