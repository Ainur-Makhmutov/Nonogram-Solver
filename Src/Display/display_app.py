from tkinter import *
from tkinter import ttk

if __name__ == '__main__':

  root = Tk()

  root.title('Дисплей для нонограмм') #заголовок
  root.iconbitmap(default = "Data/Icon/favicon.ico")
  root.geometry("800x600+500+220")

  root.update_idletasks()
  print(root.geometry())    # "300x250+400+200"

  root.resizable(False, False) # Блокировка масштабирования окна пользователем по ширине и высоте

  label = Label(text = "rr")
  label.pack()

  btn = ttk.Button() # Кнопка из пакета ttk
  btn.pack()

  btn["text"] = "sss" # ttk.Button(text = "sss")


  root.mainloop() #отображение окна
