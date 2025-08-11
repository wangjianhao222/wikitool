import tkinter as tk
import requests
from tkinter import scrolledtext, ttk


def search_wikipedia():
    query = entry.get()
    selected_language = language_var.get()
    if query:
        url = f"https://{selected_language}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "exintro": "",
            "explaintext": "",
            "redirects": 1,
            "titles": query
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            pages = data["query"]["pages"]
            for page_id, page in pages.items():
                if "extract" in page:
                    result_text.delete(1.0, tk.END)
                    result_text.insert(tk.END, page["extract"])
                else:
                    result_text.delete(1.0, tk.END)
                    result_text.insert(tk.END, "未找到相关内容。")
        except requests.RequestException as e:
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"请求出错: {e}")


# 创建主窗口
root = tk.Tk()
root.title("维基百科搜索引擎")

# 创建语言选择下拉框
languages = ["en", "zh", "fr", "de", "es"]  # 可以根据需要添加更多语言代码
language_var = tk.StringVar(root)
language_var.set("en")  # 默认选择英文
language_menu = ttk.Combobox(root, textvariable=language_var, values=languages)
language_menu.pack(pady=5)

# 创建输入框
entry = tk.Entry(root, width=50)
entry.pack(pady=10)

# 创建搜索按钮
search_button = tk.Button(root, text="搜索", command=search_wikipedia)
search_button.pack(pady=5)

# 创建结果显示区域
result_text = scrolledtext.ScrolledText(root, width=80, height=20)
result_text.pack(pady=10)

# 运行主循环
root.mainloop()
    
