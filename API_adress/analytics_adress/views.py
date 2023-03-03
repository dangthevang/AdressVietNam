from django.http import HttpResponse
from django.shortcuts import render
import json
import time
import heapq
from .__init__ import *

def getAPI(request):
    input_string = ""
    bad_request = json.dumps({'Label': 'Bad Request'})
    if 'query' in request.GET:
        input_string = request.GET['query']
        result = render_(input_string,data_co_dau,dict_co_dau,True,dict_index_co_dau)
        Response = json.dumps(result, ensure_ascii=False).encode('utf8')
        return HttpResponse(Response, content_type='application/json', status=200)
    else:
        return HttpResponse(bad_request, content_type='application/json', status=400)

def view(request):
    html  = '''<form action="adress" method="get">
                <label for="query">Text: </label>
                <input id="query" type="text" name="query" style="width:50%">
                <input type="submit" value="OK">
            </form>'''
    return HttpResponse(html)

def findPhoneNumber(sentence):
    m = re.search('0[35789][0-9]{8}', sentence)
    if m is not None:
        return str(m.group())
    else:
        return None

def step_phone(x):
    phone = findPhoneNumber(x)
    if phone != None:
        return x.replace(phone,""),phone
    return x,phone
def caculator(x,dict_):
    s = 1
    list_text = x.copy()
    list_text.sort()
    for i in list_text:
        try:
            if i != '':
                s  = s*dict_[i.capitalize()]
        except:
            pass
    return s
def replace_null(x):
    x = x.split(" ")
    for i in x:
        if i!="":
            yield i
            
def checkEncoding(s,dict_):
    normalize_key = ["NFC","NFKC","NFD","NFKD"]
    for key in normalize_key :
        try:
            word = ud.normalize(key,s).capitalize()
            dict_[word]
            return word
        except:
            pass
    return s

def checkSpecifixSymtax(s,dict_):
    arr = list(dict_alias.keys())
    for i in arr:
        if s.upper().find(i) != -1:
            return i
    return checkEncoding(s,dict_)

def format_number_adress(address_string,list_key):
    sentence = address_string.lower()
    for key_ in list_key:
        for symtax in [" ",".",". ",""]:
            word = "".join([key_,symtax,"[1-9]+"])
            m_0 = re.search(word, sentence)
            if symtax == "":
                symtax = "~"
            if m_0 is not None:
                number = re.search( "[1-9]+",str(m_0.group()))
                key_word = f"{list_key[0].capitalize()}_{str(number.group())}"
                return sentence.replace(str(m_0.group()),key_word)
    return sentence

def delete_key(sentence):
    arr = ["tp", "huyện ", "thành phố ", "thị xã ", "quận ", "phường ","tt ", "xã ", "thị trấn ", "tx "," h ",
           "tỉnh "]
    sentence = sentence.lower()
    for i in arr:
        sentence = sentence.replace(i,"")
    return sentence


def split_text(x,dict_):
    arr = []
    x = x.replace("-",' ').replace(",",' ').replace(".",' ').replace("_",' ')
    x = format_number_adress(x,["phường","f","p","phuong"])
    x = format_number_adress(x,["quận","q","quan"])

    x = delete_key(x)
    x = x.split(" ")
    for i in range(len(x)):
        if x[i] != '':
            try:
                x[i] = checkSpecifixSymtax(x[i],dict_)
                dict_[x[i]]
                arr.append(x[i])
            except:
                continue
    return arr

def getIndexRange(text):
    if len(text) <=3:
        return [4,5,6,7]
    elif len(text) <=5:
        return [2,3,4]
    elif len(text) <=10:
        return [1]
    return []

def step_adress(x,data_,dict_,dict_index):
    index,idx_run = 0,0
    amount = len(x)
    result = pd.DataFrame()
    text_result = None
    dict_result = {}
    for cap in range(amount,0,-1):
        idx_run = cap
        while cap - idx_run <=12:
            text = x[idx_run:cap]
            idx_run -= 1
            index_range = getIndexRange(text)
            tich = caculator(text,dict_)
            if dict_index.get(tich) is not None:
                list_index = dict_index[tich]
            else:
                list_index = []
            if len(list_index)>0:
                for j in index_range:
                    filter_index = list(filter_name_adress(text,list_index,dict_,data_,j))
                    if len(filter_index) > 0:
                        CongThuc = 1/len(filter_index) + len(pd.unique(text))**(len(text))
                        for key in filter_index:
                            try:
                                dict_result[key] += CongThuc
                            except:
                                dict_result[key] = CongThuc
    return dict_result

def find_indices(list_to_check, item_to_find):
    return np.array([idx for idx, value in enumerate(list_to_check) if value == item_to_find])

def check_alias(dict_alias,s):
    try:
        dict_alias[s]
        return True
    except:
        return False
def check_name_adress(text,tich,dict_key):
    text = [i.capitalize() for i in text]
    arr = np.zeros(len(text)+1)
    for idx in range(len(text)):
        if tich == 1:
            break
        if tich % dict_key[text[idx]] == 0:
            arr[find_indices(text,text[idx])] = 1
            tich = tich // dict_key[text[idx]]
            if check_alias(dict_alias,text[idx]):
                arr[idx] = 1
                arr[idx+1]= 1
            # Xử lý với ký tự với phường là số
            key = "[0-9]+"
            m_0 = re.search(key, text[idx])
            if m_0 is not None:
                arr[idx+1]= 1
    stack = 0
    for ele in arr:
        if stack == 1 and ele ==1:
            return True
        stack = ele
    return False

def filter_name_adress(text,list_index,dict_,data,number):
    # data = data.iloc[list_index]
    for idx in list_index:
        check = True
        for type_ in dict_relationship[number]:
            tich = data[f"TICH_{type_}"][idx]
            if check_name_adress(text,tich,dict_):
                continue
            else:
                check = False
        if check==True:
            yield idx


def get_adress(x,data_,dict_,dict_index):
    arr = split_text(x,dict_)
    # print(x)
    if len(arr) == 0:
        return pd.DataFrame()," ".join(arr)
    index = 0
    check = False
    dict_result = step_adress(arr,data_,dict_,dict_index)
    # print(dict_result)
    try:
        list_max = heapq.nlargest(2, list(dict_result.values()))
    except ValueError:
        return pd.DataFrame()," ".join(arr)
    arr_idx = []
    for key,value in dict_result.items():
        if value in list_max:
            arr_idx.append(key)
    return data_.iloc[arr_idx]," ".join(arr)

def convert_2(text):
    output = ud.normalize("NFKC",text)
    # for key in normalize_key:
    for regex, replace in patterns.items():
        output = re.sub(regex, replace, output)
        output = re.sub(regex.upper(), replace.upper(), output)
    return output


def last_check(sentence,a):
    sentence = convert_2(sentence.replace("_"," ")).upper()
    a = convert_2(a.replace("_"," ")).upper()
    m_0 = re.search(sentence,a)
    if m_0 is not None:
        return 1
    return 0

def create_key(code,*arg):
    s = ""
    for i in range(len(code)):
        if code[i] == "1":
            s += arg[i]
    return s

def render_(x,data_,dict_,test,dict_index_):
    list_key_result = ["Xã/Phường", "Quận/Huyện","Tỉnh/TP","Số Điện Thoại"]
    dict_result_compoment = {}
    for key in list_key_result:
        dict_result_compoment[key] = None
    list_Result = []
    Address_Special = x
    df,sdt = step_phone(x)
    df,x = get_adress(x,data_,dict_,dict_index_)
    if df.empty and test == True:
        x = convert_2(x)
        return render_(x,data_khong_dau,dict_khong_dau,False,dict_index_khong_dau)
    else:
        # print(x)
        for key,value in dict_alias.items():
            x = x.replace(key,value)
        # x = format_number_adress(x,["phường","f","p","phuong",])
        # x = format_number_adress(x,["quận","q","quan"])
        try:
            df["MatchTP"] = df.apply(lambda row: last_check(row["Tỉnh/TP"],x),axis=1)
            df["MatchQH"] = df.apply(lambda row: last_check(row["Quận/Huyện"],x),axis=1)
            df["MatchPX"] = df.apply(lambda row: last_check(row["Xã/Phường"],x),axis=1)
            df["FinalScore"] = df["MatchTP"]+df["MatchQH"]+df["MatchPX"]
            df["FinalText"] = df.apply(lambda row: "".join([str(row["MatchPX"]),str(row["MatchQH"]),str(row["MatchTP"])]),axis=1)
            max_score_file = df["FinalScore"].max()
            if max_score_file == 0:
                return list_Result
            df_finan_result = df[df["FinalScore"] == max_score_file]
            df_finan_result["Code_"] = df_finan_result.apply(lambda row: create_key(row["FinalText"],row["Xã/Phường"],row["Quận/Huyện"],row["Tỉnh/TP"]),axis=1)
            df_finan_result = df_finan_result.drop_duplicates(subset=['Code_'])
            amount_ = 0
            for idx in df_finan_result.index:
                t = df["FinalText"][idx]
                check = False
                for i in range(3):
                    if t[i] =="1":
                        check = True
                    if check == True:
                        dict_result_compoment[list_key_result[i]] = df_finan_result[list_key_result[i]][idx]
                    else:
                        dict_result_compoment[list_key_result[i]] = None
                dict_result_compoment["Số Điện Thoại"] = sdt
                list_Result.append(dict_result_compoment.copy())
                amount_ +=1
                if amount_ == 3:
                    break
        except:
            return list_Result
        
    return list_Result