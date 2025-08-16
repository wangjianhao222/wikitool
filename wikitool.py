import tkinter as tk
import requests
from tkinter import scrolledtext, ttk, messagebox, filedialog
import json
import random
import webbrowser


# Global variables for new features
search_history = []
current_article_content = ""
bookmarks = []

def add_to_history(query, language):
    """Add search query to history"""
    if query and query.strip():
        history_item = f"{query} ({language})"
        if history_item not in search_history:
            search_history.insert(0, history_item)
            if len(search_history) > 20:  # Keep only last 20 searches
                search_history.pop()
            update_history_listbox()

def update_history_listbox():
    """Update the history listbox with current search history"""
    history_listbox.delete(0, tk.END)
    for item in search_history:
        history_listbox.insert(tk.END, item)

def on_history_select(event):
    """Handle selection from search history"""
    selection = history_listbox.curselection()
    if selection:
        history_item = search_history[selection[0]]
        # Extract query and language from history item
        parts = history_item.rsplit(' (', 1)
        if len(parts) == 2:
            query = parts[0]
            language = parts[1].rstrip(')')
            entry.delete(0, tk.END)
            entry.insert(0, query)
            language_var.set(language)

def search_random_article():
    """Get a random Wikipedia article"""
    selected_language = language_var.get()
    url = f"https://{selected_language}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "random",
        "rnnamespace": 0,
        "rnlimit": 1
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "query" in data and "random" in data["query"]:
            random_title = data["query"]["random"][0]["title"]
            entry.delete(0, tk.END)
            entry.insert(0, random_title)
            search_wikipedia()
    except requests.RequestException as e:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"获取随机文章时出错: {e}")

def search_suggestions():
    """Get search suggestions from Wikipedia"""
    query = entry.get()
    selected_language = language_var.get()
    if not query:
        return
    
    url = f"https://{selected_language}.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "format": "json",
        "search": query,
        "limit": 10
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if len(data) >= 2 and data[1]:
            suggestions = data[1]
            show_suggestions_window(suggestions)
        else:
            search_wikipedia()  # If no suggestions, do regular search
    except requests.RequestException as e:
        search_wikipedia()  # Fallback to regular search

def show_suggestions_window(suggestions):
    """Show a window with search suggestions"""
    suggestions_window = tk.Toplevel(root)
    suggestions_window.title("搜索建议")
    suggestions_window.geometry("400x300")
    
    tk.Label(suggestions_window, text="选择一个搜索结果:", font=("Arial", 12)).pack(pady=10)
    
    suggestions_listbox = tk.Listbox(suggestions_window, font=("Arial", 10))
    suggestions_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
    for suggestion in suggestions:
        suggestions_listbox.insert(tk.END, suggestion)
    
    def on_suggestion_select():
        selection = suggestions_listbox.curselection()
        if selection:
            selected_title = suggestions[selection[0]]
            entry.delete(0, tk.END)
            entry.insert(0, selected_title)
            suggestions_window.destroy()
            search_wikipedia()
    
    tk.Button(suggestions_window, text="选择", command=on_suggestion_select).pack(pady=5)
    tk.Button(suggestions_window, text="取消", command=suggestions_window.destroy).pack(pady=5)

def export_results():
    """Export current results to a text file"""
    global current_article_content
    if not current_article_content:
        messagebox.showwarning("警告", "没有内容可导出")
        return
    
    filename = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        title="导出搜索结果"
    )
    if filename:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(current_article_content)
            messagebox.showinfo("成功", f"结果已导出到: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")

def search_in_results():
    """Search for text within current results"""
    search_term = search_entry.get()
    if not search_term or not current_article_content:
        return
    
    # Clear previous highlights
    result_text.tag_remove("highlight", 1.0, tk.END)
    
    # Find and highlight all occurrences
    start_pos = 1.0
    count = 0
    while True:
        pos = result_text.search(search_term, start_pos, tk.END, nocase=True)
        if not pos:
            break
        end_pos = f"{pos}+{len(search_term)}c"
        result_text.tag_add("highlight", pos, end_pos)
        start_pos = end_pos
        count += 1
    
    # Configure highlight tag
    result_text.tag_config("highlight", background="yellow", foreground="black")
    
    if count > 0:
        search_status.config(text=f"找到 {count} 个匹配项")
    else:
        search_status.config(text="未找到匹配项")

def clear_search_highlights():
    """Clear search highlights"""
    result_text.tag_remove("highlight", 1.0, tk.END)
    search_entry.delete(0, tk.END)
    search_status.config(text="")


def search_wikipedia():
    global current_article_content
    query = entry.get()
    selected_language = language_var.get()
    if query:
        # Add to search history
        add_to_history(query, selected_language)
        
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
                    current_article_content = page["extract"]
                    result_text.delete(1.0, tk.END)
                    result_text.insert(tk.END, current_article_content)
                    # Clear any previous search highlights
                    clear_search_highlights()
                else:
                    current_article_content = ""
                    result_text.delete(1.0, tk.END)
                    result_text.insert(tk.END, "未找到相关内容。")
        except requests.RequestException as e:
            current_article_content = ""
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"请求出错: {e}")


# 创建主窗口
root = tk.Tk()
root.title("维基百科搜索引擎 - 增强版")
root.geometry("1000x700")

# 创建主框架
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# 左侧框架（搜索历史）
left_frame = tk.Frame(main_frame, width=200)
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
left_frame.pack_propagate(False)

# 右侧框架（主要内容）
right_frame = tk.Frame(main_frame)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 搜索历史部分
history_label = tk.Label(left_frame, text="搜索历史", font=("Arial", 12, "bold"))
history_label.pack(pady=(0, 5))

history_listbox = tk.Listbox(left_frame, font=("Arial", 9))
history_listbox.pack(fill=tk.BOTH, expand=True)
history_listbox.bind('<<ListboxSelect>>', on_history_select)

# 控制按钮框架
control_frame = tk.Frame(right_frame)
control_frame.pack(fill=tk.X, pady=(0, 10))

# 语言选择
language_label = tk.Label(control_frame, text="语言:")
language_label.pack(side=tk.LEFT, padx=(0, 5))

languages = ["en", "zh", "fr", "de", "es", "ja", "ru", "it", "pt"]  # 添加更多语言
language_var = tk.StringVar(root)
language_var.set("en")  # 默认选择英文
language_menu = ttk.Combobox(control_frame, textvariable=language_var, values=languages, width=8)
language_menu.pack(side=tk.LEFT, padx=(0, 10))

# 搜索输入框
entry = tk.Entry(control_frame, width=40, font=("Arial", 10))
entry.pack(side=tk.LEFT, padx=(0, 5))

# 绑定回车键到搜索
entry.bind('<Return>', lambda event: search_suggestions())

# 搜索按钮
search_button = tk.Button(control_frame, text="搜索", command=search_suggestions, bg="#4CAF50", fg="white")
search_button.pack(side=tk.LEFT, padx=(0, 5))

# 随机文章按钮
random_button = tk.Button(control_frame, text="随机文章", command=search_random_article, bg="#2196F3", fg="white")
random_button.pack(side=tk.LEFT, padx=(0, 5))

# 导出按钮
export_button = tk.Button(control_frame, text="导出", command=export_results, bg="#FF9800", fg="white")
export_button.pack(side=tk.LEFT)

# 页内搜索框架
search_frame = tk.Frame(right_frame)
search_frame.pack(fill=tk.X, pady=(0, 10))

search_label = tk.Label(search_frame, text="页内搜索:")
search_label.pack(side=tk.LEFT, padx=(0, 5))

search_entry = tk.Entry(search_frame, width=20, font=("Arial", 10))
search_entry.pack(side=tk.LEFT, padx=(0, 5))

search_in_button = tk.Button(search_frame, text="查找", command=search_in_results, bg="#9C27B0", fg="white")
search_in_button.pack(side=tk.LEFT, padx=(0, 5))

clear_search_button = tk.Button(search_frame, text="清除高亮", command=clear_search_highlights, bg="#607D8B", fg="white")
clear_search_button.pack(side=tk.LEFT, padx=(0, 5))

search_status = tk.Label(search_frame, text="", fg="blue")
search_status.pack(side=tk.LEFT, padx=(10, 0))

# 绑定回车键到页内搜索
search_entry.bind('<Return>', lambda event: search_in_results())

# 创建结果显示区域
result_text = scrolledtext.ScrolledText(right_frame, width=70, height=25, font=("Arial", 10), wrap=tk.WORD)
result_text.pack(fill=tk.BOTH, expand=True)

# 运行主循环
root.mainloop()
    
