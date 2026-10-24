"""The cached apt install action: pinned actions, and PR runs that never write the cache."""
from pathlib import Path
import re
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
ACTION = ROOT / 'actions/install-apt-packages/action.yml'


def steps():
    return yaml.load(ACTION.read_text(), Loader=yaml.BaseLoader)['runs']['steps']


class InstallAptPackagesTests(unittest.TestCase):
    def test_every_used_action_is_pinned_to_a_commit(self):
        for step in steps():
            if 'uses' in step:
                with self.subTest(step=step.get('name')):
                    self.assertRegex(step['uses'], r'@[0-9a-f]{40}$')

    def test_restore_and_save_use_the_same_key_and_path(self):
        restore = next(s for s in steps() if s.get('id') == 'restore')
        save = next(s for s in steps() if 'cache/save' in s.get('uses', ''))
        self.assertEqual(restore['with']['key'], save['with']['key'])
        self.assertEqual(restore['with']['path'], save['with']['path'])

    def test_by_default_only_pushes_to_the_default_branch_save(self):
        save = next(s for s in steps() if 'cache/save' in s.get('uses', ''))
        condition = re.sub(r'\s+', ' ', save['if'])
        self.assertIn("github.event_name == 'push'", condition)
        self.assertIn('github.ref_name == github.event.repository.default_branch', condition)
        self.assertIn("cache-hit != 'true'", condition)


if __name__ == '__main__':
    unittest.main()
