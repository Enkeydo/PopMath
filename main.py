__version__ = "0.7.1"

import os
import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

try:
    from packages import package_sizes
except ImportError:
    package_sizes = {"1": ("File Missing: packages.py", 0, 1)}

class CustomSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = dp(55)
        self.font_size = '16sp'
        self.background_normal = ''
        self.background_color = (0.2, 0.2, 0.2, 1)

class DrPepperCalc(App):
    def build(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "popmath.db")
        self.init_db()

        self.package_lookup = {}
        for pkg_id, (label, oz, units_per_pack) in package_sizes.items():
            display_name = f"{pkg_id}: {label}"
            self.package_lookup[display_name] = (oz, units_per_pack)
        
        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # --- SCROLLABLE INPUTS ---
        scroll = ScrollView(size_hint=(1, 0.6))
        input_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(12))
        input_layout.bind(minimum_height=input_layout.setter('height'))

        input_layout.add_widget(Label(text="Select Package Type:", size_hint_y=None, height=dp(25), color=(0.7, 0.7, 0.7, 1)))
        
        # Spinner initialized with the counts
        self.type_spinner = Spinner(
            text='Select...', values=self.get_spinner_values_with_counts(),
            size_hint_y=None, height=dp(60), option_cls=CustomSpinnerOption,
            background_normal='', background_color=(0.15, 0.15, 0.15, 1)
        )
        self.type_spinner.dropdown_cls.max_height = dp(450)
        input_layout.add_widget(self.type_spinner)

        input_layout.add_widget(Label(text="Package Size (Quantity):", size_hint_y=None, height=dp(25), color=(0.7, 0.7, 0.7, 1)))
        self.qty_input = TextInput(text="1", multiline=False, input_filter='float', size_hint_y=None, height=dp(60), font_size='24sp')
        input_layout.add_widget(self.qty_input)

        input_layout.add_widget(Label(text="Total Price ($):", size_hint_y=None, height=dp(25), color=(0.7, 0.7, 0.7, 1)))
        self.price_input = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_y=None, height=dp(60), font_size='24sp')
        input_layout.add_widget(self.price_input)

        input_layout.add_widget(Label(text="Notes:", size_hint_y=None, height=dp(25), color=(0.7, 0.7, 0.7, 1)))
        self.notes_input = TextInput(hint_text="Store/Sale info", size_hint_y=None, height=dp(60))
        input_layout.add_widget(self.notes_input)

        scroll.add_widget(input_layout)
        root.add_widget(scroll)

        self.result_label = Label(text="Price per oz: $0.00", font_size='34sp', size_hint_y=None, height=dp(80), bold=True)
        root.add_widget(self.result_label)

        calc_btn = Button(text="Calculate & Save", size_hint_y=None, height=dp(70), font_size='22sp',
                          background_normal='', background_color=(0.1, 0.6, 0.1, 1))
        calc_btn.bind(on_release=self.calculate)
        root.add_widget(calc_btn)

        mgmt_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        log_btn = Button(text="History", background_color=(0.3, 0.3, 0.3, 1))
        log_btn.bind(on_release=self.show_history_popup)
        help_btn = Button(text="Help", background_color=(0.3, 0.3, 0.3, 1))
        help_btn.bind(on_release=self.show_help_popup)
        del_btn = Button(text="Clear Log", background_color=(0.7, 0.2, 0.2, 1))
        del_btn.bind(on_release=self.confirm_delete_popup)
        
        mgmt_layout.add_widget(log_btn)
        mgmt_layout.add_widget(help_btn)
        mgmt_layout.add_widget(del_btn)
        root.add_widget(mgmt_layout)

        return root

    def get_spinner_values_with_counts(self):
        base_displays = []
        for pkg_id, (label, _, _) in package_sizes.items():
            base_displays.append(f"{pkg_id}: {label}")

        counts = {}
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT package FROM history")
            rows = c.fetchall()
            for r in rows:
                # Matches the [ #ID ] tag in the stored history string
                for display in base_displays:
                    pkg_id = display.split(":")[0]
                    if f"[#{pkg_id}]" in r[0]:
                        counts[display] = counts.get(display, 0) + 1
            conn.close()
        except Exception:
            pass

        final_values = []
        for display in base_displays:
            count = counts.get(display, 0)
            final_values.append(f"{display} ({count})")
        return final_values

    def calculate(self, instance):
        try:
            full_text = self.type_spinner.text
            # Strip the (count) suffix for logic processing
            base_text = full_text.rsplit(" (", 1)[0] if " (" in full_text else full_text
            
            if ": " in base_text:
                pkg_id, clean_label = base_text.split(": ", 1)
            else:
                pkg_id, clean_label = "?", base_text

            oz_per_item, items_per_pack = self.package_lookup.get(base_text, (0, 0))
            multiplier = float(self.qty_input.text or 1)
            total_oz = (oz_per_item * items_per_pack) * multiplier
            
            price = float(self.price_input.text or 0)
            ppo = price / total_oz if total_oz > 0 else 0
            
            self.result_label.text = f"Price per oz: ${ppo:.4f}"
            history_entry = f"{multiplier}x {clean_label} [#{pkg_id}] ({total_oz:.1f} oz total)"
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT INTO history (package, price, ppo, note) VALUES (?, ?, ?, ?)", 
                      (history_entry, price, ppo, self.notes_input.text))
            conn.commit()
            conn.close()
            
            # Update counts in the UI immediately
            self.type_spinner.values = self.get_spinner_values_with_counts()
            self.notes_input.text = ""
        except Exception:
            self.result_label.text = "Input Error"

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS history 
                     (id INTEGER PRIMARY KEY, package TEXT, price REAL, ppo REAL, note TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

    def confirm_delete_popup(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text="Are you sure you want to delete\nall price history?"))
        btns = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        yes_btn = Button(text="Delete Everything", background_color=(0.9, 0.1, 0.1, 1))
        no_btn = Button(text="Cancel")
        btns.add_widget(yes_btn)
        btns.add_widget(no_btn)
        content.add_widget(btns)
        popup = Popup(title="Confirm Clear", content=content, size_hint=(0.8, 0.4))
        no_btn.bind(on_release=popup.dismiss)
        yes_btn.bind(on_release=lambda x: self.clear_history(popup))
        popup.open()

    def clear_history(self, popup):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM history")
        conn.commit()
        conn.close()
        # Reset counts to (0)
        self.type_spinner.values = self.get_spinner_values_with_counts()
        popup.dismiss()

    def show_help_popup(self, instance):
        help_text = (
            "[b]Quick Guide:[/b]\n\n"
            "1. [b]Package Type:[/b] Select the container (e.g., 12-pack).\n"
            "2. [b]Package Size:[/b] Use this for multi-buy deals. If it's '3 for $13', "
            "select the 12-pack in Type and enter '3' here.\n"
            "3. [b]Total Price:[/b] Enter the total cost for all items.\n\n"
            "The app calculates total volume and price-per-ounce, saving it "
            "with a timestamp in your History log."
        )
        content = BoxLayout(orientation='vertical', padding=dp(15))
        scroll = ScrollView()
        lbl = Label(text=help_text, markup=True, size_hint_y=None, halign='left', valign='top', padding=(dp(10), dp(10)))
        lbl.bind(texture_size=lbl.setter('size'))
        lbl.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        scroll.add_widget(lbl)
        content.add_widget(scroll)
        btn = Button(text="Got it", size_hint_y=None, height=dp(50))
        popup = Popup(title="Help", content=content, size_hint=(0.9, 0.6))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def show_history_popup(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        scroll = ScrollView()
        self.history_label = Label(
            text=self.get_history_text(), size_hint_y=None, halign='left', valign='top', 
            font_size='16sp', padding=(dp(25), dp(20)), markup=True
        )
        self.history_label.bind(texture_size=self.history_label.setter('size'))
        self.history_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        scroll.add_widget(self.history_label)
        content.add_widget(scroll)
        btn = Button(text="Close", size_hint_y=None, height=dp(50))
        popup = Popup(title="Price History", content=content, size_hint=(0.95, 0.9))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def get_history_text(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT package, price, ppo, note FROM history ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        text = ""
        for r in rows:
            text += f"[b]{r[0]}[/b]\n[color=00ff00]${r[1]:.2f}[/color] (${r[2]:.3f}/oz)\nNote: {r[3]}\n---\n"
        return text if text else "No history found."

if __name__ == '__main__':
    DrPepperCalc().run()