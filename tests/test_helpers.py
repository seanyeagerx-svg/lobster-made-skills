"""Synthetic fixtures only. No real credentials, messages, gateway or network."""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
import urllib.error

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]


def module(skill,filename):
    spec=importlib.util.spec_from_file_location(filename,ROOT/'skills'/skill/'scripts'/(filename+'.py'))
    value=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


api=module('meyo-api','meyo_api')
imap=module('gmail-imap-integration','check_candidate')
recovery=module('session-transcript-recovery','export_session')


class Response:
    status=200
    def __init__(self,url,payload):self.url=url;self.payload=payload
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def geturl(self):return self.url
    def read(self,size):return self.payload[:size]


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.key='synthetic-fixture-value'
        (self.root/'creds.json').write_text(json.dumps({'api_key':self.key}),encoding='utf-8')
        (self.root/'reason.txt').write_text('我按要求核对结果',encoding='utf-8')
        (self.root/'body.json').write_text(json.dumps({'content':'你好'},ensure_ascii=False),encoding='utf-8')
        self.calls=[]
    def run_client(self,method='GET',path='/feeds?sort=new',extra=(),opener=None):
        args=[method,path,'--credentials',str(self.root/'creds.json'),'--reason-file',str(self.root/'reason.txt'),
              '--skill-version','fixture-1','--trigger-source','human-order',*extra]
        def mock(req,timeout):
            self.calls.append(req)
            return Response(req.full_url,b'{"ok":true}')
        output=io.StringIO()
        with contextlib.redirect_stdout(output):code=api.main(args,opener=opener or mock)
        return code,output.getvalue()
    def test_destination_and_query_are_exact(self):
        code,_=self.run_client(path='/feeds?q=a%2Bb&sort=new')
        self.assertEqual(code,0)
        self.assertEqual(self.calls[0].full_url,api.BASE+'/feeds?q=a%2Bb&sort=new')
        self.assertEqual(self.calls[0].get_header('Authorization'),'Bearer '+self.key)
    def test_chinese_body_and_header_roundtrip(self):
        code,_=self.run_client('POST',extra=['--allow-write','--body-file',str(self.root/'body.json')])
        self.assertEqual(code,0)
        self.assertEqual(json.loads(self.calls[0].data)['content'],'你好')
        self.assertEqual(self.calls[0].get_header('X-trigger-reason').encode('latin-1').decode('utf-8'),'我按要求核对结果')
    def test_write_without_opt_in_never_calls_transport(self):
        self.assertEqual(self.run_client('POST')[0],2);self.assertEqual(self.calls,[])
    def test_external_or_ambiguous_paths_rejected(self):
        for value in ['https://other.invalid/api','//other.invalid/api','/../private','/%2e%2e/private',
                      '/feeds#fragment','/feeds#','/x\\y','/x\nheader','/中文']:
            with self.subTest(value=value):self.assertEqual(self.run_client(path=value)[0],2)
        self.assertEqual(self.calls,[])
    def test_reason_controls_and_quotes_rejected(self):
        for value in ['a\nb','a\rb','a"b',"a'b",'a'*31,'']:
            (self.root/'reason.txt').write_text(value,encoding='utf-8')
            with self.subTest(value=value):self.assertEqual(self.run_client()[0],2)
        self.assertEqual(self.calls,[])
    def test_redirect_handler_does_not_forward_auth(self):
        self.assertIsNone(api.NoRedirect().redirect_request(None,None,302,'',{},'https://other.invalid'))
    def test_http_error_body_and_secret_not_logged(self):
        def reject(req,timeout):
            self.calls.append(req)
            raise urllib.error.HTTPError(req.full_url,401,'secret '+self.key,{},io.BytesIO(self.key.encode()))
        code,out=self.run_client(opener=reject)
        self.assertEqual(code,1);self.assertNotIn(self.key,out)
        self.assertEqual(json.loads(out)['http_status'],401)
    def test_write_timeout_unknown_and_not_retried(self):
        def timeout(req,timeout):
            self.calls.append(req);raise urllib.error.URLError('contains '+self.key)
        code,out=self.run_client('POST',extra=['--allow-write'],opener=timeout)
        self.assertEqual(code,1);self.assertEqual(len(self.calls),1)
        self.assertEqual(json.loads(out)['state'],'unknown');self.assertNotIn(self.key,out)
    def test_response_redacts_fields_and_exact_credential(self):
        def reply(req,timeout):return Response(req.full_url,json.dumps({'token':'hidden','nested':{'api_key':'hidden'},'text':self.key}).encode())
        code,out=self.run_client(opener=reply)
        self.assertEqual(code,0);self.assertNotIn('hidden',out);self.assertNotIn(self.key,out)
    def test_credential_in_response_property_name_is_redacted(self):
        def reply(req,timeout):return Response(req.full_url,json.dumps({self.key:'value'}).encode())
        code,out=self.run_client(opener=reply)
        self.assertEqual(code,0);self.assertNotIn(self.key,out)
    def test_invalid_response_does_not_claim_write_failed(self):
        def reply(req,timeout):return Response(req.full_url,b'not JSON')
        code,out=self.run_client('PUT',extra=['--allow-write'],opener=reply)
        self.assertEqual(code,1);self.assertEqual(json.loads(out)['state'],'unknown')
    def test_get_body_is_rejected(self):
        self.assertEqual(self.run_client(extra=['--body-file',str(self.root/'body.json')])[0],2)


def configs():
    baseline={'agents':{'entries':{'main':{'workspace':'./main'}}},
              'bindings':[{'agentId':'main','match':{'channel':'fixture','accountId':'*'}}],
              'gateway':{'bind':'loopback'}}
    candidate=copy.deepcopy(baseline)
    candidate['agents']['ownership']='explicit'
    candidate['agents']['entries']['reader']={'workspace':'./reader','model':'fixture/model',
        'sandbox':{'mode':'all','scope':'session','workspaceAccess':'none'},
        'tools':{'profile':'minimal','allow':['session_status'],'deny':sorted(imap.DENY)}}
    candidate['plugins']={'entries':{'imap':{'enabled':True,'config':{'accounts':{'fixture':{
        'host':'imap.gmail.com','port':993,'secure':True,'user':'reader@example.com','mailbox':'INBOX',
        'password':{'source':'store','provider':'default','id':'FIXTURE_IMAP'},
        'allowedSenders':['trusted@example.com','@example.org'],
        'senderAuth':{'min':'verified','acceptTrustedAuthservId':False},'agentId':'reader','deliver':False}}}}}}
    return candidate,baseline


class ImapTests(unittest.TestCase):
    def setUp(self):
        self.c,self.b=configs()
        self.a=self.c['plugins']['entries']['imap']['config']['accounts']['fixture']
        self.r=self.c['agents']['entries']['reader']
    def test_valid_candidate_and_no_mutation(self):
        before=copy.deepcopy(self.c);self.assertEqual(imap.check(self.c,self.b),[]);self.assertEqual(before,self.c)
    def test_primary_reader_rejected(self):
        self.a['agentId']='main';self.assertIn('dedicated_reader_required',imap.check(self.c,self.b))
    def test_weak_sender_auth_rejected(self):
        for value in ['asserted','unverified',None]:
            self.a['senderAuth']['min']=value
            self.assertIn('verified_without_bypass_required',imap.check(self.c,self.b))
    def test_sender_token_bypass_rejected(self):
        self.a['addressTokens']=[{'token':'fixture-only','senders':['trusted@example.com']}]
        self.assertIn('verified_without_bypass_required',imap.check(self.c,self.b))
    def test_empty_or_wildcard_senders_rejected(self):
        for value in [[],['*'],['@'],['Display Name <trusted@example.com>']]:
            self.a['allowedSenders']=value
            self.assertIn('narrow_sender_allowlist_required',imap.check(self.c,self.b))
    def test_secret_must_be_reference(self):
        self.a['password']='fixture-plaintext';self.assertIn('store_secret_ref_required',imap.check(self.c,self.b))
    def test_delivery_not_enabled_during_setup(self):
        self.a['deliver']=True;self.assertIn('delivery_must_be_off',imap.check(self.c,self.b))
    def test_tool_additions_and_missing_deny_rejected(self):
        self.r['tools']['alsoAllow']=['exec'];self.assertIn('minimal_reader_tools_required',imap.check(self.c,self.b))
        self.r['tools'].pop('alsoAllow');self.r['tools']['deny'].remove('gateway')
        self.assertIn('minimal_reader_tools_required',imap.check(self.c,self.b))
    def test_sandbox_host_mount_or_override_rejected(self):
        self.r['sandbox']['workspaceAccess']='rw';self.assertIn('isolated_sandbox_required',imap.check(self.c,self.b))
    def test_channel_route_change_rejected(self):
        self.c['bindings']=[];self.assertIn('bindings_changed_or_missing',imap.check(self.c,self.b))
    def test_unrelated_gateway_or_existing_agent_change_rejected(self):
        self.c['gateway']['bind']='lan';self.assertIn('unrelated_configuration_changed',imap.check(self.c,self.b))
        self.c,self.b=configs();self.c['agents']['entries']['main']['workspace']='./other'
        self.assertIn('existing_agent_changed',imap.check(self.c,self.b))
    def test_existing_imap_account_not_overwritten(self):
        self.b['plugins']=copy.deepcopy(self.c['plugins'])
        self.a['allowedSenders']=['new@example.com']
        self.assertIn('existing_imap_account_changed',imap.check(self.c,self.b))
    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'config.json';p.write_text('{"agents":{},"agents":{}}')
            with self.assertRaises(ValueError):imap.load(p)
    def test_nonstandard_json_constants_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'config.json'
            for constant in ['NaN','Infinity','-Infinity']:
                with self.subTest(constant=constant):
                    p.write_text('{"metric":'+constant+'}',encoding='utf-8')
                    with self.assertRaises(ValueError):imap.load(p)
    def test_unknown_account_and_auth_fields_rejected(self):
        self.a['futureAuthBypass']=True
        self.assertIn('unsupported_account_fields',imap.check(self.c,self.b))
        self.a.pop('futureAuthBypass');self.a['senderAuth']['futureAuthBypass']=True
        self.assertIn('unsupported_sender_auth_fields',imap.check(self.c,self.b))


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.db=self.root/'snapshot.sqlite';self.out=self.root/'result.jsonl'
        with contextlib.closing(sqlite3.connect(self.db)) as c, c:
            c.execute('CREATE TABLE transcript_events(session_id TEXT,seq INTEGER,event_json TEXT,created_at INTEGER)')
            c.executemany('INSERT INTO transcript_events VALUES(?,?,?,?)',[
                ('wanted',2,'{"role":"assistant","text":"原文二"}',20),
                ('other',1,'{"role":"user","text":"unrelated-private-fixture"}',10),
                ('wanted',1,'{"role":"user","text":"原文一"}',10)])
    def test_exact_session_order_raw_text_and_source_unchanged(self):
        before=hashlib.sha256(self.db.read_bytes()).digest()
        result=recovery.export(self.db,'wanted',self.out)
        self.assertEqual(result['rows'],2)
        self.assertEqual(self.out.read_text(encoding='utf-8'),'{"role":"user","text":"原文一"}\n{"role":"assistant","text":"原文二"}\n')
        self.assertEqual(hashlib.sha256(self.db.read_bytes()).digest(),before)
    def test_range_does_not_include_earlier_rows(self):
        self.assertEqual(recovery.export(self.db,'wanted',self.out,2,2)['rows'],1)
    def test_sql_injection_like_session_is_data(self):
        self.assertEqual(recovery.export(self.db,"' OR 1=1 --",self.out)['rows'],0)
    def test_existing_output_or_database_never_overwritten(self):
        self.out.write_text('keep')
        with self.assertRaises(ValueError):recovery.export(self.db,'wanted',self.out)
        with self.assertRaises(ValueError):recovery.export(self.db,'wanted',self.db)
        self.assertEqual(self.out.read_text(),'keep')
    def test_invalid_json_does_not_create_partial_export(self):
        with contextlib.closing(sqlite3.connect(self.db)) as c, c:c.execute('UPDATE transcript_events SET event_json=? WHERE session_id=? AND seq=2',('broken','wanted'))
        with self.assertRaises(ValueError):recovery.export(self.db,'wanted',self.out)
        self.assertFalse(self.out.exists())
    def test_missing_schema_rejected(self):
        blank=self.root/'blank.sqlite'
        sqlite3.connect(blank).close()
        with self.assertRaises(ValueError):recovery.export(blank,'wanted',self.out)
    def test_view_is_not_accepted_as_source_table(self):
        view=self.root/'view.sqlite'
        with contextlib.closing(sqlite3.connect(view)) as c, c:c.execute('CREATE VIEW transcript_events AS SELECT 1 AS seq')
        with self.assertRaises(ValueError):recovery.export(view,'wanted',self.out)
    def test_size_and_row_limits_stop_before_output(self):
        old=recovery.MAX_ROWS;recovery.MAX_ROWS=1
        try:
            with self.assertRaises(ValueError):recovery.export(self.db,'wanted',self.out)
        finally:recovery.MAX_ROWS=old
        self.assertFalse(self.out.exists())
        old=recovery.MAX_BYTES;recovery.MAX_BYTES=1
        try:
            with self.assertRaises(ValueError):recovery.export(self.db,'wanted',self.out)
        finally:recovery.MAX_BYTES=old
    def test_invalid_range_rejected(self):
        with self.assertRaises(ValueError):recovery.export(self.db,'wanted',self.out,3,1)
    def test_duplicate_sequences_are_not_claimed_ordered(self):
        with contextlib.closing(sqlite3.connect(self.db)) as c, c:c.execute('INSERT INTO transcript_events VALUES(?,?,?,?)',('wanted',1,'{}',30))
        with self.assertRaises(ValueError):recovery.export(self.db,'wanted',self.out)
    def test_nocase_column_does_not_mix_different_session_ids(self):
        folded=self.root/'nocase.sqlite'
        with contextlib.closing(sqlite3.connect(folded)) as c, c:
            c.execute('CREATE TABLE transcript_events(session_id TEXT COLLATE NOCASE,seq INTEGER,event_json TEXT,created_at INTEGER)')
            c.executemany('INSERT INTO transcript_events VALUES(?,?,?,?)',[
                ('wanted',1,'{"text":"wanted"}',1),('WANTED',2,'{"text":"other-session"}',2)])
        self.assertEqual(recovery.export(folded,'wanted',self.out)['rows'],1)
        self.assertNotIn('other-session',self.out.read_text(encoding='utf-8'))
    def test_virtual_table_rejected_even_with_no_rows(self):
        virtual=self.root/'virtual.sqlite'
        with contextlib.closing(sqlite3.connect(virtual)) as c, c:
            c.execute('CREATE VIRTUAL TABLE transcript_events USING fts5(session_id,seq,event_json,created_at)')
        with self.assertRaises(ValueError):recovery.export(virtual,'none',self.out)
    def test_numeric_session_schema_is_rejected(self):
        for declared,requested in [('INTEGER','01'),('NUMERIC','1e0')]:
            with self.subTest(declared=declared):
                numeric=self.root/(declared+'.sqlite')
                with contextlib.closing(sqlite3.connect(numeric)) as c, c:
                    c.execute('CREATE TABLE transcript_events(session_id '+declared+',seq INTEGER,event_json TEXT,created_at INTEGER)')
                    c.execute('INSERT INTO transcript_events VALUES(1,1,?,1)',('{"text":"other-id"}',))
                with self.assertRaises(ValueError):recovery.export(numeric,requested,self.out)
                self.assertFalse(self.out.exists())
    def test_text_session_ids_are_not_normalized_as_numbers(self):
        with contextlib.closing(sqlite3.connect(self.db)) as c, c:
            c.executemany('INSERT INTO transcript_events VALUES(?,?,?,?)',[
                ('01',1,'{"text":"exact-id"}',1),('1',2,'{"text":"other-id"}',2)])
        self.assertEqual(recovery.export(self.db,'01',self.out)['rows'],1)
        self.assertNotIn('other-id',self.out.read_text(encoding='utf-8'))
    def test_output_byte_limit_applies_to_utf8_from_utf16_database(self):
        utf16=self.root/'utf16.sqlite'
        with contextlib.closing(sqlite3.connect(utf16)) as c, c:
            c.execute("PRAGMA encoding='UTF-16'")
            c.execute('CREATE TABLE transcript_events(session_id TEXT,seq INTEGER,event_json TEXT,created_at INTEGER)')
            c.execute('INSERT INTO transcript_events VALUES(?,?,?,?)',('wanted',1,json.dumps({'text':'汉'*100},ensure_ascii=False),1))
        old=recovery.MAX_BYTES;recovery.MAX_BYTES=250
        try:
            with self.assertRaises(ValueError):recovery.export(utf16,'wanted',self.out)
        finally:recovery.MAX_BYTES=old
        self.assertFalse(self.out.exists())


if __name__=='__main__':unittest.main()
