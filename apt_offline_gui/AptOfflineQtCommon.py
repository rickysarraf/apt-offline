# -*- coding: utf-8 -*-

styles = {
            'red': "<span style='color:red;'>#</span>",
            'orange': "<span style='color:orange;'>#</span>",
            'green': "<span style='color:green;'>#</span>",
            'green_fin': "<span style='color:green;font-weight:bold;'>#</span>"
        }

def style(text, style_type):
    try:
        return styles[style_type].replace("#",text)
    except:
        return text

def updateInto(myobject,text):
    # sanitize coloring
    if ('[1;' in text):
        return

    if ("ERROR" in text or "FATAL" in text):
        text = style(text,'red')

    if ("Completed" in text):
        text = style(text,'green_fin')

    myobject.append (text)