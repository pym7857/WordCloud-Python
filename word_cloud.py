# 워드 클라우드에 필요한 라이브러리
from wordcloud import WordCloud
# 한국어 자연어 처리 라이브러리
from konlpy.tag import Twitter
# 명사 출현 빈도를 세는 라이브러리
from collections import Counter
# 그래프 생성에 필요한 라이브러리
import matplotlib.pyplot as plt
# Flask 웹 서버 구축에 필요한 라이브러리
from flask import Flask, request, jsonify
# CORS를 처리합니다.
from flask_cors import CORS
# 파일에 접근하기 위한 라이브러리
import os

# 플라스크 웹 서버 객체 생성
app = Flask(__name__, static_folder='outputs')  # 정적폴더
CORS(app)

# 폰트 경로 설정
font_path = 'NanumGothic.ttf'

def get_tags(text, max_count, min_length):
    t = Twitter()           # 자연어 처리 라이브러리 호출
    nouns = t.nouns(text)   # 명사만 뽑아옴

    processed = [n for n in nouns if len(n) >= min_length]
    count = Counter(processed)      # 해당 명사 출현 횟수 반환
    result = {}

    for n, c in count.most_common(max_count):
        result[n] = c
    if len(result) == 0:
        result["내용이 없습니다."] = 1
    return result

def make_cloud_image(tags, file_name):
    # 만들고자 하는 워드 클라우드의 기본 설정
    word_cloud = WordCloud(
        font_path=font_path,
        width=800,
        height=800,
        background_color="white"
    )
    word_cloud = word_cloud.generate_from_frequencies(tags)     # 각각의 tags 로 빈도수 설정

    # 이미지 객체 생성
    fig = plt.figure(figsize=(10, 10))
    plt.imshow(word_cloud)
    plt.axis("off")

    # 만들어진 이미지 객체를 파일 형태로 저장
    fig.savefig("outputs/{0}.png".format(file_name))

def process_from_text(text, max_count, min_length, words, file_name):
    tags = get_tags(text, int(max_count), int(min_length))

    # 단어 가중치 적용
    for n, c in words.items():
        if n in tags:   # 그 단어가 tags 안에 있다면
            tags[n] = tags[n] * float(words[n])       # 가중치를 곱해준다

    make_cloud_image(tags, file_name)

@app.route("/process", methods=['GET', 'POST'])
def process():
    content = request.json      # 서버로 부터 받아온 request 데이터가 content 에 담긴다 ★
    words = {}

    # JSON 형식 수정
    if content['words'] is not None:
        for data in content['words'].values():
            words[data['word']] = data['weight']        # 공부: "7"  이런식으로 나올 것이다.

    process_from_text(content['text'], content['maxCount'], content['minLength'], words, content['textID'])

    result = {'result': True}

    return jsonify(result)

@app.route('/outputs', methods=['GET', 'POST'])
def output():
    text_id = request.args.get('textID')            # 서버로 부터 받아온 textID
    return app.send_static_file(text_id + '.png')   # 정적폴더에 저장

@app.route('/validate', methods=['GET', 'POST'])
def validate():
    text_id = request.args.get('textID')            # # 서버로 부터 받아온 textID
    path = "outputs/{0}.png".format(text_id)
    result = {}
    # 해당 이미지 파일이 존재하는지 확인
    if os.path.isfile(path):
        result['result'] = True
    else:
        result['result'] = False
    return jsonify(result)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, threaded=True)   # 0.0.0.0 : localhost