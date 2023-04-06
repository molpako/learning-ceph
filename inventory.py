#!venv/bin/python
import json
import subprocess
import sys

# multipassのVMのリストを取得するコマンド
cmd = ['multipass', 'list', '--format', 'json']
result = subprocess.run(cmd, stdout=subprocess.PIPE)

# multipassコマンドの出力をJSONデータに変換する
instances = json.loads(result.stdout.decode('utf-8'))
names = [instance["name"] for instance in instances["list"]]

# Ansibleに渡すためのホストリストを作成する
host_vars = {}
for instance in instances["list"]:
    host_vars[instance["name"]] = {
        'ansible_host': instance['ipv4'][0],
        'ansible_port': 22,
        'ansible_user': 'ubuntu',
        'ansible_ssh_private_key_file': './multipass.key'
    }

# Ansibleが理解できる形式でJSONを出力する
if len(sys.argv) == 2 and sys.argv[1] == '--list':
    # --listフラグが渡された場合、ホストリスト全体を出力する
    print(json.dumps({'_meta': {'hostvars': host_vars}, 'all': {'hosts': names}}))
elif len(sys.argv) == 3 and sys.argv[1] == '--host':
    # --hostフラグが渡された場合、指定されたホストの情報を出力する
    hostname = sys.argv[2]
    host = next((name for name in names if name == hostname), None)
    if host:
        print(json.dumps({'_meta': {'hostvars': {}}, 'host': host}))
    else:
        print(json.dumps({'_meta': {'hostvars': {}}, 'host': {}}))
else:
    # それ以外の場合は空のJSONを出力する
    print(json.dumps({'_meta': {'hostvars': {}}, 'all': {'hosts': []}}))
