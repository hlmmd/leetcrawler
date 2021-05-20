import json

with open('output.json') as f:
    problems = json.load(f)
    datas = []
    for id,problem in problems.items():
        if problem['dislikes'] ==0:
            problem['dislikes'] = 1
        # likeRatio = problem['likes']/ (problem['likes'] + problem['dislikes'])
        likeRatio = problem['likes']/ ( problem['dislikes'])
        data = {}
        data['id'] = id
        data['titleSlug']= problem['titleSlug']
        data['likeRatio'] = likeRatio
        data['acceptRatio'] = problem['acceptRatio']
        data['difficulty'] = problem['difficulty']
        data['title'] = problem['title']

        datas.append(data)

    datas = sorted(datas,reverse= True,key = lambda data:data['acceptRatio'])

    steps = [10 * i for i in range(1,11)]
    ratios = {}
    for step in steps:
        count = 0
        for data in datas:
            count = count +1
            if  count  >= len(datas) * step / 100:
                # print( "{}%".format(step), data['acceptRatio'])
                ratios[step] = data['acceptRatio']
                break
    newdatas = []
    for data in datas:
        if data['difficulty'] == 'Easy' and data['acceptRatio'] > ratios[50]:
            continue
        # if data['acceptRatio'] > 0.5824890307140008 or data['acceptRatio'] < 0.4303226863502119:
        #    continue
        if data['likeRatio'] < 20:
            continue
        newdatas.append(data)
    newdatas = sorted(newdatas,reverse=True,key= lambda data:data['likeRatio'])
    for n in newdatas:
        mstr = '[{} {}. {}](https://leetcode.com/problems/{})\n'.format(n['id'],n['difficulty'],n['title'],n['titleSlug'])
        print(mstr)

