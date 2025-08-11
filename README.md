# wikitool
Imported Libraries The script starts by importing the necessary libraries:  tkinter as tk: This is Python's standard GUI (Graphical User Interface) toolkit. It's used to create the windows, buttons, text fields, and other visual elements of the application.  requests: This library is used for making HTTP requests to external web services, 
search_wikipedia() Function
This is the core logic of the application. It's called when the "Search" button is clicked.

Getting Input:

query = entry.get(): Retrieves the text entered by the user into the search input field.

selected_language = language_var.get(): Gets the language selected by the user from the dropdown menu (e.g., "en", "zh", "fr").

Constructing the API URL:

url = f"https://{selected_language}.wikipedia.org/w/api.php": Dynamically creates the Wikipedia API endpoint URL based on the chosen language. For example, if "en" is selected, the URL will be https://en.wikipedia.org/w/api.php.

Setting API Parameters:

params = {...}: Defines a dictionary of parameters for the Wikipedia API request. These parameters tell the API what kind of data to return:

"action": "query": Specifies that the request is for querying information.

"format": "json": Requests the response in JSON format.

"prop": "extracts": Asks for the extracted plain text of the page.

"exintro": "": Limits the extract to the introductory section of the page.

"explaintext": "": Returns the extract as plain text, stripping out Wiki markup.

"redirects": 1: Resolves redirects (e.g., if you search for "NYC", it will redirect to "New York City").

"titles": query: The search term provided by the user.

Making the API Request:

try...except requests.RequestException as e:: This block handles potential errors during the web request, such as network issues or invalid URLs.

response = requests.get(url, params=params): Sends an HTTP GET request to the Wikipedia API with the defined URL and parameters.

response.raise_for_status(): Checks if the request was successful (status code 200). If not, it raises an HTTPError.

data = response.json(): Parses the JSON response from the API into a Python dictionary.

Processing the Response:

pages = data["query"]["pages"]: Navigates through the JSON structure to get the "pages" object, which contains the search results.

for page_id, page in pages.items():: Iterates through the pages returned by the API (usually just one relevant page for a direct search).

if "extract" in page:: Checks if an "extract" (the article content) is present for the page.

result_text.delete(1.0, tk.END): Clears any previous text in the result_text display area.

result_text.insert(tk.END, page["extract"]): Inserts the retrieved Wikipedia article extract into the display area.

else:: If no extract is found for the page.

result_text.delete(1.0, tk.END): Clears the display.

result_text.insert(tk.END, "未找到相关内容。"): Displays a message indicating that no content was found (this message is in Chinese).

Error Handling:

except requests.RequestException as e:: If an error occurs during the API request (e.g., no internet connection), it catches the exception.

result_text.delete(1.0, tk.END): Clears the display.

result_text.insert(tk.END, f"请求出错: {e}"): Displays an error message to the user (in Chinese, showing the specific error).

GUI Setup (Main Window)
This section sets up the main window and its widgets.

root = tk.Tk(): Creates the main window of the application.

root.title("维基百科搜索引擎"): Sets the title of the window to "Wikipedia Search Engine" (in Chinese).

Language Selection Dropdown
languages = ["en", "zh", "fr", "de", "es"]: Defines a list of supported language codes.

language_var = tk.StringVar(root): Creates a Tkinter variable to hold the currently selected language.

language_var.set("en"): Sets the default selected language to English.

language_menu = ttk.Combobox(root, textvariable=language_var, values=languages): Creates a dropdown (combobox) widget linked to language_var and populated with the languages list.

language_menu.pack(pady=5): Places the dropdown widget in the window, with some vertical padding.

Input Field
entry = tk.Entry(root, width=50): Creates a single-line text input field where the user types their search query.

entry.pack(pady=10): Places the input field, with vertical padding.

Search Button
search_button = tk.Button(root, text="搜索", command=search_wikipedia): Creates a button with the text "Search" (in Chinese). When this button is clicked, it executes the search_wikipedia function.

search_button.pack(pady=5): Places the button, with vertical padding.

Result Display Area
result_text = scrolledtext.ScrolledText(root, width=80, height=20): Creates a multi-line text area with a scrollbar to display the Wikipedia search results. It's set to a width of 80 characters and a height of 20 lines.

result_text.pack(pady=10): Places the text area, with vertical padding.

Running the Application
root.mainloop(): Starts the Tkinter event loop. This line keeps the application window open and responsive to user interactions (like button clicks and typing) until the window is closed.

In summary, wikitool.py is a user-friendly, self-contained desktop application that allows users to search Wikipedia articles in multiple languages directly from their computer, providing a simple interface for quick information retrieval.
