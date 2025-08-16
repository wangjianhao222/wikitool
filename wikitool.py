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
current_theme = "light"

def toggle_theme():
    """Toggle between light and dark theme"""
    global current_theme
    if current_theme == "light":
        current_theme = "dark"
        apply_dark_theme()
    else:
        current_theme = "light"
        apply_light_theme()

def apply_dark_theme():
    """Apply dark theme to the application"""
    dark_bg = "#2b2b2b"
    dark_fg = "#ffffff"
    dark_entry_bg = "#404040"
    
    root.configure(bg=dark_bg)
    main_frame.configure(bg=dark_bg)
    left_frame.configure(bg=dark_bg)
    right_frame.configure(bg=dark_bg)
    control_frame.configure(bg=dark_bg)
    search_frame.configure(bg=dark_bg)
    
    history_label.configure(bg=dark_bg, fg=dark_fg)
    language_label.configure(bg=dark_bg, fg=dark_fg)
    search_label.configure(bg=dark_bg, fg=dark_fg)
    search_status.configure(bg=dark_bg, fg="#4CAF50")
    
    history_listbox.configure(bg=dark_entry_bg, fg=dark_fg, selectbackground="#555555")
    entry.configure(bg=dark_entry_bg, fg=dark_fg, insertbackground=dark_fg)
    search_entry.configure(bg=dark_entry_bg, fg=dark_fg, insertbackground=dark_fg)
    result_text.configure(bg=dark_entry_bg, fg=dark_fg, insertbackground=dark_fg)

def apply_light_theme():
    """Apply light theme to the application"""
    light_bg = "#f0f0f0"
    light_fg = "#000000"
    light_entry_bg = "#ffffff"
    
    root.configure(bg=light_bg)
    main_frame.configure(bg=light_bg)
    left_frame.configure(bg=light_bg)
    right_frame.configure(bg=light_bg)
    control_frame.configure(bg=light_bg)
    search_frame.configure(bg=light_bg)
    
    history_label.configure(bg=light_bg, fg=light_fg)
    language_label.configure(bg=light_bg, fg=light_fg)
    search_label.configure(bg=light_bg, fg=light_fg)
    search_status.configure(bg=light_bg, fg="blue")
    
    history_listbox.configure(bg=light_entry_bg, fg=light_fg, selectbackground="#0078d4")
    entry.configure(bg=light_entry_bg, fg=light_fg, insertbackground=light_fg)
    search_entry.configure(bg=light_entry_bg, fg=light_fg, insertbackground=light_fg)
    result_text.configure(bg=light_entry_bg, fg=light_fg, insertbackground=light_fg)

def clear_history():
    """Clear search history"""
    global search_history
    if messagebox.askyesno("确认", "确定要清除所有搜索历史吗？"):
        search_history.clear()
        update_history_listbox()

def show_about():
    """Show about dialog"""
    about_text = """维基百科搜索引擎 - 增强版
    
版本: 2.0
作者: Enhanced by AI Assistant

功能特色:
• 多语言Wikipedia搜索
• 搜索历史记录
• 随机文章发现
• 搜索建议
• 页内文本搜索
• 结果导出功能
• 深色/浅色主题切换
• 键盘快捷键支持

快捷键:
• Enter: 搜索/页内搜索
• Ctrl+R: 随机文章
• Ctrl+E: 导出结果
• Ctrl+F: 焦点到页内搜索
• Ctrl+T: 切换主题
• Ctrl+H: 清除历史
• F1: 显示帮助"""
    
    messagebox.showinfo("关于", about_text)

def show_help():
    """Show help dialog"""
    help_text = """使用帮助:

1. 搜索文章:
   - 在搜索框输入关键词
   - 选择语言后点击"搜索"或按Enter
   - 可点击"搜索建议"查看多个匹配结果

2. 搜索历史:
   - 左侧显示最近20次搜索
   - 点击历史记录可快速重新搜索

3. 随机文章:
   - 点击"随机文章"按钮发现新内容

4. 页内搜索:
   - 在"页内搜索"框输入文本
   - 点击"查找"或按Enter高亮显示
   - 点击"清除高亮"取消高亮

5. 导出功能:
   - 点击"导出"按钮保存当前文章到文本文件

6. 主题切换:
   - 使用Ctrl+T切换深色/浅色主题

7. 键盘快捷键:
   - 查看"关于"对话框了解所有快捷键"""
    
    messagebox.showinfo("帮助", help_text)

def on_key_press(event):
    """Handle keyboard shortcuts"""
    if event.state & 0x4:  # Ctrl key pressed
        if event.keysym == 'r':
            search_random_article()
        elif event.keysym == 'e':
            export_results()
        elif event.keysym == 'f':
            search_entry.focus_set()
        elif event.keysym == 't':
            toggle_theme()
        elif event.keysym == 'h':
            clear_history()
    elif event.keysym == 'F1':
        show_help()

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

def get_article_info():
    """Get additional information about current article"""
    if not current_article_content:
        return
    
    word_count = len(current_article_content.split())
    char_count = len(current_article_content)
    lines_count = current_article_content.count('\n') + 1
    
    # Estimate reading time (average 200 words per minute)
    reading_time = max(1, word_count // 200)
    
    info_text = f"""文章统计信息:

字符数: {char_count:,}
单词数: {word_count:,}
行数: {lines_count:,}
预计阅读时间: {reading_time} 分钟"""
    
    messagebox.showinfo("文章信息", info_text)

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
    suggestions_window.grab_set()  # Make it modal
    
    tk.Label(suggestions_window, text="选择一个搜索结果:", font=("Arial", 12)).pack(pady=10)
    
    suggestions_listbox = tk.Listbox(suggestions_window, font=("Arial", 10))
    suggestions_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
    for suggestion in suggestions:
        suggestions_listbox.insert(tk.END, suggestion)
    
    # Select first item by default
    if suggestions:
        suggestions_listbox.selection_set(0)
    
    button_frame = tk.Frame(suggestions_window)
    button_frame.pack(pady=10)
    
    def on_suggestion_select():
        selection = suggestions_listbox.curselection()
        if selection:
            selected_title = suggestions[selection[0]]
            entry.delete(0, tk.END)
            entry.insert(0, selected_title)
            suggestions_window.destroy()
            search_wikipedia()
    
    def on_double_click(event):
        on_suggestion_select()
    
    suggestions_listbox.bind('<Double-Button-1>', on_double_click)
    suggestions_listbox.bind('<Return>', lambda e: on_suggestion_select())
    
    tk.Button(button_frame, text="选择", command=on_suggestion_select, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="取消", command=suggestions_window.destroy, bg="#f44336", fg="white").pack(side=tk.LEFT, padx=5)
    
    # Focus on listbox and bind keys
    suggestions_listbox.focus_set()

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
            # Add metadata to export
            query = entry.get()
            language = language_var.get()
            
            export_content = f"""维基百科搜索结果
{"="*50}
搜索词: {query}
语言: {language}
导出时间: {tk.StringVar().get()}

{"="*50}

{current_article_content}
"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(export_content)
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
        # Scroll to first match
        first_match = result_text.search(search_term, 1.0, tk.END, nocase=True)
        if first_match:
            result_text.see(first_match)
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
root.title("维基百科搜索引擎 - 增强版 v2.0")
root.geometry("1200x800")
root.minsize(800, 600)

# Bind keyboard shortcuts
root.bind('<Key>', on_key_press)
root.focus_set()

# 创建菜单栏
menubar = tk.Menu(root)
root.config(menu=menubar)

# 文件菜单
file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="文件", menu=file_menu)
file_menu.add_command(label="导出结果 (Ctrl+E)", command=export_results)
file_menu.add_separator()
file_menu.add_command(label="退出", command=root.quit)

# 工具菜单
tools_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="工具", menu=tools_menu)
tools_menu.add_command(label="随机文章 (Ctrl+R)", command=search_random_article)
tools_menu.add_command(label="文章信息", command=get_article_info)
tools_menu.add_command(label="清除历史 (Ctrl+H)", command=clear_history)
tools_menu.add_separator()
tools_menu.add_command(label="切换主题 (Ctrl+T)", command=toggle_theme)

# 帮助菜单
help_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="帮助", menu=help_menu)
help_menu.add_command(label="使用帮助 (F1)", command=show_help)
help_menu.add_command(label="关于", command=show_about)

# 创建主框架
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# 左侧框架（搜索历史）
left_frame = tk.Frame(main_frame, width=250)
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
left_frame.pack_propagate(False)

# 右侧框架（主要内容）
right_frame = tk.Frame(main_frame)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 搜索历史部分
history_header = tk.Frame(left_frame)
history_header.pack(fill=tk.X, pady=(0, 5))

history_label = tk.Label(history_header, text="搜索历史", font=("Arial", 12, "bold"))
history_label.pack(side=tk.LEFT)

clear_history_btn = tk.Button(history_header, text="清除", command=clear_history, 
                             bg="#f44336", fg="white", font=("Arial", 8))
clear_history_btn.pack(side=tk.RIGHT)

history_listbox = tk.Listbox(left_frame, font=("Arial", 9))
history_listbox.pack(fill=tk.BOTH, expand=True)
history_listbox.bind('<<ListboxSelect>>', on_history_select)

# 控制按钮框架
control_frame = tk.Frame(right_frame)
control_frame.pack(fill=tk.X, pady=(0, 10))

# 语言选择
language_label = tk.Label(control_frame, text="语言:", font=("Arial", 10))
language_label.pack(side=tk.LEFT, padx=(0, 5))

languages = ["en", "zh", "fr", "de", "es", "ja", "ru", "it", "pt", "ar", "ko", "hi"]  # 更多语言
language_var = tk.StringVar(root)
language_var.set("en")  # 默认选择英文
language_menu = ttk.Combobox(control_frame, textvariable=language_var, values=languages, width=8, state="readonly")
language_menu.pack(side=tk.LEFT, padx=(0, 10))

# 搜索输入框
search_label = tk.Label(control_frame, text="搜索:", font=("Arial", 10))
search_label.pack(side=tk.LEFT, padx=(0, 5))

entry = tk.Entry(control_frame, width=30, font=("Arial", 10))
entry.pack(side=tk.LEFT, padx=(0, 5))

# 绑定回车键到搜索
entry.bind('<Return>', lambda event: search_suggestions())

# 搜索按钮
search_button = tk.Button(control_frame, text="🔍 搜索", command=search_suggestions, 
                         bg="#4CAF50", fg="white", font=("Arial", 9, "bold"))
search_button.pack(side=tk.LEFT, padx=(0, 5))

# 建议按钮
suggest_button = tk.Button(control_frame, text="💡 建议", command=search_suggestions, 
                          bg="#2196F3", fg="white", font=("Arial", 9))
suggest_button.pack(side=tk.LEFT, padx=(0, 5))

# 随机文章按钮
random_button = tk.Button(control_frame, text="🎲 随机", command=search_random_article, 
                         bg="#9C27B0", fg="white", font=("Arial", 9))
random_button.pack(side=tk.LEFT, padx=(0, 5))

# 第二行控制按钮
control_frame2 = tk.Frame(right_frame)
control_frame2.pack(fill=tk.X, pady=(0, 10))

# 导出按钮
export_button = tk.Button(control_frame2, text="💾 导出", command=export_results, 
                         bg="#FF9800", fg="white", font=("Arial", 9))
export_button.pack(side=tk.LEFT, padx=(0, 5))

# 文章信息按钮
info_button = tk.Button(control_frame2, text="📊 信息", command=get_article_info, 
                       bg="#607D8B", fg="white", font=("Arial", 9))
info_button.pack(side=tk.LEFT, padx=(0, 5))

# 主题切换按钮
theme_button = tk.Button(control_frame2, text="🌙 主题", command=toggle_theme, 
                        bg="#795548", fg="white", font=("Arial", 9))
theme_button.pack(side=tk.LEFT, padx=(0, 5))

# 帮助按钮
help_button = tk.Button(control_frame2, text="❓ 帮助", command=show_help, 
                       bg="#009688", fg="white", font=("Arial", 9))
help_button.pack(side=tk.LEFT)

# 页内搜索框架
search_frame = tk.Frame(right_frame, relief=tk.RIDGE, bd=1)
search_frame.pack(fill=tk.X, pady=(0, 10), padx=2)

search_title = tk.Label(search_frame, text="📝 页内搜索", font=("Arial", 10, "bold"))
search_title.pack(side=tk.LEFT, padx=(5, 10))

search_entry = tk.Entry(search_frame, width=20, font=("Arial", 10))
search_entry.pack(side=tk.LEFT, padx=(0, 5))

search_in_button = tk.Button(search_frame, text="🔍 查找", command=search_in_results, 
                            bg="#E91E63", fg="white", font=("Arial", 8))
search_in_button.pack(side=tk.LEFT, padx=(0, 5))

clear_search_button = tk.Button(search_frame, text="🧹 清除", command=clear_search_highlights, 
                               bg="#757575", fg="white", font=("Arial", 8))
clear_search_button.pack(side=tk.LEFT, padx=(0, 5))

search_status = tk.Label(search_frame, text="", fg="blue", font=("Arial", 9))
search_status.pack(side=tk.LEFT, padx=(10, 5))

# 绑定回车键到页内搜索
search_entry.bind('<Return>', lambda event: search_in_results())

# 创建结果显示区域
result_frame = tk.Frame(right_frame, relief=tk.SUNKEN, bd=1)
result_frame.pack(fill=tk.BOTH, expand=True)

result_text = scrolledtext.ScrolledText(result_frame, width=70, height=25, 
                                       font=("Arial", 10), wrap=tk.WORD,
                                       state=tk.NORMAL)
result_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

# 状态栏
status_frame = tk.Frame(root, relief=tk.SUNKEN, bd=1)
status_frame.pack(side=tk.BOTTOM, fill=tk.X)

status_label = tk.Label(status_frame, text="就绪 - 使用F1查看帮助", font=("Arial", 9))
status_label.pack(side=tk.LEFT, padx=5, pady=2)

version_label = tk.Label(status_frame, text="v2.0", font=("Arial", 9), fg="gray")
version_label.pack(side=tk.RIGHT, padx=5, pady=2)

# 应用默认主题
apply_light_theme()

# 设置初始焦点
entry.focus_set()

# 运行主循环
root.mainloop()
    
