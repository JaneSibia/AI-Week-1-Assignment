import unittest
from crypto_advisor import CryptoAdvisor

class TestCryptoAdvisor(unittest.TestCase):
    def setUp(self):
        self.advisor = CryptoAdvisor()

    def test_get_most_sustainable(self):
        coin, data = self.advisor.get_most_sustainable()
        self.assertEqual(coin, 'cardano')  # Cardano should be most sustainable in our static DB
        self.assertEqual(self.advisor.crypto_db[coin]['sustainability_score'], 8)

    def test_analyze_price_trend(self):
        self.assertEqual(self.advisor.analyze_price_trend(6), "rising strongly")
        self.assertEqual(self.advisor.analyze_price_trend(3), "rising")
        self.assertEqual(self.advisor.analyze_price_trend(1), "stable")
        self.assertEqual(self.advisor.analyze_price_trend(-3), "falling")
        self.assertEqual(self.advisor.analyze_price_trend(-6), "falling sharply")

    def test_get_best_long_term(self):
        coin, score = self.advisor.get_best_long_term()
        self.assertIn(coin, self.advisor.crypto_db)
        self.assertIsInstance(score, float)

    def test_process_query_sustainability(self):
        response = self.advisor.process_query("What's the most sustainable cryptocurrency?")
        self.assertIn("sustainability", response.lower())
        self.assertIn("cardano", response.lower())

    def test_process_query_help(self):
        response = self.advisor.process_query("help")
        self.assertIn("help", response.lower())
        self.assertIn("price", response.lower())
        self.assertIn("sustainability", response.lower())

if __name__ == '__main__':
    unittest.main() 