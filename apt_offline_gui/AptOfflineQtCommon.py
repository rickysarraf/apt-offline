# -*- coding: utf-8 -*-

styles = {
            'red': "<span style='color:red;'>#</span>",
            'green': "<span style='color:green;'>#</span>",
            'green_fin': "<span style='color:green;font-weight:bold;'>#</span>"
        }

def style(text, style_type):
    try:
        return styles[style_type].replace("#",text)
    except:
        return text