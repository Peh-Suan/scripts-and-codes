from PIL import Image, ImageTk
import tkinter as tk

class areaSelectionUI:

    def __init__(self, imgPath):

        WIDTH, HEIGHT = 1100, 634
        if HEIGHT < 500:
            HEIGHT = 700
        
        self.radii, self.center, self.rec = None, None, None
        self.x1, self.y1, self.x2, self.y2, self.r = 0, 0, 0, 0, 0
        self.topx, self.topy, self.btmx, self.btmy = 0, 0, 0, 0

        self.selectArc = True
        
        def get_mouse_posn(event):
            
            if self.selectArc and not self.center_selected:
                self.x1, self.y1 = event.x, event.y
                canvas.coords(self.center_id, self.x1 - 3, self.y1 - 3, self.x1 + 3, self.y1 + 3)
                button_save3['state'] = 'normal'
                text1.configure(text = f'center: {self.x1, self.y1}; radius: 0')
            elif self.selectArc and self.center_selected:
                self.x1, self.y1 = event.x, event.y
                self.r1 = (((self.x1 - self.center[0])**2 + (self.y1 - self.center[1])**2)**.5)
                canvas.coords(self.center_id, self.center[0] - 3, self.center[1] - 3, self.center[0] + 3, self.center[1] + 3)
                canvas.coords(self.c1_id, self.center[0] - self.r1, self.center[1] - self.r1, self.center[0] + self.r1, self.center[1] + self.r1)
                canvas.coords(self.c2_id, 0, 0, 0, 0)
                text1.configure(text = f'center: {self.center}; radii: (0, 0)')
            else:
                self.btmx, self.btmy = 0, 0
                self.topx, self.topy = event.x, event.y
                text1.configure(text = f'rectangle: {self.topx, self.topy, self.btmx, self.btmy}')
                button_save4['state'] = 'normal'
                

        def update_selection(event):
            if self.selectArc and not self.center_selected:
                self.x2, self.y2 = event.x, event.y
                self.r = (((self.x1 - self.x2)**2 + (self.y1 - self.y2)**2)**.5)
                canvas.coords(self.c1_id, self.x1 - self.r, self.y1 - self.r, self.x1 + self.r, self.y1 + self.r)
                text1.configure(text = f'center: {self.x1, self.y1}; radius: {round(self.r, 2)}')
            elif self.selectArc and self.center_selected:
                self.x2, self.y2 = event.x, event.y
                self.r2 = (((self.center[0] - self.x2)**2 + (self.center[1] - self.y2)**2)**.5)
                canvas.coords(self.c2_id, self.center[0] - self.r2, self.center[1] - self.r2, self.center[0] + self.r2, self.center[1] + self.r2)
                text1.configure(text = f'center: {self.center}; radii: {round(self.r1, 2), round(self.r2, 2)}')
            else:
                self.btmx, self.btmy = event.x, event.y
                canvas.coords(self.rect_id, self.topx, self.topy, self.btmx, self.btmy)
                text1.configure(text = f'rectangle: {self.topx, self.topy, self.btmx, self.btmy}')

    
        def save_radius():
            if self.selectArc:
                canvas.coords(self.c1_id, 0, 0, 0, 0)
                canvas.coords(self.c2_id, 0, 0, 0, 0)
                canvas.coords(self.center_id, 0, 0, 0, 0)
                if self.r1 < self.r2:
                    self.radii = (round(self.r1), round(self.r2))
                else:
                    self.radii = (round(self.r2), round(self.r1))
                if None not in [self.radii, self.center, self.rec]:
                    button_quit['state'] = 'normal'
                text2.configure(text = f'radii: {round(self.r1, 2), round(self.r2, 2)}')
            else:
                pass



        def save_center():
            if self.selectArc:
                canvas.coords(self.c1_id, 0, 0, 0, 0)
                self.center = (self.x1, self.y1)
                text4.configure(text = f'center: {self.x1, self.y1}')
                self.center_selected = True
                button_save1['state'] = 'normal'
                text2.configure(text = 'radii: Please select')
                button_save3['state'] = 'disabled'
                if None not in [self.radii, self.center, self.rec]:
                    button_quit['state'] = 'normal'
            else:
                pass
            
        def save_rectangle():
            if self.selectArc:
                pass
            else:
                canvas.coords(self.rect_id, 0, 0, 0, 0)
                if self.topx < self.btmx:
                    x_first, x_second = self.topx, self.btmx
                else:
                    x_first, x_second = self.btmx, self.topx
                if self.topy < self.btmy:
                    y_first, y_second = self.topy, self.btmy
                else:
                    y_first, y_second = self.btmy, self.topy
                text5.configure(text = f'rectangle: {x_first, y_first, x_second, y_second}')
                self.rec = (x_first, y_first, x_second, y_second)
                if None not in [self.radii, self.center, self.rec]:
                    button_quit['state'] = 'normal'
            
        def select_arc():
            canvas.coords(self.c1_id, 0, 0, 0, 0)
            canvas.coords(self.c2_id, 0, 0, 0, 0)
            canvas.coords(self.center_id, 0, 0, 0, 0)
            canvas.coords(self.rect_id, 0, 0, 0, 0)
            self.selectArc = not self.selectArc
            button_save1['state'] = 'disabled'
            button_save3['state'] = 'disabled'
            button_save4['state'] = 'disabled'
            if self.selectArc:
                button_select.configure(text = 'Arc selection')
                text1.configure(text = f'center: {0, 0}; r: {0}')
                if self.center_selected:
                    button_save1['state'] = 'normal'
                text2.configure(fg = 'black')
                text4.configure(fg = 'black')
                text5.configure(fg = 'gray')
                
            else:
                button_select.configure(text = 'Rectangle selection')
                text1.configure(text = f'rectangle: (0, 0, 0, 0)')
                text2.configure(fg = 'gray')
                text4.configure(fg = 'gray')
                text5.configure(fg = 'black')
            if None not in [self.radii, self.center, self.rec]:
                button_quit['state'] = 'normal'
        
        def erase_all():
            self.center_selected = False
            canvas.coords(self.c1_id, 0, 0, 0, 0)
            canvas.coords(self.c2_id, 0, 0, 0, 0)
            canvas.coords(self.center_id, 0, 0, 0, 0)
            canvas.coords(self.rect_id, 0, 0, 0, 0)
            button_save1['state'] = 'disabled'
            button_save3['state'] = 'disabled'
            button_save4['state'] = 'disabled'
            button_quit['state'] = 'disabled'
            if self.selectArc:
                text1.configure(text = f'center: {0, 0}; r: {0}')
                text2.configure(text = f'radii: Please select center first')
                text4.configure(text = f'center: Please select')
                text5.configure(text = f'rectangle: Please select')
            else:
                text1.configure(text = f'rectangle: (0, 0, 0, 0)')
                text2.configure(text = f'radii: Please select center first')
                text4.configure(text = f'center: Please select')
                text5.configure(text = f'rectangle: Please select')

        self.window = tk.Tk()
        self.window.title("Select Area")
        self.window.geometry('%sx%s' % (WIDTH, HEIGHT))
        img = ImageTk.PhotoImage(Image.open(imgPath))
        
        self.center_selected = False
        canvas = tk.Canvas(self.window, width = img.width(), height = img.height(), borderwidth = 10, highlightthickness = 0, bg ='white')
        canvas.place(x = 10, y = 10)
        
        canvas.create_image(10, 10, image = img, anchor = tk.NW)

        self.center_id = canvas.create_oval(0, 0, 0, 0, fill = 'red', outline = 'red')
        self.c1_id = canvas.create_oval(0, 0, 0, 0, dash = (2,2), fill = '', outline = 'white')
        self.c2_id = canvas.create_oval(0, 0, 0, 0, dash = (2,2), fill = '', outline = 'white')
        self.rect_id = canvas.create_rectangle(0, 0, 0, 0, dash=(2, 2), fill = '', outline = 'white')

        text1 = tk.Label(self.window, text = f'center: {self.x1, self.y1}; radius: {self.r}')
        text1.place(x = img.width() + 50, y = 10)

        text2 = tk.Label(self.window, text = f'radii: Please select center first')
        text2.place(x = img.width() + 50, y = 60)

        text4 = tk.Label(self.window, text = f'center: Please select')
        text4.place(x = img.width() + 50, y = 140)
        
        text5 = tk.Label(self.window, text = f'rectangle: Please select', fg = 'gray')
        text5.place(x = img.width() + 50, y = 220)
        
        button_select = tk.Button(self.window, text = 'Arc selection', command = select_arc)
        button_select.place(x = img.width() + 50, y = HEIGHT - 50)
        
        button_erase = tk.Button(self.window, text = 'Erase all', command = erase_all, fg = 'red')
        button_erase.place(x = img.width() + 200, y = HEIGHT - 80)
        
        button_save1 = tk.Button(self.window, text = 'Save radii', command = save_radius, state = 'disabled')

        button_save3 = tk.Button(self.window, text = 'Save center', command = save_center, state = 'disabled')
        button_save4 = tk.Button(self.window, text = 'Save rectangle', command = save_rectangle, state = 'disabled')
        
        button_quit = tk.Button(self.window, text = 'Save and Quit', command = self.window.destroy, fg = 'green', state = 'disabled')
        
        
        button_save1.place(x = img.width() + 50, y = 90)
        button_save3.place(x = img.width() + 50, y = 170)
        button_save4.place(x = img.width() + 50, y = 250)
        button_quit.place(x = img.width() + 200, y = HEIGHT - 50)
    


        canvas.bind('<Button-1>', get_mouse_posn)
        canvas.bind('<B1-Motion>', update_selection)

        self.window.mainloop()

selectedArea = areaSelectionUI(input('Please enter image path:'))

with open('Crop Info.txt', 'w') as file:
    file.write(f'radii:\t\t{selectedArea.radii}\ncenter:\t\t{selectedArea.center}\nrectangle:\t{selectedArea.rec}')


print(f'radii:{selectedArea.radii}\ncenter:{selectedArea.center}\nrectangle:{selectedArea.rec}\nInformation saved as "Crop Info.txt".')

