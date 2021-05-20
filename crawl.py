import requests
import os
import json
import re
import html2text

root_url = 'https://leetcode.com'
contest_info_api = 'https://leetcode.com/contest/api/info/weekly-contest-'
question_urls = 'https://leetcode.com/graphql'

save_json = True

# create dir
if not os.path.exists('raw_data'):
    os.mkdir('raw_data')

if not os.path.exists('markdown'):
    os.mkdir('markdown')

def get_problems(res_json):
    ret_dict = {}
    probs = res_json['stat_status_pairs']
    for prob in probs:
        # 跳过付费
        if prob['paid_only']:
            continue
        front_id = prob['stat']['frontend_question_id']
        # 访问problem需要的是titleSlug
        ret_dict[front_id] = {}
        ret_dict[front_id]['titleSlug'] = prob['stat']['question__title_slug']
    return ret_dict


def get_problems_raw():
    all_questions_url = 'https://leetcode.com/api/problems/all'
    req = requests.get(url=all_questions_url)
    htmlstr = req.text
    problems_json = json.loads(htmlstr)
    if save_json:
        with open('problems.json', 'w') as f:
            json.dump(problems_json, f, indent=4)
    return problems_json, get_problems(problems_json)


def get_one_problem_detail(res_json):
    prob_dict = {}
    question = res_json['data']['question']
    prob_dict['questionFrontendId'] = question['questionFrontendId']
    prob_dict['title'] = question['title']
    prob_dict['titleSlug'] = question['titleSlug']
    prob_dict['difficulty'] = question['difficulty']

    prob_dict['likes'] = question['likes']
    prob_dict['dislikes'] = question['dislikes']

    prob_dict['similarQuestions'] = []
    similar_json = json.loads(question['similarQuestions'])
    for similar in similar_json:
        prob_dict['similarQuestions'] .append(similar['titleSlug'])

    prob_dict['topicTags'] = []

    for tag in question['topicTags']:
        prob_dict['topicTags'].append(tag['name'])

    stats = json.loads(question['stats'])
    prob_dict['totalAcceptedRaw'] = stats['totalAcceptedRaw']
    prob_dict['totalSubmissionRaw'] = stats['totalSubmissionRaw']
    prob_dict['acceptRatio'] = prob_dict['totalAcceptedRaw'] / \
        prob_dict['totalSubmissionRaw']

    prob_dict['hints'] = question['hints']

    content = question['content']
    content = content.replace('\t', '').replace('\n\n', '\n')
    content = html2text.html2text(content)
    content = content.replace('**Input:**', 'Input:').replace('**Output:**',
                                                            'Output:').replace('**Explanation:**', 'Explanation:')
    prob_dict['content'] = content

    with open('markdown/{}.md'.format(prob_dict['questionFrontendId']), 'w') as f:
        f.write(content)

    return prob_dict


def get_one_problem_raw(question_url):
    if question_url[-1] == '/':
        question_url = question_url[:-1]
    question_str = question_url.split('/')[-1]
    req_json = {"operationName": "questionData", "variables": {"titleSlug": "check-if-the-sentence-is-pangram"},
                "query": "query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n    translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    similarQuestions\n    exampleTestcases\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      __typename\n    }\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n      canSeeDetail\n      paidOnly\n      hasVideoSolution\n      paidOnlyVideo\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    enableTestMode\n    enableDebugger\n    envInfo\n    libraryUrl\n    adminUrl\n    __typename\n  }\n}\n"}

    req_json['variables']['titleSlug'] = question_str
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    res = requests.request("post", question_urls,
                           json=req_json, headers=headers, timeout=60)

    res_json = json.loads(res.text)

    if save_json:
        front_id = res_json['data']['question']['questionFrontendId']
        filename = 'raw_data/{}.json'.format(front_id)
        with open(filename, 'w') as f:
            json.dump(res_json, f, indent=4)

    return res_json


_, prob_dict = get_problems_raw()

output_dict = {}
for front_id, problem_detail in prob_dict.items():
    if os.path.exists('raw_data/{}.json'.format(front_id)):
        with open('raw_data/{}.json'.format(front_id)) as f:
            raw = json.load(f)
        # continue
    else:
        titleSlug = problem_detail['titleSlug']
        question_url = 'https://leetcode.com/problems/' + titleSlug
        raw = get_one_problem_raw(question_url)
    data = get_one_problem_detail(raw)
    output_dict[front_id] = data

with open('output.json', 'w')as f:
    json.dump(output_dict, f, indent=4)

