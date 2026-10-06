"""Read explicit observations; automatic checks never author visual acceptance."""
import json
from datetime import datetime
from pathlib import Path

from sparse_enclosure_corrections import sha


def visual_qa_status(root, observation_file, artifact, required_checks=()):
    root, observation_file = Path(root), Path(observation_file)
    if not observation_file.exists():
        return {'status': 'NOT_EVALUATED', 'reason': 'No observation record'}
    try:
        store = json.loads(observation_file.read_text())
        if store['schema_version'] != 1 or not isinstance(store['observations'], list):
            raise ValueError('Invalid observation schema')
        candidates = [record for record in store['observations'] if record['artifact'] == artifact]
        if not candidates:
            return {'status': 'NOT_EVALUATED', 'reason': 'No observation for this artifact'}
        record = candidates[-1]
        if not isinstance(record['observed_utc'], str):
            raise ValueError('Observation timestamp must be text')
        # Browser Date.toISOString() uses Z; support Python 3.9 as well as 3.11.
        observed = datetime.fromisoformat(record['observed_utc'].replace('Z', '+00:00'))
        if (observed.tzinfo is None or not record['observer'] or not record['method']
                or not record['scope'] or not record['evidence'] or not isinstance(record['checks'], dict)):
            raise ValueError('Observation metadata incomplete')
        result = {'status': 'STALE', 'observation': record}
        if record['artifact_sha256'] != sha(root / artifact):
            return {**result, 'reason': 'Current content differs from observed bytes'}
        for evidence in record['evidence']:
            path = root / evidence['path']
            if not path.is_file() or sha(path) != evidence['sha256']:
                return {**result, 'reason': 'Observation evidence missing or changed'}
        if record['status'] != 'PASS' or any(record['checks'].get(key) != 'PASS' for key in required_checks):
            return {'status': 'NOT_ACCEPTED', 'observation': record, 'reason': 'Required checks did not pass'}
        return {'status': 'PASS', 'observation': record,
                'reason': 'Same artifact bytes and evidence; only recorded scope accepted'}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {'status': 'INVALID', 'reason': f'Invalid observation record: {exc}'}
