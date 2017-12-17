#coding=utf8
import os
import json

import pandas as pd

def getxlsx():
    f_list = [os.path.join('people_json', i) for i in os.listdir('people_json')]
    datas = []
    for f_path in f_list:
        with open(f_path) as f:
            json_data = json.load(f)
            datas.append(json_data)
    df = pd.DataFrame(datas)
    df.to_excel('people.xlsx')

def getjl():
    f_list = [os.path.join('people_json', i) for i in os.listdir('people_json')]
    datas = []
    with open('people.jl', 'w') as f1:
        for f_path in f_list:
            with open(f_path) as f2:
                f1.write(f2.read())


def concat2table():
    df1 = pd.read_excel('people.xlsx')
    df2 = pd.read_excel('people2.xlsx')
    for i,j in zip(df1, df2):
        print(i, j)
        break

def main():
    getjl()



if __name__ == '__main__':
    main()