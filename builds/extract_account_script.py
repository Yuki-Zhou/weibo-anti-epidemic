import json
import os

token_file = "./tokens.json"
dst_dir = "./cache"
dst_filename = "account_name.txt"

if not os.path.exists(dst_dir):
    os.mkdir(dst_dir)

with open(token_file, "r", encoding="utf-8") as inf:
    next(inf)
    next(inf)
    next(inf)
    account2id = json.loads(inf.readline())

with open(os.path.join(dst_dir, dst_filename), "w", encoding="utf-8") as outf:
    for name in account2id:
        outf.write("{}\n".format(name))