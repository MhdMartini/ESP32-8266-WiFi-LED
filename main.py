"""
Mobile User
"""
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivy.uix.colorpicker import ColorWheel
from kivy.core.window import Window
import socket

Window.size = (600, 1000)

KV = '''
Screen:
    NavigationLayout:
        ScreenManager:

            Screen:
                MDBoxLayout:
                    orientation: "vertical"

                    MDToolbar:
                        title: "Example Tabs"
                        left_action_items: [["menu", lambda x: nav_drawer.toggle_nav_drawer()]]

                    MDTabs:
                        id: tabs
                        on_tab_switch: app.on_tab_switch(*args)
                        Tab:
                            id: "LED"
                            orientation:
                                "vertical"
                            padding:
                                [0, 0 , 0 , 40]

                            text: "lightbulb-on"          

                            ColorWheel:
                                id: color_wheel
                                size_hint: (1,1)
                                pos_hint: {"center_x": 0.5, "center_y": 0.5}

                            MDFloatingActionButton:
                                id: toggle
                                icon: "toggle-switch-off"
                                text: "Toggle LED"
                                md_bg_color: app.theme_cls.primary_color
                                user_font_size: "40sp"
                                pos_hint: {"center_x": 0.5}
                                on_press:
                                    app.toggle_led()

                        Tab:
                            id: "Speaker"
                            text: "music"
                        Tab:
                            id: "Charger"
                            text: "battery-charging"

        MDNavigationDrawer:
            id: nav_drawer

            MDBoxLayout:
                orientation: "vertical"
                MDBoxLayout:
                    orientation: "vertical"
                    MDLabel:
                        text: "Top Box"
                        font_style: "H5"
                MDBoxLayout:
                    orientation: "vertical"
                    MDLabel:
                        text: "Middle Box"
                        font_style: "H5"
                MDBoxLayout:
                    orientation: "vertical"
                    MDLabel:
                        text: "Bottom Box"
                        font_style: "H5"

'''


class Tab(MDBoxLayout, MDTabsBase):
    """Class implementing content for a tab."""
    pass


class Example(MDApp):
    selected_color = (1, 0.825, 0.3, 1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def build(self):
        self.theme_cls.primary_palette = "Gray"  # Color of buttons/menus/etc,
        self.theme_cls.theme_style = "Dark"  # Primary theme. "Light" is the other option
        self.theme_cls.accent_palette = "Red"

        return Builder.load_string(KV)

    def on_start(self):
        # Bind selecting a color in the Wheel to the on_color method
        self.root.ids.color_wheel.bind(color=self.on_color)

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        # Method must exist
        # print(instance_tab.id, instance_tab.ids)
        pass

    def on_color(self, instance, value):
        # When a color is selected on the ColorWheel, change the selected_color attribute
        # to the selected RGB value
        self.selected_color = value
        self.root.ids.toggle.md_bg_color = value
        print(value)

    # Command Methods
    def toggle_led(self):
        self.sock.sendto(b"LED", ("10.0.0.167", 1111))
        dict_ = {"toggle-switch": "toggle-switch-off", "toggle-switch-off": "toggle-switch"}
        self.root.ids.toggle.icon = dict_[self.root.ids.toggle.icon]


Example().run()
