"""Read-only guard for a deliberately narrow IMAP setup candidate; not a sandbox proof."""
import argparse
import copy
import json
from pathlib import Path
import re
import sys

DENY = {'group:fs','group:runtime','group:web','browser','cron','gateway','nodes'}
ACCOUNT_FIELDS = {'host','port','secure','user','mailbox','password','allowedSenders',
                  'senderAuth','addressTokens','agentId','deliver','watch','includeBody','maxBytes'}
LIMIT = 2 * 1024 * 1024


def load(file):
    with Path(file).open('rb') as source:
        raw = source.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError('config_too_large')
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result: raise ValueError('duplicate_key')
            result[key]=value
        return result
    def reject_constant(value):
        raise ValueError('nonstandard_json_constant')
    value = json.loads(raw.decode('utf-8'),object_pairs_hook=unique,
                       parse_constant=reject_constant)
    if not isinstance(value, dict): raise ValueError('config_object_required')
    return value


def check(candidate, baseline):
    errors=[]
    agents=candidate.get('agents',{})
    if not isinstance(agents,dict) or agents.get('ownership')!='explicit':
        errors.append('agents.ownership_required')
    entries=agents.get('entries',{}) if isinstance(agents,dict) else {}
    if not isinstance(entries,dict): entries={}
    if (not isinstance(candidate.get('bindings'),list)
            or not isinstance(baseline.get('bindings'),list)
            or candidate['bindings']!=baseline['bindings']):
        errors.append('bindings_changed_or_missing')
    try:
        plugin=candidate['plugins']['entries']['imap']
        accounts=plugin['config']['accounts']
        if plugin.get('enabled') is not True or not isinstance(accounts,dict) or not accounts:
            raise ValueError()
    except (KeyError,TypeError,AttributeError,ValueError):
        return errors+['imap_accounts_required']
    old_entries=baseline.get('agents',{}).get('entries',{})
    if not isinstance(old_entries,dict):
        return errors+['baseline_agents_invalid']
    # This setup may add readers, but never repurpose an existing agent.
    for name, original in old_entries.items():
        if entries.get(name)!=original:
            errors.append('existing_agent_changed')
            break
    binding_agents={x.get('agentId') for x in baseline.get('bindings',[]) if isinstance(x,dict)}
    readers=set()
    if set(plugin)!={'enabled','config'} or set(plugin['config'])!={'accounts'}:
        errors.append('unsupported_imap_plugin_fields')
    for account in accounts.values():
        if not isinstance(account,dict):
            errors.append('account_object_required'); continue
        if set(account)-ACCOUNT_FIELDS:
            errors.append('unsupported_account_fields')
        if (account.get('host')!='imap.gmail.com' or type(account.get('port')) is not int
                or account['port']!=993 or account.get('secure') is not True
                or account.get('mailbox')!='INBOX'):
            errors.append('gmail_tls_inbox_required')
        if not isinstance(account.get('user'),str) or not account['user'].strip():
            errors.append('account_user_required')
        secret=account.get('password')
        if (not isinstance(secret,dict) or set(secret)!={'source','provider','id'}
                or secret.get('source')!='store'
                or not all(isinstance(secret.get(k),str) and secret[k].strip() for k in ['provider','id'])):
            errors.append('store_secret_ref_required')
        senders=account.get('allowedSenders')
        if (not isinstance(senders,list) or not senders
                or any(not isinstance(s,str) or '*' in s or not re.fullmatch(
                    r'(?:[A-Za-z0-9.!#$%&+\-/=?^_`{|}~]+)?@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}',s)
                    for s in senders)):
            errors.append('narrow_sender_allowlist_required')
        auth=account.get('senderAuth')
        if isinstance(auth,dict) and set(auth)-{'min','trustedAuthservIds','acceptTrustedAuthservId'}:
            errors.append('unsupported_sender_auth_fields')
        if (not isinstance(auth,dict) or auth.get('min')!='verified'
                or auth.get('acceptTrustedAuthservId',False) is not False
                or account.get('addressTokens')):
            errors.append('verified_without_bypass_required')
        if 'watch' in account:
            watch=account['watch']
            if (not isinstance(watch,dict) or set(watch)-{'mode','pollSeconds'}
                    or watch.get('mode','auto') not in {'auto','interval'}
                    or ('pollSeconds' in watch and (type(watch['pollSeconds']) is not int or watch['pollSeconds']<15))):
                errors.append('unsupported_watch_fields')
        if account.get('deliver') is not False:
            errors.append('delivery_must_be_off')
        reader_id=account.get('agentId')
        reader=entries.get(reader_id) if isinstance(reader_id,str) else None
        if not reader_id or reader_id=='main' or reader_id in binding_agents or not isinstance(reader,dict):
            errors.append('dedicated_reader_required');continue
        readers.add(reader_id)
        if set(reader)-{'workspace','model','sandbox','tools'}:
            errors.append('unsupported_reader_fields')
        if not isinstance(reader.get('model'),str) or not reader['model'].strip():
            errors.append('reader_model_required')
        sandbox=reader.get('sandbox',{})
        if (not isinstance(sandbox,dict) or sandbox.get('mode')!='all'
                or sandbox.get('scope')!='session' or sandbox.get('workspaceAccess')!='none'
                or set(sandbox)!={'mode','scope','workspaceAccess'}):
            errors.append('isolated_sandbox_required')
        tools=reader.get('tools',{})
        if (not isinstance(tools,dict) or set(tools)-{'profile','allow','deny'}
                or tools.get('profile')!='minimal'
                or tools.get('allow')!=['session_status']
                or not isinstance(tools.get('deny'),list)
                or any(not isinstance(x,str) for x in tools.get('deny',[]))
                or not DENY <= set(tools.get('deny',[]))):
            errors.append('minimal_reader_tools_required')
    # Compare the whole document: only enable this narrow plugin and add its readers.
    previous_accounts=baseline.get('plugins',{}).get('entries',{}).get('imap',{}).get('config',{}).get('accounts',{})
    if not isinstance(previous_accounts,dict) or any(accounts.get(k)!=v for k,v in previous_accounts.items()):
        errors.append('existing_imap_account_changed')
    expected=copy.deepcopy(baseline)
    expected.setdefault('agents',{})['ownership']='explicit'
    expected['agents'].setdefault('entries',{})
    for reader_id in readers:
        if reader_id not in old_entries:
            expected['agents']['entries'][reader_id]=entries[reader_id]
    expected.setdefault('plugins',{}).setdefault('entries',{})['imap']=plugin
    if expected!=candidate:
        errors.append('unrelated_configuration_changed')
    return sorted(set(errors))


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',required=True)
    p.add_argument('--baseline',required=True)
    args=p.parse_args(argv)
    try:
        errors=check(load(args.candidate),load(args.baseline))
    except (OSError,ValueError,TypeError,AttributeError):
        errors=['invalid_input_json']
    print(json.dumps({'candidate_checks':'failed' if errors else 'passed',
                      'errors':errors,'runtime_validation':'not_performed'}))
    return 1 if errors else 0


if __name__=='__main__':sys.exit(main())
