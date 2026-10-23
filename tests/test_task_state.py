import unittest
from tools.task_state import apply

class StateTests(unittest.TestCase):
    def setUp(self):
        self.data = {"schema_version": 1, "tasks": {}}
        apply(self.data, "init", "TASK-A", scope="Exemple", criteria=["AC-001"], max_attempts=2)

    def test_no_completion_without_approval(self):
        apply(self.data, "set", "TASK-A", status="ready")
        apply(self.data, "set", "TASK-A", status="in_progress")
        apply(self.data, "set", "TASK-A", status="verifying")
        apply(self.data, "set", "TASK-A", status="awaiting_approval")
        with self.assertRaises(ValueError):
            apply(self.data, "set", "TASK-A", status="done")

    def test_reject_invalid_transition(self):
        with self.assertRaises(ValueError):
            apply(self.data, "set", "TASK-A", status="done")

    def test_attempt_limit(self):
        for _ in range(2):
            apply(self.data, "set", "TASK-A", status="ready")
            apply(self.data, "set", "TASK-A", status="in_progress")
            apply(self.data, "set", "TASK-A", status="blocked", note="Test")
        apply(self.data, "set", "TASK-A", status="ready")
        with self.assertRaises(ValueError):
            apply(self.data, "set", "TASK-A", status="in_progress")
