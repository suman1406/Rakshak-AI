import ast
from pathlib import Path

def test_revision_identifiers_fit_postgresql_alembic_version_column():
    revisions = {}
    for path in (Path(__file__).parents[2] / 'alembic' / 'versions').glob('*.py'):
        assignments = {node.targets[0].id: ast.literal_eval(node.value) for node in ast.parse(path.read_text()).body if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in {'revision', 'down_revision'}}
        revision = assignments['revision']
        assert len(revision) <= 32, path.name
        assert revision not in revisions
        revisions[revision] = assignments['down_revision']
    assert all(parent is None or parent in revisions for parent in revisions.values())
