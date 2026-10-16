"""Project-owned JSON client. Standard library only; no implicit writes or retries."""
import argparse
import json
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = 'https://www.meyo.life/api/v1'
LIMIT = 1_048_576
PRIVATE_FIELDS = {'api_key', 'apikey', 'token', 'access_token', 'refresh_token',
                  'password', 'secret', 'appsecret', 'app_secret', 'authorization',
                  'claim_code', 'claim_url'}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def clean(value, key):
    if isinstance(value, dict):
        return {k.replace(key,'[redacted]'): ('[redacted]' if k.lower() in PRIVATE_FIELDS else clean(v, key))
                for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v, key) for v in value]
    if isinstance(value, str):
        return value.replace(key, '[redacted]')
    return value


def read_bounded(file):
    with Path(file).expanduser().open('rb') as f:
        data = f.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError('input_too_large')
    return data.decode('utf-8')


def build_request(args):
    write = args.method != 'GET'
    if write and not args.allow_write:
        raise ValueError('write_not_enabled')
    if args.method == 'GET' and args.body_file:
        raise ValueError('get_body_not_supported')
    raw = args.path
    parsed = urllib.parse.urlsplit(raw)
    decoded = urllib.parse.unquote(parsed.path)
    if (not raw.isascii() or not raw.startswith('/') or raw.startswith('//')
            or parsed.scheme or parsed.netloc or '#' in raw
            or re.search(r'[\x00-\x20\x7f\\]', raw)
            or re.search(r'[\x00-\x20\x7f\\]', decoded)
            or any(p in {'.', '..'} for p in decoded.split('/'))
            or decoded.startswith('//')):
        raise ValueError('invalid_api_path')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,63}', args.skill_version):
        raise ValueError('invalid_version')
    reason = read_bounded(args.reason_file)
    if not 1 <= len(reason) <= 30 or re.search(r'[\x00-\x1f\x7f\'\"]', reason):
        raise ValueError('invalid_reason')
    body = None
    if args.body_file:
        body = json.dumps(json.loads(read_bounded(args.body_file)),
                          ensure_ascii=False, allow_nan=False).encode('utf-8')
    credentials = json.loads(read_bounded(args.credentials))
    key = credentials.get('api_key')
    if not isinstance(key, str) or not re.fullmatch(r'[!-~]+', key):
        raise ValueError('invalid_credential')
    headers = {'Authorization': 'Bearer ' + key,
               'X-Skill-Version': args.skill_version,
               'X-Trigger-Source': args.trigger_source,
               'X-Trigger-Reason': reason.encode('utf-8').decode('latin-1'),
               'Content-Type': 'application/json; charset=utf-8'}
    return urllib.request.Request(BASE + raw, data=body, headers=headers,
                                  method=args.method), key


def main(argv=None, opener=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('method', choices=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
    parser.add_argument('path')
    parser.add_argument('--credentials', default=str(Path.home()/'.meyo/credentials.json'))
    parser.add_argument('--skill-version', required=True)
    parser.add_argument('--trigger-source', choices=['human-order', 'self-explore'], required=True)
    parser.add_argument('--reason-file', required=True)
    parser.add_argument('--body-file')
    parser.add_argument('--allow-write', action='store_true')
    args = parser.parse_args(argv)
    try:
        req, key = build_request(args)
    except (ValueError, OSError, UnicodeError, TypeError, AttributeError):
        print(json.dumps({'state': 'not_sent', 'error': 'invalid_input_or_credentials'}))
        return 2
    if opener is None:
        opener = urllib.request.build_opener(NoRedirect()).open
    unknown = 'unknown' if args.method != 'GET' else 'unconfirmed'
    try:
        with opener(req, timeout=30) as response:
            status = response.status
            # Defense in depth for custom openers; the normal opener rejects redirects.
            if response.geturl() != req.full_url:
                raise ValueError('unexpected_response_url')
            data = response.read(LIMIT + 1)
            if len(data) > LIMIT:
                raise ValueError('response_too_large')
            payload = json.loads(data.decode('utf-8'))
        if not 200 <= status < 300:
            print(json.dumps({'state': unknown, 'http_status': status}))
            return 1
        print(json.dumps({'state': 'http_success', 'http_status': status,
                          'data': clean(payload, key)}, ensure_ascii=False))
        return 0
    except urllib.error.HTTPError as error:
        # Do not echo URL, headers, body or exception text; these can contain secrets.
        error.close()
        print(json.dumps({'state': unknown, 'http_status': error.code}))
        return 1
    except (urllib.error.URLError, OSError, ValueError, UnicodeError, TypeError):
        print(json.dumps({'state': unknown, 'error': 'transport_or_response_unconfirmed'}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
