import pymongo
import json




class Global:
    fieldID = 0
    IDmap = {}

def getFieldID():
    Global.fieldID = Global.fieldID + 1
    return Global.fieldID

def getField(question):
    if 'questions' in question:
        return getGroupfield(question)

    field = {
        '_id':question['displayId'],
        'title':question['title'],
        'descpription':'',
        'properties':{
            'allowNotSuitable':False,
            'allowEmpty':False
        },
    }

    if 'descpription' in question:
        field['descpription'] = question['description']

    if question['type'] == 'multiple':
        field['type'] = 'choice'
        field['choices'] = []
        cnt = 0
        for data in question['choices']:
            cnt += 1
            choice = {
                'id': data['id'],
                'description': data['title'],
                'score': None,
                'needInput': 'input' in data,
            }
            field['choices'].append(choice)
        field['isDropdown'] = False
        field['maxCount'] = 1
        field['minCount'] = 1
        if 'min' in question:
            field['minCount'] = int(question['min'])
        if 'max' in question:
            field['maxCount'] = int(question['max'])


    if question['type'] == 'fill':
        field['title'] = question['title']
        if question['contentType'] == 'text':
            field['type'] = 'string'
            field['isMultiLine'] = False
            field['maxLength'] = None
        elif question['contentType'] == 'digit':
            field['type'] = 'number'
            field['fixedPrecision'] = None
            field['minValue'] = int(question['range_min']) if 'range_min' in question else None
            field['maxValue'] = int(question['range_max']) if 'range_max' in question else None

    if question['type'] == 'textarea':
        field['descpription'] = question['title']
        field['type'] = 'string'
        field['isMultiLine'] = True
        field['maxLength'] = None


    return field

def getGroupfield(questions):
    groupfield = {}

    groupfield['_id']=questions['id']
    groupfield['type']='group'
    groupfield['title']=questions['title']
    groupfield['desciption']=''
    groupfield['properties']={
        'allowNotSuitable':False,
        'allowEmpty':False
    }

    groupfield['children'] = [getField(data) for data in questions['questions']]

    return groupfield

def main():
    # MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["questionnaireConv"]
    collection = db["q"]



    path = './data/json/居家问卷'
    modulesName=['newqnnA','newqnnB']

    questionnaire={
        '_id': '',
        'version':'',
        'title':'',
        'description':'',
        'modules':[],
        'creator':''
    }
    for moduleName in modulesName:
        with open(f'{path}/{moduleName}.json', 'r', encoding='utf-8') as file:
            filedata = json.load(file)
        questionnaire['modules'].append(getGroupfield(filedata))

    collection.insert_one(questionnaire)



    # with open('data.json', 'w',encoding='utf-8') as file:
    #     json.dump(getGroupfield(filedata),file,indent=2,ensure_ascii=False)



if __name__ == '__main__':
    main()