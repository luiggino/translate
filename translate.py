from gi.repository import Gtk
import goslate
from textblob import TextBlob
import redis

class Handler:
    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def on_imagemenuitem10_activate(self, widget):
        dialogAbout = builder.get_object("aboutdialog1")
        response = dialogAbout.run()

        if response == Gtk.ResponseType.OK:
            print("The OK button was clicked")
        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

        dialogAbout.destroy()

    def on_imagemenuitem5_activate(self, widget):
        Gtk.main_quit()

    def onAboutDialogClosed(self, widget):
        widget.destroy()

    def onClearPressed(self, button):
        textbuffer = tview_text.get_buffer()
        start = textbuffer.get_start_iter()
        end = textbuffer.get_end_iter()
        textbuffer.delete(start, end)

        textbuffer = tview_translate.get_buffer()
        start = textbuffer.get_start_iter()
        end = textbuffer.get_end_iter()
        textbuffer.delete(start, end)

    def onButtonPressed(self, button):
        textbuffer = tview_translate.get_buffer()
        start = textbuffer.get_start_iter()
        end = textbuffer.get_end_iter()
        textbuffer.delete(start, end)

        textbuffer = tview_text.get_buffer()
        start = textbuffer.get_start_iter()
        end = textbuffer.get_end_iter()

        text = u"{0}".format(textbuffer.get_text(start, end, False))
        tree_iter = comboboxtext_to.get_active_iter()
        language_to = None
        if tree_iter is not None:
            model = comboboxtext_to.get_model()
            key, language_to = model[tree_iter][:2]

        tree_iter = comboboxtext_from.get_active_iter()
        language_from = None
        if tree_iter is not None:
            model = comboboxtext_from.get_model()
            key, language_from = model[tree_iter][:2]

        if language_to is not None:
            value = r.hget(text + ":" + language_to, language_from)
            if value:
                textbuffer = tview_translate.get_buffer()
                textbuffer.set_text(value)
                return

            blob = TextBlob(text)
            if language_from == 'detect':
                language_from = blob.detect_language()

            if language_from is None:
                translate = u"{0}".format(blob.translate(to=language_to))
            else:
                translate = u"{0}".format(blob.translate(
                    from_lang=language_from, to=language_to))

            textbuffer = tview_translate.get_buffer()
            textbuffer.set_text(translate)
            if value is None:
                mapping = {language_from: translate}
                r.hmset(text + ":" + language_to, mapping)

builder = Gtk.Builder()
builder.add_from_file("window.glade")

builder.connect_signals(Handler())

window = builder.get_object("window1")
window.show_all()

tview_text = builder.get_object("tview_text")
tview_translate = builder.get_object("tview_translate")

gs = goslate.Goslate()

comboboxtext_to = builder.get_object("comboboxtext_to")
comboboxtext_from = builder.get_object("comboboxtext_from")

name_store_to = Gtk.ListStore(str, str)

name_store_from = Gtk.ListStore(str, str)
name_store_from.append(['detect', 'detect'])

languages = gs.get_languages()

for key, value in sorted(languages.items()):
    name_store_to.append([value, key])
    name_store_from.append([value, key])

comboboxtext_to.set_model(name_store_to)
comboboxtext_from.set_model(name_store_from)

r = redis.Redis(
    host='localhost',
    port=6379,
    password=''
    )

Gtk.main()
