#!/usr/bin/python3
import sys
import tkinter as tk
from tkinter import scrolledtext, ttk, StringVar
from platform import system
from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyglet
import googletrans

NORMAL_FONT = ("Lato", 14)
BASE_URL = "https://translate.google.com"
ACCEPT_BTN_XPATH = "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div/div/button"
INPUT_XPATH = "/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[3]/c-wiz[1]/span/span/div/textarea"
OUTPUT_XPATH = "/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[3]/c-wiz[2]/div[6]/div/div[1]/span[1]"
TEST = "/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[1]/c-wiz/div[1]/c-wiz/div[2]/div/div[2]/div/div" \
       "/span/button[1]/span[1]/span"


class App(tk.Tk):
    def __init__(self):
        super().__init__(className="Translator")

        # Data
        self.languages = googletrans.LANGUAGES
        self.languages = dict([(value.capitalize(), key) for key, value in self.languages.items()])
        self.languages["Hebrew"] = "iw"
        self.languages["Chinese (traditional)"] = "zh-TW"
        self.languages["Chinese (simplified)"] = "zh-CN"
        self.languages_list = [i for i in self.languages.keys()]

        self.sl = str()
        self.tl = "fr"

        # Web Driver and Options
        self.options = ChromeOptions()
        self.options.add_argument("headless")

        self.driver = Chrome(options=self.options)
        self.driver.maximize_window()
        self.driver.get(BASE_URL)
        self.driver.implicitly_wait(10)

        self.accept_condition()

        # Style
        self.app_style = ttk.Style()
        self.app_style.theme_create('appstyle', parent='alt',
                                    settings={'TCombobox': {'configure': {'selectbackground': "white",
                                                                          'fieldbackground': "white",
                                                                          'background': "white",
                                                                          'selectforeground': "black"}}
                                              })
        self.app_style.theme_use('appstyle')

        # Font
        pyglet.font.add_directory("./fonts")

        # Root options
        self.title("Translator")
        self.resizable(False, False)
        self.option_add('*TCombobox*Listbox.font', NORMAL_FONT)
        self.option_add('*TCombobox*Listbox.justify', "center")
        self.option_add('*TCombobox*Scrollbar.width', 40)
        self.wm_protocol("WM_DELETE_WINDOW", self.exit)

        if system() == "Windows":
            self.iconbitmap("./images/languages.ico")
        elif system() == "Linux":
            icon = tk.PhotoImage(master=self, file="./images/languages.png")
            self.wm_iconphoto(True, icon)

        # Widgets
        self.radio_value = StringVar()
        self.input_text = tk.scrolledtext.ScrolledText(self, width=30, height=10, font=NORMAL_FONT, wrap="word")
        self.output_text = tk.scrolledtext.ScrolledText(self, width=30, height=10, font=NORMAL_FONT, wrap="word")
        self.input_combo = ttk.Combobox(self, values=self.languages_list, font=NORMAL_FONT, justify=tk.CENTER)
        self.output_combo = ttk.Combobox(self, values=self.languages_list, font=NORMAL_FONT, justify=tk.CENTER)
        self.trad_btn = tk.Button(self, text="Translate", font=NORMAL_FONT, command=self.translate)
        self.clear_btn = tk.Button(self, text="Clear", font=NORMAL_FONT, command=self.clear)
        self.auto_radio = tk.Radiobutton(self, text="Auto detect", variable=self.radio_value, value="auto")
        self.select_radio = tk.Radiobutton(self, text="Select language", variable=self.radio_value, value="select")

        self.input_combo.config(state="readonly")
        self.output_combo.config(state="readonly")
        self.auto_radio.config(font=NORMAL_FONT, command=self.on_radio_choice)
        self.select_radio.config(font=NORMAL_FONT, command=self.on_radio_choice)
        self.input_text.bind("<KeyRelease>", self.check_if_translate)
        self.input_text.config(borderwidth=3)
        self.output_text.config(borderwidth=3)

        self.input_combo.set("Auto")
        self.output_combo.set("French")
        self.auto_radio.select()
        self.input_combo.config(state=tk.DISABLED)
        self.trad_btn.config(state=tk.DISABLED, borderwidth=3)
        self.clear_btn.config(borderwidth=3)
        self.input_text.focus_set()

        self.input_text.grid(row=0, column=0, pady=5)
        self.output_text.grid(row=0, column=1, pady=5)
        self.input_combo.grid(row=1, column=0)
        self.auto_radio.grid(row=2, column=0)
        self.select_radio.grid(row=3, column=0)
        self.output_combo.grid(row=1, column=1)
        self.trad_btn.grid(row=2, column=1, pady=(10, 5))
        self.clear_btn.grid(row=3, column=1, ipadx=15, pady=(0, 10))

    def accept_condition(self):
        try:
            btn = self.driver.find_element(by=By.XPATH, value=ACCEPT_BTN_XPATH)
            btn.click()
        except NoSuchElementException as e:
            print(e)
            self.exit()
        except ElementClickInterceptedException as e:
            print(e)
            self.exit()

    def translate(self):
        try:
            if self.radio_value.get() == "select":
                self.sl = self.languages[self.input_combo.get()]
                self.tl = self.languages[self.output_combo.get()]
                self.driver.get(f"https://translate.google.com/?sl={self.sl}&tl={self.tl}&op=translate")
            elif self.radio_value.get() == "auto":
                self.tl = self.languages[self.output_combo.get()]
                self.driver.get(f"https://translate.google.com/?sl=auto&tl={self.tl}&op=translate")

            text_area = self.driver.find_element(by=By.XPATH, value=INPUT_XPATH)
            action = ActionChains(self.driver)
            action.key_down(Keys.CONTROL).send_keys('A').key_up(Keys.CONTROL).perform()
            text_area.send_keys(Keys.BACKSPACE)
            text_area.send_keys(self.input_text.get("1.0", tk.END))

        except NoSuchElementException as e:
            print(e)
            self.exit()

        try:
            trad = self.driver.find_element(by=By.XPATH, value=OUTPUT_XPATH)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", trad.text)

            if self.radio_value.get() == "auto":
                self.input_combo.config(state=tk.NORMAL)
                test = self.driver.find_element(by=By.XPATH, value=TEST)
                self.input_combo.set(test.text.split(" - ")[0].capitalize())
                self.input_combo.config(state=tk.DISABLED)

        except NoSuchElementException as e:
            print(e)
            self.exit()

    def clear(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.check_if_translate(1)

    def exit(self):
        self.driver.close()
        self.driver.quit()
        sys.exit()

    def on_radio_choice(self):
        if self.radio_value.get() == "auto":
            self.input_combo.set("Auto")
            self.input_combo.config(state=tk.DISABLED)
        elif self.radio_value.get() == "select":
            self.input_combo.config(state="readonly")
            self.input_combo.set("English")

    def check_if_translate(self, event):
        if len(self.input_text.get("1.0", tk.END)) == 1:
            self.trad_btn.config(state=tk.DISABLED)
        else:
            self.trad_btn.config(state=tk.NORMAL)

        return event


if __name__ == '__main__':
    app = App()
    app.mainloop()
