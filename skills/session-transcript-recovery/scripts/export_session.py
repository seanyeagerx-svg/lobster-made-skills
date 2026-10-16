"""Export one authorized session from an existing SQLite snapshot, read-only."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys
import re

MAX_ROWS = 10_000
MAX_BYTES = 20 * 1024 * 1024


def export(database, session, output, start=0, end=None):
    db = Path(database).resolve(strict=True)
    target = Path(output).absolute()
    if not db.is_file() or not session or start < 0 or (end is not None and end < start):
        raise ValueError('invalid_scope')
    if target.exists() or target.is_symlink() or target.resolve() == db:
        raise ValueError('output_must_be_new')
    # Block sibling paths used by SQLite itself, including WAL/SHM sidecars.
    if target.resolve() in {Path(str(db)+s) for s in ['-wal','-shm','-journal']}:
        raise ValueError('output_conflicts_with_source')
    uri = db.as_uri() + '?mode=ro'
    connection = sqlite3.connect(uri, uri=True)
    try:
        connection.execute('PRAGMA query_only=ON')
        connection.execute('PRAGMA trusted_schema=OFF')
        kind = connection.execute("SELECT type,sql FROM sqlite_master WHERE name=?",
                                  ('transcript_events',)).fetchone()
        if (not kind or kind[0] != 'table' or not isinstance(kind[1],str)
                or not re.match(r'^\s*CREATE\s+TABLE\b',kind[1],re.IGNORECASE)):
            raise ValueError('unsupported_schema')
        columns = {r[1]:r[2] for r in connection.execute('PRAGMA table_info(transcript_events)')}
        if (not {'session_id','seq','event_json','created_at'} <= columns.keys()
                or columns['session_id'].strip().upper() != 'TEXT'):
            raise ValueError('unsupported_schema')
        # Unary + removes column affinity; BINARY removes inherited collations.
        clause = "typeof(session_id)='text' AND +session_id COLLATE BINARY=? AND seq>=?"
        params = [session, start]
        if end is not None:
            clause += ' AND seq<=?'
            params.append(end)
        connection.execute('BEGIN')
        count, size = connection.execute(
            'SELECT COUNT(*),COALESCE(SUM(LENGTH(CAST(event_json AS BLOB))+1),0) '
            'FROM transcript_events WHERE '+clause, params).fetchone()
        if count > MAX_ROWS or size > MAX_BYTES:
            raise ValueError('scope_too_large')
        rows = connection.execute('SELECT seq,event_json FROM transcript_events WHERE '
                                  +clause+' ORDER BY seq', params).fetchall()
        texts = []
        previous = None
        for seq, raw in rows:
            if not isinstance(seq, int) or not isinstance(raw, str) or '\n' in raw or '\r' in raw:
                raise ValueError('unsupported_event_encoding')
            if previous is not None and seq <= previous:
                raise ValueError('non_unique_sequence')
            previous = seq
            obj = json.loads(raw)
            if not isinstance(obj, dict):
                raise ValueError('unsupported_event_encoding')
            texts.append(raw + '\n')
        if sum(len(text.encode('utf-8')) for text in texts) > MAX_BYTES:
            raise ValueError('output_too_large')
        # No output is created before every selected record has been validated.
        with target.open('x', encoding='utf-8', newline='\n') as out:
            for text in texts:
                out.write(text)
        return {'rows': len(rows), 'first_seq': rows[0][0] if rows else None,
                'last_seq': rows[-1][0] if rows else None,
                'scope': 'selected_session_only', 'completeness': 'not_proven'}
    finally:
        connection.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', required=True)
    parser.add_argument('--session', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--start-seq', type=int, default=0)
    parser.add_argument('--end-seq', type=int)
    args = parser.parse_args(argv)
    try:
        result = export(args.database,args.session,args.output,args.start_seq,args.end_seq)
        print(json.dumps({'state':'exported',**result}))
        return 0
    except (OSError,ValueError,TypeError,sqlite3.Error):
        print(json.dumps({'state':'not_exported','error':'invalid_scope_schema_or_output'}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
