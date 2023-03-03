import pandas as pd
import numpy as np
import re
import math
import sympy
import xlrd
import unicodedata as ud
pd.options.mode.chained_assignment = None 

data_base = pd.read_csv(r"ListMain.csv")
data_base = data_base[['Tỉnh Thành Phố','Quận Huyện','Phường Xã']]

def transform_raw(sentence):
    if pd.isna(sentence):
        return sentence
    arr_key_bo = ["Thành Phố ","Thành phố ","Tỉnh ","Huyện ","Thị xã ","Thị trấn ","Xã "]
    for i in arr_key_bo:
        sentence = sentence.replace(i,"",1)
    key = "[0-9]+"
    m_0 = re.search(key, sentence)
    if m_0 is not None:
        key_word = str(int(str(m_0.group())))
        sentence = sentence.replace(str(m_0.group()),key_word).replace(" ","_")
    arr_key_bo = ["Quận ","Phường "]
    for i in arr_key_bo:
        sentence = sentence.replace(i,"")
    return sentence
data_base["Tỉnh/TP"] = data_base["Tỉnh Thành Phố"].apply(lambda row: transform_raw(row))
data_base["Quận/Huyện"] = data_base["Quận Huyện"].apply(lambda row: transform_raw(row))
data_base["Xã/Phường"] = data_base["Phường Xã"].apply(lambda row: transform_raw(row))
key_tinh_tp = pd.unique(pd.Series(data_base["Tỉnh/TP"]))
key_huyen = pd.unique(pd.Series(data_base["Quận/Huyện"]))
key_phuong = pd.unique(pd.Series(data_base["Xã/Phường"]))

def getWord(word):
    if pd.isna(word):
        return word
    b = word.split(" ")
    for i in b:
        yield i.capitalize()

def GetUnique(*arg):
    list_ = []
    for keys in arg:
        for word in keys:
            w = list(getWord(word))
            for i in w:
                list_.append(i)
    return list(set(list_))

Key_UniCon = GetUnique(key_tinh_tp,key_huyen,key_phuong)
list_id_ = list(sympy.primerange(0, 100000))
normalize_key = ["NFC","NFKC","NFD","NFKD"]
dict_co_dau = {}
for i in range(len(Key_UniCon)):
    for key in normalize_key:
        word = ud.normalize(key,Key_UniCon[i])
        if dict_co_dau.get(word) == None:
            try:
                number = str(int(word.split("_")[1]))
                dict_co_dau[word] = float(list_id_[i])
                # dict_co_dau[number] = float(list_id_[i])
                if "Phường" in word:
                    dict_co_dau[f"Phường {number}"] = float(list_id_[i])
                    dict_co_dau[f"Phường{number}"] = float(list_id_[i])
                    dict_co_dau[f"Phường.{number}"] = float(list_id_[i])
                    dict_co_dau[f"P.{number}"] = float(list_id_[i])
                    dict_co_dau[f"P{number}"] = float(list_id_[i])
                    dict_co_dau[f"P_{number}"] = float(list_id_[i])
                    dict_co_dau[f"F{number}"] = float(list_id_[i])
                    dict_co_dau[f"F.{number}"] = float(list_id_[i])
                elif "Quận"in word:
                    dict_co_dau[f"Quận {number}"] = float(list_id_[i])
                    dict_co_dau[f"Quận{number}"] = float(list_id_[i])
                    dict_co_dau[f"Quận.{number}"] = float(list_id_[i])
                    dict_co_dau[f"Q.{number}"] = float(list_id_[i])
                    dict_co_dau[f"Q{number}"] = float(list_id_[i])
            except:
                dict_co_dau[word] = float(list_id_[i])
dict_alias = {
    "Hn": "Hà Nội",
    "Hcm": "Hồ Chí Minh",
    "Dn":"Đà Nẵng",
    "brvt":"Bà Rịa Vũng Tàu"
}
for key, value in dict_alias.items():
    dict_co_dau[key] = 1
    for word in value.split(" "):
        dict_co_dau[key] *= dict_co_dau[word]

patterns = {
    '[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
    '[đ]': 'd',
    '[èéẻẽẹêềếểễệ]': 'e',
    '[ìíỉĩị]': 'i',
    '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
    '[ùúủũụưừứửữự]': 'u',
    '[ỳýỷỹỵ]': 'y'
}
def convert_1(text):
    """
    Convert from 'Tieng Viet co dau' thanh 'Tieng Viet khong dau'
    text: input string to be converted
    Return: string converted
    """
    output = ud.normalize("NFKC",text)
    for regex, replace in patterns.items():
        output = re.sub(regex, replace, output)
        output = re.sub(regex.upper(), replace.upper(), output)
    return output

Key_UniCon = GetUnique(key_tinh_tp,key_huyen,key_phuong)
list_id_ = list(sympy.primerange(0, 100000))
dict_khong_dau = {}
for i in range(len(Key_UniCon)):
    word = convert_1(Key_UniCon[i])
    for key in normalize_key:
        word = ud.normalize(key,word)
        if dict_khong_dau.get(word) == None:
            try:
                number = str(int(word.split("_")[1]))
                dict_khong_dau[word] = float(list_id_[i])
                # dict_khong_dau[number] = float(list_id_[i])
                if "Phuong" in word:
                    dict_khong_dau[f"Phuong {number}"] = float(list_id_[i])
                    dict_khong_dau[f"Phuong{number}"] = float(list_id_[i])
                    dict_khong_dau[f"Phuong. {number}"] = float(list_id_[i])
                    dict_khong_dau[f"P.{number}"] = float(list_id_[i])
                    dict_khong_dau[f"P{number}"] = float(list_id_[i])
                    dict_khong_dau[f"P_{number}"] = float(list_id_[i])
                    dict_khong_dau[f"F{number}"] = float(list_id_[i])
                    dict_khong_dau[f"F.{number}"] = float(list_id_[i])

                elif "Quan" in word:
                    dict_khong_dau[f"Quan {number}"] = float(list_id_[i])
                    dict_khong_dau[f"Quan{number}"] = float(list_id_[i])
                    dict_khong_dau[f"Quan. {number}"] = float(list_id_[i])
                    dict_khong_dau[f"Q.{number}"] = float(list_id_[i])
                    dict_khong_dau[f"Q{number}"] = float(list_id_[i])
            except:
                dict_khong_dau[word] = float(list_id_[i])
for key, value in dict_alias.items():
    dict_khong_dau[key] = 1
    for word in value.split(" "):
        dict_khong_dau[key] *= dict_khong_dau[convert_1(word)]
def ghep(*arg):
    # text = ""
    try:
        text = " ".join(arg)
        # for i in ["Huyện ","Thành ","phố ","Thị ","xã ","Xã ","Quận ","Phường ","trấn ","Tỉnh "]:
        #     text = text.replace(i,"")
        return text
    except TypeError:
        return " "

def caculator_base(x,dict_,co_dau = True):
    s = 1
    x = x.split(" ")
    x.sort()
    for i in x:
        t = i
        if co_dau == False:
            t = convert_1(i)
        if i != "":
            try:
                s = dict_[t.capitalize()]*s
            except:
                pass
    return s

def setup_data(file_data,dict_,co_dau):
    file_data["CODE_1"] = file_data.apply(lambda row: ghep(row["Tỉnh/TP"],row["Quận/Huyện"],row["Xã/Phường"]),axis=1)
    file_data["CODE_2"] = file_data.apply(lambda row: ghep(row["Tỉnh/TP"],row["Quận Huyện"]),axis=1)
    file_data["CODE_3"] = file_data.apply(lambda row: ghep(row["Tỉnh/TP"],row["Xã/Phường"]),axis=1)
    file_data["CODE_4"] = file_data.apply(lambda row: ghep(row["Quận/Huyện"],row["Xã/Phường"]),axis=1)
    file_data["CODE_5"] = file_data.apply(lambda row: ghep(row["Tỉnh/TP"]),axis=1)
    file_data["CODE_6"] = file_data.apply(lambda row: ghep(row["Quận/Huyện"]),axis=1)
    file_data["CODE_7"] = file_data.apply(lambda row: ghep(row["Xã/Phường"]),axis=1)
    file_data["TICH_1"] = file_data["CODE_1"].apply(lambda row: caculator_base(row,dict_,co_dau))
    file_data["TICH_2"] = file_data["CODE_2"].apply(lambda row: caculator_base(row,dict_,co_dau))
    file_data["TICH_3"] = file_data["CODE_3"].apply(lambda row: caculator_base(row,dict_,co_dau))
    file_data["TICH_4"] = file_data["CODE_4"].apply(lambda row: caculator_base(row,dict_,co_dau))
    file_data["TICH_5"] = file_data["CODE_5"].apply(lambda row: caculator_base(row,dict_,co_dau))
    file_data["TICH_6"] = file_data["CODE_6"].apply(lambda row: caculator_base(row,dict_,co_dau))
    file_data["TICH_7"] = file_data["CODE_7"].apply(lambda row: caculator_base(row,dict_,co_dau))
    return file_data
dict_relationship = {
    1:[5,6,7],
    2:[5,6],
    3:[5,7],
    4:[6,7],
    5:[5],
    6:[6],
    7:[7]
}
data_co_dau = setup_data(data_base.copy(),dict_co_dau,True)
data_khong_dau = setup_data(data_base.copy(),dict_khong_dau,False)
def create_arr_key(data_):
    dict_ = {}
    for i in range(1,8):
        field = f"TICH_{i}"
        for i in data_.index:
            try:
                dict_[data_[field][i]].append(i)
            except:
                dict_[data_[field][i]] = [i]
    for key,values in dict_.items():
        dict_[key] =  pd.unique(values)
    return dict_

dict_index_co_dau = create_arr_key(data_co_dau)
dict_index_khong_dau = create_arr_key(data_khong_dau)