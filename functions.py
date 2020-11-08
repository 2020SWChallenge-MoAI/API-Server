def isValidBid(bid):
    import os
    import re
    from config import config
    from database.book import Book

    qresult = Book.query.filter_by(bid=bid).all()

    if len(qresult) == 0:
        return False
    else:
        return True

def getDBURI():
    from config import config, secret

    return f"{config.DB_TYPE}+{config.DB_DRIVER}://{config.DB_USER}:{secret.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"

def getKeywordExtractor():
    from keyext import preprocess, KeywordExtractor
    from config import config
    import os
    import re

    # TODO : pkl 파일은 외부에서 만들어 넣어주는 형식이라 생각하자. => build 함수 지워도 됨 (config.BOOK_TEXT_DIR을 사용함)
    def buildKeywordExtractionDataFile(extractor):
        build_data = []
        for i, bid in enumerate(sorted([int(x.split(".")[0]) for x in os.listdir(config.BOOK_TEXT_DIR) if (re.compile("^\d+[.]txt$").match(x) != None)])):
            with open(os.path.join(config.MODEL_DIR, str(bid) + ".txt"), "r") as f:
                text = f.read()
            
            build_data.append([bid, preprocess(text)])
        
        extractor.build(build_data)
        extractor.save(os.path.join(config.MODEL_DIR, "keyext", config.KEYWORD_DATA_FILE_NAME))

    keyword_extractor = KeywordExtractor()

    # NOTE : 로드 방식 바뀌어서 파일 이름 체크만으로는 빌드 여부 확인 못함. 일단 주석처리해놓음
    # if config.KEYWORD_DATA_FILE_NAME not in os.listdir(os.path.join(config.MODEL_DIR, "keyext")):
    #    buildKeywordExtractionDataFile(keyword_extractor)
    
    keyword_extractor.load(os.path.join(config.MODEL_DIR, "keyext", config.KEYWORD_DATA_FILE_NAME))

    return keyword_extractor

def subword_tokenizer(sent, n=3):
    def subword(token, n):
        if len(token) <= n:
            return [token]

        return [token[i:i+n] for i in range(len(token) - n + 1)]

    return [sub for token in sent.split() for sub in subword(token, n)]

def komoran_tokenizer(sent):
    from init_once import komoran

    words = komoran.pos(sent, join=True)
    words = [w for w in words if ('/NN' in w or '/XR' in w or '/VA' in w or '/VV' in w)]
    return words

def isValidQuestion(bid, question):
    import os
    from config import config
    from init_once import electra

    path = os.path.join(config.BOOK_DIR, str(bid), "text.txt")
    with open(path, "r", encoding="utf-8") as f:
        text_by_lines = f.readlines()
    
    text = "".join(text_by_lines[1:])

    score = electra.get_answer(question=question, context=text)[0]["score"]

    # DEBUG CODE
    print(f"{score} - {question}")

    if score >= config.QNA_QUESTION_VALID_SCORE_THRESHOLD:
        return True
    else:
        return False

def isValidAnswer(bid, question, type, answer):
    import os
    from config import config
    from init_once import electra
    from model.qna.utils import f1_score

    path = os.path.join(config.BOOK_DIR, str(bid), "text.txt")
    with open(path, "r", encoding="utf-8") as f:
        text_by_lines = f.readlines()
    
    text = "".join(text_by_lines[1:])

    electra_answer = electra.get_answer(question=question, context=text, topk=1)[0]["answer"]

    if type == 0:
        choices = answer.split("#@@#")
        answer = int(choices[0])
        choices = choices[1:]

        scores = []
        for choice in choices:
            scores.append(f1_score(electra_answer, choice))
        
        if answer == [(i + 1) for i, s in enumerate(scores) if s == max(scores)][0]:
            return True
        else:
            return False
    else:  # type == 1
        score = f1_score(electra_answer, answer)

        if score >= config.QNA_ANSWER_VALID_SCORE_THRESHOLD:
            return True
        else:
            return False

def getUserReadBookBids(uid, num=-1):
    from database.user_book import User_Book
    from sqlalchemy import desc

    qresult = User_Book.query.filter_by(uid=uid).order_by(desc(User_Book.read_at)).all()
    read_book_bids = []
    appeared_bids = []
    for row in qresult:
        if row.bid not in appeared_bids:
            read_book_bids.append({
                "bid": row.bid,
                "read_at": row.read_at.isoformat()
            })
            appeared_bids.append(row.bid)
        
        if num != -1 and len(read_book_bids) == num:
            break
    
    if num != -1:
        read_book_bids = read_book_bids[:num]
    
    return read_book_bids

def getUserWorkWids(uid):
    from database.work import Work
    from sqlalchemy import desc

    def convertDateTimeToMonthStr(datetime):
        return datetime.strftime("%Y-%m")

    qresult = Work.query.filter_by(uid=uid).order_by(desc(Work.updated_at)).all()

    wids = []
    monthly_grade = {}
    for row in qresult:
        wids.append(row.wid)
        
        month_str = convertDateTimeToMonthStr(row.updated_at)
        if month_str not in monthly_grade.keys():
            monthly_grade[month_str] = {}
            monthly_grade[month_str]["understanding"] = 0
            monthly_grade[month_str]["sincerity"] = 0
            monthly_grade[month_str]["creativity"] = 0

        monthly_grade[month_str]["understanding"] += row.max_depth + row.avg_child_num
        monthly_grade[month_str]["sincerity"] += row.morethan2child_node_num - row.max_depth_diff - row.template_node_balance
        monthly_grade[month_str]["creativity"] += row.user_created_node_num - row.ai_support_num - row.duplicate_node
    
    return wids, monthly_grade

def gradeMindmap(mindmap):
    def getTree(nodes):
        nodes_dict = {}
        for node in nodes:
            if "label" in node.keys():
                if len(node["label"]) != 0:
                    nodes_dict[node["id"]] = {
                        "id": node["id"],
                        "label": node["label"],
                        "parent": node["parent"],
                        "child": []
                    }
            else:
                nodes_dict[node["id"]] = {
                    "id": node["id"],
                    "parent": node["parent"],
                    "child": []
                }

        root = nodes_dict[0]

        def appendChildRecursive(current):
            for key in nodes_dict.keys():
                if nodes_dict[key]["parent"] == current["id"]:
                    current["child"].append(nodes_dict[key])
            
            for item in current["child"]:
                appendChildRecursive(item)
        
        appendChildRecursive(root)

        return root
    
    def calcMaxDepth(tree):
        max_depth = 0

        def recursive(node, cur_depth):
            nonlocal max_depth
            if len(node["child"]) == 0: # if leaf node
                if max_depth < cur_depth:
                    max_depth = cur_depth

                return
            
            for child in node["child"]:
                recursive(child, cur_depth + 1)
        
        recursive(tree, 0)

        return max_depth
    
    def calcMinDepth(tree):
        min_depth = 999999

        def recursive(node, cur_depth):
            nonlocal min_depth
            if len(node["child"]) == 0: # if leaf node
                if min_depth > cur_depth:
                    min_depth = cur_depth

                return
            
            for child in node["child"]:
                recursive(child, cur_depth + 1)
        
        recursive(tree, 0)

        return min_depth

    def calcAvgChildNum(tree):
        child_num_sum = 0
        child_num_count = 0

        def recursive(node):
            nonlocal child_num_sum, child_num_count
            if len(node["child"]) == 0:
                return

            child_num_sum += len(node["child"])
            child_num_count += 1

            for item in node["child"]:
                recursive(item)

        recursive(tree)

        return child_num_sum // child_num_count

    def countHighDepthNode(tree, depth):
        count = 0

        def recursive(node, cur_depth):
            nonlocal count

            if cur_depth > depth:
                count += 1
            
            for child in node["child"]:
                recursive(child, cur_depth + 1)
        
        recursive(tree, 0)

        return count
    
    def calcMaxDepthDiff(tree):
        max_depth = calcMaxDepth(tree)
        min_depth = calcMinDepth(tree)

        return max_depth - min_depth

    def countDescendantNum(tree):
        count = 0

        def recursive(node):
            nonlocal count

            count += len(node["child"])

            for item in node["child"]:
                recursive(item)
        
        recursive(tree)

        return count

    def calcTemplateNodeBalance(tree):
        child_nums = []
        for item in tree["child"]:
            if len(str(item["id"])) < 3:  # if template node
                child_nums.append(countDescendantNum(item))
        
        return max(child_nums) - min(child_nums)

    def countUserCreatedNodeNum(tree):
        count = 0

        def recursive(node):
            nonlocal count

            if len(str(node["id"])) >= 3:
                count += 1
            
            for item in node["child"]:
                recursive(item)
        
        recursive(tree)

        return count

    def countDuplicateNodes(tree):
        count = 0
        label_list = []

        def recursive(node):
            nonlocal count

            if "label" in node.keys():
                label = node["label"]

                if label in label_list:
                    count += 1
                else:
                    label_list.append(label)
            
            for item in node["child"]:
                recursive(item)

        return count

    tree = getTree(mindmap["nodes"])
    
    max_depth = calcMaxDepth(tree)
    avg_child_num = calcAvgChildNum(tree)
    morethan2child_node_num = countHighDepthNode(tree, 2)
    max_depth_diff = calcMaxDepthDiff(tree)
    template_node_balance = calcTemplateNodeBalance(tree)
    user_created_node_num = countUserCreatedNodeNum(tree)
    ai_support_num = mindmap["aiSupportCount"]
    duplicate_node = countDuplicateNodes(tree)

    return max_depth, avg_child_num, morethan2child_node_num, max_depth_diff, template_node_balance, user_created_node_num, ai_support_num, duplicate_node