from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox
import pandas as pd
import os
import shutil

class FoodRankingApp(QWidget):
    def __init__(self):
        super().__init__()

        # 创建 food_picture 文件夹（如果不存在）
        if not os.path.exists('food_picture'):
            os.makedirs('food_picture')

        # 界面布局
        self.layout = QVBoxLayout()

        # 图像选择
        self.image_label = QLabel("选择图像:")
        self.layout.addWidget(self.image_label)
        self.image_input = QLineEdit()
        self.layout.addWidget(self.image_input)

        self.browse_button = QPushButton("浏览")
        self.browse_button.clicked.connect(self.browse_image)
        self.layout.addWidget(self.browse_button)

        # 其他输入框
        self.taste_input = QLineEdit()
        self.taste_input.setPlaceholderText("味道评分 (0-10)")
        self.layout.addWidget(self.taste_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("价格评分 (0-10)")
        self.layout.addWidget(self.price_input)

        self.speed_input = QLineEdit()
        self.speed_input.setPlaceholderText("出餐速度评分 (0-10)")
        self.layout.addWidget(self.speed_input)

        self.remark_input = QLineEdit()
        self.remark_input.setPlaceholderText("备注（用于重命名图像）")
        self.layout.addWidget(self.remark_input)

        # 提交按钮
        self.submit_button = QPushButton("提交")
        self.submit_button.clicked.connect(self.submit_data)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)
        self.setWindowTitle("武汉纺织大学美食榜")
        self.show()

    def browse_image(self):
        # 打开文件对话框选择图像
        file_name, _ = QFileDialog.getOpenFileName(self, "选择图像文件", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_name:
            self.image_input.setText(file_name)

    def validate_score(self, score):
        """ 验证评分是否在0到10之间 """
        try:
            score = float(score)
            if 0 <= score <= 10:
                return True
            else:
                return False
        except ValueError:
            return False

    def submit_data(self):
        # 获取输入数据
        image = self.image_input.text()
        taste = self.taste_input.text()
        price = self.price_input.text()
        speed = self.speed_input.text()
        remark = self.remark_input.text()

        # 验证评分
        if not (self.validate_score(taste) and self.validate_score(price) and self.validate_score(speed)):
            QMessageBox.warning(self, "输入错误", "评分必须在 0 到 10 之间。")
            return

        # 转换评分为 float
        taste = float(taste)
        price = float(price)
        speed = float(speed)

        # 存储数据到 data.csv（只包含 Image, Taste, Price, Speed）
        data = {
            'Image': image,
            'Taste': taste,
            'Price': price,
            'Speed': speed
        }

        # 创建 DataFrame
        df = pd.DataFrame([data])

        # 写入 CSV 文件
        df.to_csv('data.csv', mode='a', header=not pd.io.common.file_exists('data.csv'), index=False)

        # 清空输入框
        self.image_input.clear()
        self.taste_input.clear()
        self.price_input.clear()
        self.speed_input.clear()
        self.remark_input.clear()

        # 自动排名
        self.generate_rank(image, remark)

    def generate_rank(self, image, remark):
        # 读取 data.csv
        df = pd.read_csv('data.csv')

        # 计算综合评分
        df['Composite Score'] = 0.4 * df['Taste'] + 0.3 * df['Price'] + 0.3 * df['Speed']

        # 排名
        ranked_df = df.sort_values(by='Composite Score', ascending=False)
        ranked_df['Rank'] = range(1, len(ranked_df) + 1)

        # 保存排名到 rank.csv（只包含 Image, Composite Score, Rank）
        ranked_df[['Image', 'Composite Score', 'Rank']].to_csv('rank.csv', index=False)

        # 处理图片重命名
        self.rename_image(image, remark)

        # 提示用户
        print("排名已生成并保存至 rank.csv")

    def rename_image(self, original_image, remark):
        # 获取文件扩展名
        _, ext = os.path.splitext(original_image)

        # 新文件名
        new_image_name = f"{remark}{ext}" if remark else f"{os.path.basename(original_image)}"
        new_image_path = os.path.join('food_picture', new_image_name)

        # 移动并重命名文件
        shutil.copy(original_image, new_image_path)

        print(f"图片已重命名为: {new_image_name}")

        # 更新 CSV 文件中的图片名称
        self.update_csv_with_image_name(original_image, new_image_name)

    def update_csv_with_image_name(self, original_image, new_image_name):
        # 更新 data.csv
        df = pd.read_csv('data.csv')
        df.loc[df['Image'] == original_image, 'Image'] = new_image_name
        df.to_csv('data.csv', index=False)

        # 更新 rank.csv
        ranked_df = pd.read_csv('rank.csv')
        ranked_df.loc[ranked_df['Image'] == original_image, 'Image'] = new_image_name
        ranked_df.to_csv('rank.csv', index=False)

        print("CSV 文件中的图片名称已更新。")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ex = FoodRankingApp()
    sys.exit(app.exec_())
