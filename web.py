from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    # 读取 CSV 文件
    df = pd.read_csv('rank.csv')

    # 处理数据，去掉 Image 列的后缀
    df['Food Name'] = df['Image'].apply(lambda x: os.path.splitext(x)[0])  # 去掉后缀
    rankings = df[['Rank', 'Food Name', 'Composite Score']].to_dict(orient='records')

    return render_template('index.html', rankings=rankings)

if __name__ == '__main__':
    app.run(debug=True)
