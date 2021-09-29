# import json

# """
# 根据replace和delete文件修改at数据！！！！
# """
# # token_file = "../builds/tokens.json"
# at_file = "../data/weibo_ats.json"
# replace_file = "./replace.txt"
# delete_file = "./delete.txt"

# with open(at_file, "r", encoding="utf-8") as inf:
#     weibo_ats = json.load(inf)
# replaces = {}
# with open(replace_file, "r", encoding="utf-8") as inf:
#     for line in inf:
#         splits = line.strip().split(" ")
#         replaces[splits[0]] = splits[1]
#         print(splits[0], splits[1])
# deletes = []
# with open(delete_file, "r", encoding="utf-8") as inf:
#     for line in inf:
#         deletes.append(line.strip())

# # Process in weibo_at
# to_delete_indexes = []
# to_add_indexes = []
# for weibo in weibo_ats:
#     for account in weibo_ats[weibo]:
#         if account in deletes:
#             to_delete_indexes.append((weibo, account))
#         elif account in replaces:
#             replace_account = replaces[account]
#             if replace_account not in weibo_ats[weibo]:
#                 to_add_indexes.append((weibo, replace_account, weibo_ats[weibo][account]))
#             else:
#                 weibo_ats[weibo][replace_account] += weibo_ats[weibo][account]
#             to_delete_indexes.append((weibo, account))

# for item in to_delete_indexes:
#     del weibo_ats[item[0]][item[1]]

# for item in to_add_indexes:
#     weibo_ats[item[0]][item[1]] = item[2]

# with open(at_file, "w", encoding="utf-8") as outf:
#     json.dump(weibo_ats, outf, ensure_ascii=False)


import json
account_cate = {}
with open("./account_category.txt", "r", encoding="utf-8") as inf:
    for line in inf:
        splits = line.strip().split("\t")
        if len(splits) < 2:
            continue
        account_cate[splits[0]] = int(splits[1])
with open("../builds/category.json", "w", encoding="utf-8") as outf:
    json.dump(account_cate, outf, ensure_ascii=False)
        
