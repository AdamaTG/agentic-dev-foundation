import unittest
from examples.signalement import creer_signalement

class SignalementTests(unittest.TestCase):
    def test_description_obligatoire(self):
        for value in ("", "   ", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                creer_signalement(value)

    def test_identifiant_unique_et_statut(self):
        first = creer_signalement("Déchets sur la chaussée")
        second = creer_signalement("Déchets sur la chaussée")
        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual(first["statut"], "nouveau")
        self.assertTrue(first["id"].startswith("SIG-"))
