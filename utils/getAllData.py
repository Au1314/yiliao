import re

from utils.getPublicData import getAllCasesData


def getPieData():
    casesList = getAllCasesData()
    ageDic = {'0-10岁':0,'10-20岁':0,'20-30岁':0,'30-40岁':0,'40-50岁':0,'50-60岁':0,'60岁以上':0}
    for caseItem in casesList:
        if int(caseItem[3]) < 10:
            ageDic['0-10岁'] += 1
        elif int(caseItem[3]) < 20:
            ageDic['10-20岁'] += 1
        elif int(caseItem[3]) < 30:
            ageDic['20-30岁'] += 1
        elif int(caseItem[3]) < 40:
            ageDic['30-40岁'] += 1
        elif int(caseItem[3]) < 50:
            ageDic['40-50岁'] += 1
        elif int(caseItem[3]) < 60:
            ageDic['50-60岁'] += 1
        else:
            ageDic['60岁以上'] += 1
    # print(ageDic)
    listResult = []
    for k,v in ageDic.items():
        listResult.append({
            'name':k,
            'value':v
        })
    print(listResult)
    return listResult

def getConfigOne():
    casesList = getAllCasesData()
    caseDic = {}
    for caseItem in casesList:
        if caseDic.get(caseItem[1],-1) == -1:
            caseDic[caseItem[1]] = 1
        else:
            caseDic[caseItem[1]] += 1
    listResult = []
    for k,v in caseDic.items():
        listResult.append({
            'name':k,
            'value':v
        })
    print(1,listResult)
    return listResult[:6],listResult

def getFoundData():
    casesList = getAllCasesData()
    maxNum = len(list(casesList))
    typeDic = {}
    depDic = {}
    hosDic = {}
    maxAge = 0
    minAge = 100
    for caseItem in casesList:
        #类型
        if typeDic.get(caseItem[1],-1) == -1:
            typeDic[caseItem[1]] = 1
        else:
            typeDic[caseItem[1]] += 1
        #科室
        if depDic.get(caseItem[8],-1) == -1:
            depDic[caseItem[8]] = 1
        else:
            depDic[caseItem[8]] += 1
        #医院
        if hosDic.get(caseItem[7],-1) == -1:
            hosDic[caseItem[7]] = 1
        else:
            hosDic[caseItem[7]] += 1
        #年龄
        if int(caseItem[3]) > maxAge:
            maxAge = int(caseItem[3])
        if int(caseItem[3]) < minAge:
            minAge = int(caseItem[3])

    typeSort = sorted(typeDic.items(),key=lambda data:data[1],reverse=True)
    depSort = sorted(depDic.items(), key=lambda data: data[1], reverse=True)
    hosSort = sorted(hosDic.items(), key=lambda data: data[1], reverse=True)
    maxType = typeSort[0][0]
    maxDep = depSort[0][0]
    maxHos = hosSort[0][0]
    return maxNum,maxType,maxDep,maxHos,maxAge,minAge

def getGenderData():
    casesList = getAllCasesData()
    boyDic = {}
    girlDic = {}
    boyNum = 0
    girlNum = 0
    for caseItem in casesList:
        if caseItem[2] == '男':
            boyNum += 1
            if boyDic.get(caseItem[1],-1) == -1:
                boyDic[caseItem[1]] = 1
            else:
                boyDic[caseItem[1]] += 1
        elif caseItem[2] == '女':
            girlNum += 1
            if girlDic.get(caseItem[1],-1) == -1:
                girlDic[caseItem[1]] = 1
            else:
                girlDic[caseItem[1]] += 1

    ratioData = []
    boyRatio = int(round(boyNum / len(casesList) * 100,0))
    girlRatio = int(round(girlNum / len(casesList) * 100,0))
    print(boyRatio, girlRatio)
    ratioData.append(girlRatio)
    ratioData.append(boyRatio)
    boyList = []
    girlList = []
    for k,v in boyDic.items():
        boyList.append({
            'name':k,
            'value':v
        })
    for k,v in girlDic.items():
        girlList.append({
            'name':k,
            'value':v
        })
    return boyList,girlList,ratioData

def getCircleData():
    casesList = getAllCasesData()
    depDic = {}
    for caseItem in casesList:
        if depDic.get(caseItem[8],-1) == -1:
            depDic[caseItem[8]] = 1
        else:
            depDic[caseItem[8]] += 1
    # print(depDic)
    dataSort = sorted(depDic.items(),key=lambda data:data[1],reverse=True)
    dataResultList = []
    for i in dataSort:
        dataResultList.append({
            'name':i[0],
            'value':i[1]
        })

    return dataResultList

def _to_num(value):
    """把身高/体重字段安全转成数字，'无'、空串、非数字统一返回 None。"""
    if value is None:
        return None
    s = str(value).strip()
    if s == '' or s == '无':
        return None
    try:
        return float(s)
    except ValueError:
        return None


def getBodyData():
    casesList = getAllCasesData()
    dataDic = {}
    for caseItem in casesList:
        dataDic[caseItem[1]] = dataDic.get(caseItem[1], 0) + 1
    dataSort = sorted(dataDic.items(), key=lambda data: data[1], reverse=True)
    xData = [i[0] for i in dataSort]

    # 分别累加身高、体重，并记录各自的有效条数（跳过 '无'/非数字）
    heightSum = [0.0 for _ in xData]
    weightSum = [0.0 for _ in xData]
    heightCnt = [0 for _ in xData]
    weightCnt = [0 for _ in xData]
    for caseItem in casesList:
        if caseItem[1] not in xData:
            continue
        index = xData.index(caseItem[1])
        h = _to_num(caseItem[10])
        w = _to_num(caseItem[11])
        if h is not None:
            heightSum[index] += h
            heightCnt[index] += 1
        if w is not None:
            weightSum[index] += w
            weightCnt[index] += 1

    y1Data = [round(heightSum[i] / heightCnt[i], 0) if heightCnt[i] else 0
              for i in range(len(xData))]
    y2Data = [round(weightSum[i] / weightCnt[i], 0) if weightCnt[i] else 0
              for i in range(len(xData))]
    return xData, y1Data, y2Data


def _classify_duration(v):
    """把患病时长归并为统一档位，脏数据（纯数字等）返回 None 丢弃。"""
    v = str(v).strip()
    if v == '' or v == '无':
        return '无'
    if '半年' in v:
        return '大于半年' if '大于' in v else '半年内'
    if '大于' in v or '年' in v:
        return '大于半年'
    if '月' in v:
        return '一月内'
    if any(k in v for k in ('周', '天', '日', '小时')):
        return '一周内'
    return None


def getIllDurationData():
    casesList = getAllCasesData()
    order = ['一周内', '一月内', '半年内', '大于半年', '无']
    durDic = {k: 0 for k in order}
    for caseItem in casesList:
        c = _classify_duration(caseItem[12])
        if c in durDic:
            durDic[c] += 1
    return [{'name': k, 'value': durDic[k]} for k in order]


def getAllergyData():
    casesList = getAllCasesData()
    dic = {}
    for caseItem in casesList:
        v = str(caseItem[13]).strip()
        if v in ('', '无', '暂无信息', '否认', '忘记了'):
            key = '无过敏史'
        elif '青霉素' in v and '头孢' in v:
            key = '青霉素+头孢类'
        elif '青霉素' in v:
            key = '青霉素类'
        elif '头孢' in v:
            key = '头孢类'
        else:
            key = '其他'
        dic[key] = dic.get(key, 0) + 1
    result = [{'name': k, 'value': dic[k]}
              for k, _ in sorted(dic.items(), key=lambda x: x[1], reverse=True)]
    return result
