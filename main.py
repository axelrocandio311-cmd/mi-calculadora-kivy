from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

class CalculatorApp(App):
    def build(self):
        self.operators = ["/", "*", "+", "-"]
        self.last_was_operator = None
        self.last_button = None
        
        # Layout principal
        main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        Window.size = (400, 600)

        # Pantalla de la calculadora
        self.solution = TextInput(
            multiline=False, readonly=True, halign="right", font_size=55,
            background_color=(0.1, 0.1, 0.1, 1), foreground_color=(1, 1, 1, 1)
        )
        main_layout.add_widget(self.solution)

        # Rejilla de botones
        buttons = [
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            [".", "0", "C", "+"],
        ]

        grid_layout = GridLayout(cols=4, spacing=10)
        for row in buttons:
            for label in row:
                button = Button(
                    text=label, pos_hint={"center_x": 0.5, "center_y": 0.5},
                    background_color=(0.3, 0.3, 0.3, 1)
                )
                button.bind(on_press=self.on_button_press)
                grid_layout.add_widget(button)

        # Botón de igual
        equals_button = Button(
            text="=", pos_hint={"center_x": 0.5, "center_y": 0.5},
            background_color=(0.9, 0.5, 0.1, 1)
        )
        equals_button.bind(on_press=self.on_solution)
        
        main_layout.add_widget(grid_layout)
        main_layout.add_widget(equals_button)

        return main_layout

    def on_button_press(self, instance):
        current = self.solution.text
        button_text = instance.text

        if button_text == "C":
            self.solution.text = ""
        else:
            if current and (self.last_was_operator and button_text in self.operators):
                return
            elif current == "" and button_text in self.operators:
                return
            else:
                new_text = current + button_text
                self.solution.text = new_text
        
        self.last_button = button_text
        self.last_was_operator = self.last_button in self.operators

    def on_solution(self, instance):
        text = self.solution.text
        if text:
            try:
                # La función eval() hace la magia matemática [00:23:40]
                self.solution.text = str(eval(self.solution.text))
            except Exception:
                self.solution.text = "Error"

if __name__ == "__main__":
    app = CalculatorApp()
    app.run()
