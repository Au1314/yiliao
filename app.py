import json
from flask import Flask,request,jsonify,Response,stream_with_context
from flask_cors import CORS
from utils.getAllData import *
from machine.tree import predict as predict_disease
from agent.nl2sql import answer_question, stream_answer
from agent.format import process_result

app = Flask(__name__)
# 添加CORS支持，允许前端跨域访问
CORS(app)

from utils.getPublicData import *
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

# 添加/api/home路由以匹配前端axios配置
@app.route('/api/home',methods=['GET','POST'])
def api_home():
    return getHomeData()

@app.route('/getHomeData',methods=['GET','POST'])
def getHomeData():
    pieData = getPieData()
    configOne,wordData = getConfigOne()
    casesData = list(getAllCasesData())
    maxNum,maxType,maxDep,maxHos,maxAge,minAge = getFoundData()
    boyList,girlList,ratioData = getGenderData()
    circleData=getCircleData()
    xData,y1Data,y2Data = getBodyData()
    illDurationData = getIllDurationData()
    allergyData = getAllergyData()
    return jsonify({
        'message':'success',
        'code':200,
        'data':{
            'pieData':pieData,
            'configOne':configOne,
            'casesData':casesData,
            'maxNum':maxNum,
            'maxType': maxType,
            'maxDep': maxDep,
            'maxHos': maxHos,
            'maxAge': maxAge,
            'minAge': minAge,
            'boyList':boyList,
            'girlList':girlList,
            'ratioData':ratioData,
            'circleData':circleData,
            'wordData':wordData,
            'illDurationData':illDurationData,
            'allergyData':allergyData,
            'lastData':{
                'xData':xData,
                'y1Data':y1Data,
                'y2Data':y2Data
            }
        }
    })

@app.route('/api/submit',methods=['GET','POST'])
def api_submit():
    content = (request.get_json(silent=True) or {}).get('content') or request.values.get('content') or ''
    if not content:
        return jsonify({'message': 'content 不能为空', 'status': 400})
    try:
        result = predict_disease(content)
    except Exception as e:
        return jsonify({'message': f'预测失败: {e}', 'status': 500})
    return jsonify({'message': 'success', 'status': 200, 'data': {'resultData': result}})

@app.route('/submitModel',methods=['GET','POST'])
def submitModel():
    content = (request.get_json(silent=True) or {}).get('content') or request.values.get('content') or ''
    if not content:
        return jsonify({'message': 'content 不能为空', 'code': 400, 'data': {'resultData': ''}})
    try:
        result = predict_disease(content)
    except Exception as e:
        return jsonify({'message': f'预测失败: {e}', 'code': 500, 'data': {'resultData': ''}})
    return jsonify({'message': 'success', 'code': 200, 'data': {'resultData': result}})

# 添加/api/table路由
@app.route('/api/table',methods=['GET','POST'])
def api_table():
    return tableData()

@app.route('/tableData',methods=['GET','POST'])
def tableData():
    tableDataList = getAllCasesData()
    resultData = [x[1:] for x in tableDataList]
    # print(resultData)
    return jsonify({
        'message':'success',
        'code':200,
        'data':{
            'resultData':resultData
        }
    })

@app.route('/api/chat',methods=['GET','POST'])
@app.route('/chat',methods=['GET','POST'])
def api_chat():
    body = request.get_json(silent=True) or {}
    question = body.get('question') or request.values.get('question') or ''
    session_id = body.get('session_id') or request.values.get('session_id') or None
    if not question:
        return jsonify({'message': 'question 不能为空', 'code': 400})
    try:
        result = answer_question(question, session_id)
        processed = process_result(result.get('answer', ''), result.get('data'))
    except Exception as e:
        return jsonify({'message': f'Agent 调用失败: {e}', 'code': 500})
    return jsonify({
        'message': 'success',
        'code': 200,
        'data': {
            'answer': result.get('answer', ''),
            'answer_html': processed.get('answer_html', ''),
            'sql': result.get('sql', ''),
            'data': result.get('data'),
            'chart': processed.get('chart'),
            'summary': processed.get('summary'),
            'prediction': result.get('prediction'),
        },
    })

@app.route('/api/chat/stream',methods=['GET','POST'])
@app.route('/chat/stream',methods=['GET','POST'])
def api_chat_stream():
    body = request.get_json(silent=True) or {}
    question = body.get('question') or request.values.get('question') or ''
    session_id = body.get('session_id') or request.values.get('session_id') or None
    if not question:
        return jsonify({'message': 'question 不能为空', 'code': 400})

    def generate():
        try:
            for event in stream_answer(question, session_id):
                if event.get('type') == 'done':
                    processed = process_result(event.get('answer', ''), event.get('data'))
                    event.update({
                        'answer_html': processed.get('answer_html', ''),
                        'chart': processed.get('chart'),
                        'summary': processed.get('summary'),
                    })
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
