import sys
import os
import tkinter as tk
from tkinter import messagebox, colorchooser, filedialog

import utils
utils.check_and_setup_dependencies()

import customtkinter as ctk
import engine

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class YuzukoAAGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("950x900")
        self.minsize(850, 700)
        
        self.current_lang = "JP"
        self.font_list = utils.load_font_cache()

        self.ui_texts = {
            "JP": {
                "title": "ユズコ式AAロゴジェネレーター",
                "help": "ヘルプ/ログ",
                "font": "フォント (入力で検索可):",
                "update": "更新",
                "size": "サイズ:",
                "aspect": "アスペクト比",
                "letter_spacing": "文字間隔:",
                "line_spacing": "行間:",
                "input": "テキスト入力 (複数行対応):",
                "charset": "文字セット:",
                "charset_vals": ["ベタ塗り (█)", "階調表現 (█▓▒░)"],
                "single": "単色",
                "c_start": "開始色:",
                "c_end": "終了色:",
                "dir": "グラデ方向:",
                "dir_vals": ["水平 (Horizontal)", "垂直 (Vertical)"],
                "shadow": "シャドウ",
                "offset_x": "ズレX:",
                "offset_y": "ズレY:",
                "btn_gen": "AA生成",
                "btn_save_img": "画像保存",
                "btn_cp_c": "コピー (色付)",
                "btn_cp_p": "コピー (色無)",
                "btn_cmd": "CMDカラー確認",
                "preview": "プレビュー (白黒確認用):"
            },
            "EN": {
                "title": "AA Logo Generator Type Yuzuko",
                "help": "Help/Log",
                "font": "Font (Type to search):",
                "update": "Update",
                "size": "Size:",
                "aspect": "Aspect Ratio",
                "letter_spacing": "Letter Spacing:",
                "line_spacing": "Line Spacing:",
                "input": "Input Text (Multi-line):",
                "charset": "Charset:",
                "charset_vals": ["Solid (█)", "Gradient (█▓▒░)"],
                "single": "Single",
                "c_start": "Start Color:",
                "c_end": "End Color:",
                "dir": "Direction:",
                "dir_vals": ["Horizontal", "Vertical"],
                "shadow": "Shadow",
                "offset_x": "Offset X:",
                "offset_y": "Offset Y:",
                "btn_gen": "Generate AA",
                "btn_save_img": "Save Image",
                "btn_cp_c": "Copy (Color)",
                "btn_cp_p": "Copy (Plain)",
                "btn_cmd": "CMD Preview",
                "preview": "Preview (B&W):"
            }
        }

        self.setup_ui()
        self.apply_language()

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        self.lbl_title = ctk.CTkLabel(top_frame, text="", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.pack(side="left", padx=10)
        
        self.btn_help = ctk.CTkButton(top_frame, text="", width=80, command=self.show_help)
        self.btn_help.pack(side="right", padx=5)
        
        self.btn_lang = ctk.CTkButton(top_frame, text="EN", width=50, command=self.toggle_lang)
        self.btn_lang.pack(side="right", padx=5)

        font_frame = ctk.CTkFrame(self)
        font_frame.pack(fill="x", padx=10, pady=10)
        
        self.lbl_font = ctk.CTkLabel(font_frame, text="")
        self.lbl_font.pack(side="left", padx=(10, 5), pady=10)
        
        self.combo_font = ctk.CTkComboBox(font_frame, values=self.font_list, width=250)
        self.combo_font.pack(side="left", padx=5)
        if self.font_list:
            self.combo_font.set(self.font_list[0])
            
        self.combo_font.bind("<KeyRelease>", self.filter_fonts)
            
        self.btn_update_font = ctk.CTkButton(font_frame, text="", width=50, command=self.update_fonts)
        self.btn_update_font.pack(side="left", padx=5)
        
        self.lbl_size = ctk.CTkLabel(font_frame, text="")
        self.lbl_size.pack(side="left", padx=(20, 5))
        
        self.entry_size = ctk.CTkEntry(font_frame, width=50)
        self.entry_size.insert(0, "20")
        self.entry_size.pack(side="left", padx=5)

        self.lbl_letter_spacing = ctk.CTkLabel(font_frame, text="")
        self.lbl_letter_spacing.pack(side="left", padx=(20, 5))

        self.entry_letter_spacing = ctk.CTkEntry(font_frame, width=40)
        self.entry_letter_spacing.insert(0, "0")
        self.entry_letter_spacing.pack(side="left", padx=5)

        self.lbl_line_spacing = ctk.CTkLabel(font_frame, text="")
        self.lbl_line_spacing.pack(side="left", padx=(20, 5))

        self.entry_line_spacing = ctk.CTkEntry(font_frame, width=40)
        self.entry_line_spacing.insert(0, "0")
        self.entry_line_spacing.pack(side="left", padx=5)
        
        aspect_frame = ctk.CTkFrame(self, fg_color="transparent")
        aspect_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.lbl_aspect = ctk.CTkLabel(aspect_frame, text="")
        self.lbl_aspect.pack(side="left", padx=(10, 5))
        
        self.slider_aspect = ctk.CTkSlider(aspect_frame, from_=0.1, to=2.0, number_of_steps=190, width=120, command=self.update_aspect_label) # type: ignore
        self.slider_aspect.set(0.5)
        self.slider_aspect.pack(side="left", padx=5)

        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.lbl_input = ctk.CTkLabel(input_frame, text="")
        self.lbl_input.pack(anchor="w", padx=10, pady=(10, 0))
        
        self.textbox_input = ctk.CTkTextbox(input_frame, height=100)
        self.textbox_input.pack(fill="both", expand=True, padx=10, pady=10)

        style_frame = ctk.CTkFrame(self)
        style_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.lbl_charset = ctk.CTkLabel(style_frame, text="")
        self.lbl_charset.pack(side="left", padx=(10, 5), pady=10)
        
        self.combo_charset = ctk.CTkComboBox(style_frame, values=[], width=110)
        self.combo_charset.pack(side="left", padx=2)
        
        self.checkbox_single = ctk.CTkCheckBox(style_frame, text="", width=50, command=self.toggle_single)
        self.checkbox_single.pack(side="left", padx=(5, 5))
        
        self.lbl_c_start = ctk.CTkLabel(style_frame, text="")
        self.lbl_c_start.pack(side="left", padx=(5, 2))
        
        self.entry_color_start = ctk.CTkEntry(style_frame, width=60)
        self.entry_color_start.insert(0, "#FF00FF")
        self.entry_color_start.pack(side="left", padx=2)
        
        self.btn_pick_start = ctk.CTkButton(style_frame, text="■", width=30, fg_color="#FF00FF", 
                                            command=lambda: self.pick_color(self.entry_color_start, self.btn_pick_start))
        self.btn_pick_start.pack(side="left", padx=2)
        
        self.lbl_c_end = ctk.CTkLabel(style_frame, text="")
        self.lbl_c_end.pack(side="left", padx=(5, 2))
        
        self.entry_color_end = ctk.CTkEntry(style_frame, width=60)
        self.entry_color_end.insert(0, "#00FFFF")
        self.entry_color_end.pack(side="left", padx=2)
        
        self.btn_pick_end = ctk.CTkButton(style_frame, text="■", width=30, fg_color="#00FFFF", 
                                          command=lambda: self.pick_color(self.entry_color_end, self.btn_pick_end))
        self.btn_pick_end.pack(side="left", padx=2)
        
        self.lbl_dir = ctk.CTkLabel(style_frame, text="")
        self.lbl_dir.pack(side="left", padx=(5, 2))
        
        self.combo_dir = ctk.CTkComboBox(style_frame, values=[], width=120)
        self.combo_dir.pack(side="left", padx=2)

        effect_frame = ctk.CTkFrame(self)
        effect_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.checkbox_shadow = ctk.CTkCheckBox(effect_frame, text="", width=50)
        self.checkbox_shadow.pack(side="left", padx=(10, 5), pady=10)
        
        self.lbl_offset_x = ctk.CTkLabel(effect_frame, text="")
        self.lbl_offset_x.pack(side="left", padx=(15, 2))
        
        self.entry_offset_x = ctk.CTkEntry(effect_frame, width=40)
        self.entry_offset_x.insert(0, "2")
        self.entry_offset_x.pack(side="left", padx=2)
        
        self.lbl_offset_y = ctk.CTkLabel(effect_frame, text="")
        self.lbl_offset_y.pack(side="left", padx=(15, 2))
        
        self.entry_offset_y = ctk.CTkEntry(effect_frame, width=40)
        self.entry_offset_y.insert(0, "1")
        self.entry_offset_y.pack(side="left", padx=2)

        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.btn_generate = ctk.CTkButton(action_frame, text="", command=self.generate_aa, fg_color="#FF5722", hover_color="#E64A19", width=90)
        self.btn_generate.pack(side="left", padx=5)

        self.btn_save_img = ctk.CTkButton(action_frame, text="", command=self.save_as_image, fg_color="#4CAF50", hover_color="#388E3C", width=90)
        self.btn_save_img.pack(side="left", padx=5)
        
        self.btn_copy_color = ctk.CTkButton(action_frame, text="", command=lambda: self.copy_to_clip(color=True), width=100)
        self.btn_copy_color.pack(side="left", padx=5)
        
        self.btn_copy_plain = ctk.CTkButton(action_frame, text="", command=lambda: self.copy_to_clip(color=False), width=100)
        self.btn_copy_plain.pack(side="left", padx=5)
        
        self.btn_cmd = ctk.CTkButton(action_frame, text="", command=self.open_in_cmd, width=120)
        self.btn_cmd.pack(side="right", padx=5)

        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.lbl_preview = ctk.CTkLabel(preview_frame, text="")
        self.lbl_preview.pack(anchor="w", padx=10, pady=(5, 0))
        
        fixed_font = ctk.CTkFont(family="Consolas", size=12)
        self.textbox_preview = ctk.CTkTextbox(preview_frame, font=fixed_font, wrap="none")
        self.textbox_preview.pack(fill="both", expand=True, padx=10, pady=10)

        self.current_ansi_text = ""
        self.current_image = None

    def update_aspect_label(self, value):
        t = self.ui_texts[self.current_lang]
        self.lbl_aspect.configure(text=f"{t['aspect']}: {value:.2f}")

    def filter_fonts(self, event):
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Return'):
            return
            
        typed = self.combo_font.get()
        if not typed:
            self.combo_font.configure(values=self.font_list)
        else:
            filtered = [f for f in self.font_list if typed.lower() in f.lower()]
            self.combo_font.configure(values=filtered if filtered else ["Not Found"])

    def toggle_single(self):
        if self.checkbox_single.get() == 1:
            self.entry_color_end.configure(state="disabled")
            self.btn_pick_end.configure(state="disabled")
            self.combo_dir.configure(state="disabled")
        else:
            self.entry_color_end.configure(state="normal")
            self.btn_pick_end.configure(state="normal")
            self.combo_dir.configure(state="normal")

    def apply_language(self):
        t = self.ui_texts[self.current_lang]
        
        self.title(t["title"])
        self.lbl_title.configure(text=t["title"])
        self.btn_help.configure(text=t["help"])
        
        self.lbl_font.configure(text=t["font"])
        self.btn_update_font.configure(text=t["update"])
        self.lbl_size.configure(text=t["size"])
        self.lbl_letter_spacing.configure(text=t["letter_spacing"])
        self.lbl_line_spacing.configure(text=t["line_spacing"])
        
        current_aspect = self.slider_aspect.get()
        self.lbl_aspect.configure(text=f"{t['aspect']}: {current_aspect:.2f}")
        
        self.lbl_input.configure(text=t["input"])
        
        self.lbl_charset.configure(text=t["charset"])
        self.combo_charset.configure(values=t["charset_vals"])
        self.combo_charset.set(t["charset_vals"][0])
        
        self.checkbox_single.configure(text=t["single"])
        
        self.lbl_c_start.configure(text=t["c_start"])
        self.lbl_c_end.configure(text=t["c_end"])
        
        self.lbl_dir.configure(text=t["dir"])
        self.combo_dir.configure(values=t["dir_vals"])
        self.combo_dir.set(t["dir_vals"][0])

        self.checkbox_shadow.configure(text=t["shadow"])
        self.lbl_offset_x.configure(text=t["offset_x"])
        self.lbl_offset_y.configure(text=t["offset_y"])
        
        self.btn_generate.configure(text=t["btn_gen"])
        self.btn_save_img.configure(text=t["btn_save_img"])
        self.btn_copy_color.configure(text=t["btn_cp_c"])
        self.btn_copy_plain.configure(text=t["btn_cp_p"])
        self.btn_cmd.configure(text=t["btn_cmd"])
        
        self.lbl_preview.configure(text=t["preview"])

    def toggle_lang(self):
        self.current_lang = "EN" if self.current_lang == "JP" else "JP"
        self.btn_lang.configure(text="JP" if self.current_lang == "EN" else "EN")
        self.apply_language()

    def pick_color(self, entry_widget, btn_widget):
        color_code = colorchooser.askcolor(title="色を選択")[1]
        if color_code:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, color_code)
            btn_widget.configure(fg_color=color_code)

    def show_help(self):
        if self.current_lang == "JP":
            msg = (
                "【トラブルシューティング】\n\n"
                "・フォントが読み込めない、または見つからない場合は、アプリと同じフォルダにある「error_log.txt」をご確認ください。\n"
                "・「更新」ボタンを押すことで、新しくインストールしたフォントを読み込むことができます。\n"
                "・CMDカラー確認で色が表示されない場合は、お使いのターミナル設定をご確認ください。\n"
                "・プレビュー画面では白黒で表示されますが、コピーや画像保存には色が反映されます。"
            )
        else:
            msg = (
                "[Troubleshooting]\n\n"
                "- If fonts cannot be loaded or found, please check 'error_log.txt' in the same directory as the app.\n"
                "- Press the 'Update' button to load newly installed fonts.\n"
                "- If colors do not appear in CMD Preview, check your terminal settings.\n"
                "- The preview area is B&W, but colors are retained for copying and image saving."
            )
        messagebox.showinfo("Help", msg)

    def update_fonts(self):
        self.font_list = utils.force_update_font_cache()
        self.combo_font.configure(values=self.font_list)
        if self.font_list:
            self.combo_font.set(self.font_list[0])

    def generate_aa(self):
        text = self.textbox_input.get("1.0", "end-1c")
        
        text = text.replace('\t', '    ')
        
        if not text.strip():
            return
            
        font_name = self.combo_font.get()
        
        try:
            font_size = int(self.entry_size.get())
        except ValueError:
            font_size = 20

        try:
            letter_spacing = int(self.entry_letter_spacing.get())
        except ValueError:
            letter_spacing = 0

        try:
            line_spacing = int(self.entry_line_spacing.get())
        except ValueError:
            line_spacing = 0
            
        aspect = self.slider_aspect.get()
        charset = "solid" if "█" in self.combo_charset.get() and "░" not in self.combo_charset.get() else "gradient"
        
        c_start = self.entry_color_start.get()
        if self.checkbox_single.get() == 1:
            c_end = c_start
        else:
            c_end = self.entry_color_end.get()
            
        direction = "horizontal" if "Horizontal" in self.combo_dir.get() or "水平" in self.combo_dir.get() else "vertical"

        shadow_on = bool(self.checkbox_shadow.get() == 1)
        try:
            off_x = int(self.entry_offset_x.get())
            off_y = int(self.entry_offset_y.get())
        except ValueError:
            off_x = 2
            off_y = 1

        try:
            plain_text, ansi_text, out_img = engine.create_ascii_art(
                text=text, font_name=font_name, font_size=font_size, 
                aspect=aspect, charset=charset, 
                color_start=c_start, color_end=c_end, direction=direction,
                shadow=shadow_on, shadow_offset_x=off_x, shadow_offset_y=off_y,
                letter_spacing=letter_spacing, line_spacing=line_spacing
            )
            
            self.textbox_preview.delete("1.0", "end")
            self.textbox_preview.insert("1.0", plain_text)
            
            self.current_ansi_text = ansi_text
            self.current_image = out_img
            
        except Exception as e:
            utils.log_error(f"Generate Error: {str(e)}")
            messagebox.showerror("Error", "生成時にエラーが発生しました。ログをご確認ください。")

    def save_as_image(self):
        if not self.current_image:
            msg = "先にAAを生成してください。" if self.current_lang == "JP" else "Please generate AA first."
            messagebox.showwarning("Warning", msg)
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            title="画像を保存" if self.current_lang == "JP" else "Save Image"
        )
        if not file_path:
            return

        try:
            self.current_image.save(file_path)
            msg = "画像を保存しました。" if self.current_lang == "JP" else "Image saved successfully."
            messagebox.showinfo("Success", msg)
        except Exception as e:
            utils.log_error(f"Image Save Error: {str(e)}")
            messagebox.showerror("Error", "画像の保存中にエラーが発生しました。ログをご確認ください。")

    def copy_to_clip(self, color=False):
        text_to_copy = self.current_ansi_text if color else self.textbox_preview.get("1.0", "end-1c")
        if text_to_copy:
            utils.copy_to_clipboard(text_to_copy)
            messagebox.showinfo("Copied", "クリップボードにコピーしました。")

    def open_in_cmd(self):
        if not self.current_ansi_text:
            return
        utils.preview_in_cmd(self.current_ansi_text)

if __name__ == "__main__":
    app = YuzukoAAGenerator()
    app.mainloop()