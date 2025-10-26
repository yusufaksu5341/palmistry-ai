import random
import os
import cv2
import numpy as np
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.core.window import Window

class CustomButton(Button):
    def __init__(self, **kwargs):
        super(CustomButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.2, 0.7, 0.3, 1) 
        self.color = (1, 1, 1, 1)  
        self.border = (0, 0, 0, 0)
        
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        Window.clearcolor = (0.95, 0.95, 0.95, 1)  
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        top_box = BoxLayout(orientation='vertical', size_hint=(1, 0.7))
        
        img_container = BoxLayout(orientation='vertical', 
                                size_hint=(1, 0.8),
                                padding=(50, 20))
        
        logo = Image(source='images/xatu.png',
                    size_hint=(1, 1),
                    allow_stretch=True,
                    keep_ratio=True)
        
        title = Label(text="Xatu'nun Kehaneti",
                     font_size=32,
                     size_hint=(1, 0.2),
                     color=(0.2, 0.2, 0.2, 1), 
                     bold=True)
        
        img_container.add_widget(logo)
        img_container.add_widget(title)
        
        top_box.add_widget(img_container)
        
        btn_container = BoxLayout(orientation='vertical',
                                size_hint=(1, 0.3),
                                padding=(80, 20))
        
        start_btn = CustomButton(
            text="Falına Bak",
            size_hint=(1, None),
            height=60,
            font_size=24
        )
        start_btn.bind(on_press=self.go_to_camera)
        
        btn_container.add_widget(start_btn)
        
        main_layout.add_widget(top_box)
        main_layout.add_widget(btn_container)
        
        self.add_widget(main_layout)

    def go_to_camera(self, instance):
        self.manager.current = 'camera'

class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)
        Window.clearcolor = (0.1, 0.1, 0.1, 1)  
        
        self.capture = None
        self.frame = None
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        camera_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.8),
            padding=10
        )
        
        self.img_widget = Image(size_hint=(1, 1))
        camera_container.add_widget(self.img_widget)
        
        controls_container = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.2),
            padding=(40, 10),
            spacing=20
        )
        
        back_btn = CustomButton(
            text='Geri Dön',
            size_hint=(0.3, None),
            height=50,
            background_color=(0.7, 0.2, 0.2, 1)  
        )
        back_btn.bind(on_press=self.go_back)
        
        # Çekim butonu
        capture_btn = CustomButton(
            text='El Görüntüsünü Al',
            size_hint=(0.7, None),
            height=50
        )
        capture_btn.bind(on_press=self.capture_image)
        
        controls_container.add_widget(back_btn)
        controls_container.add_widget(capture_btn)
        
        main_layout.add_widget(camera_container)
        main_layout.add_widget(controls_container)
        
        self.add_widget(main_layout)
    
    def go_back(self, instance):
        self.manager.current = 'main'

    def on_enter(self):
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def on_leave(self):
        if self.capture:
            self.capture.release()
        Clock.unschedule(self.update)

    def update(self, dt):
        if self.capture:
            ret, frame = self.capture.read()
            if ret:
                buf = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.img_widget.texture = texture
                self.frame = frame

    def capture_image(self, instance):
        os.makedirs("images", exist_ok=True)
        cv2.imwrite("images/el_goruntusu.jpg", self.frame)
        self.manager.get_screen('analysis').analyze_palm()
        self.manager.current = 'analysis'

class AnalysisScreen(Screen):
    def __init__(self, **kwargs):
        super(AnalysisScreen, self).__init__(**kwargs)
        Window.clearcolor = (0.95, 0.95, 0.95, 1)  # Açık gri arkaplan
        
        # Ana düzen
        main_layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # Başlık container'ı
        title_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.15),
            padding=(0, 10)
        )
        
        title = Label(
            text="El Çizgisi Analizi",
            font_size=36,
            color=(0.2, 0.2, 0.2, 1),
            bold=True
        )
        title_container.add_widget(title)
        
        scroll = BoxLayout(orientation='vertical', size_hint=(1, 0.7))
        
        self.grid = GridLayout(
            cols=2,
            spacing=15,
            size_hint=(1, None),
            row_force_default=True,
            row_default_height=80,
            padding=(20, 10)
        )
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        scroll.add_widget(self.grid)
        
        button_container = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.15),
            padding=(40, 10),
            spacing=20
        )
        
        back_btn = CustomButton(
            text='Ana Menüye Dön',
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.7, 0.3, 1)
        )
        back_btn.bind(on_press=self.go_main)
        
        button_container.add_widget(back_btn)
        
        main_layout.add_widget(title_container)
        main_layout.add_widget(scroll)
        main_layout.add_widget(button_container)
        
        self.add_widget(main_layout)
    
    def go_main(self, instance):
        self.manager.current = 'main'

    def interpret_line(self, name, length):
        yorumlar = {
            "Hayat Çizgisi": [
                "Yaşamın nehir gibi akıyor, güçlü ve derin.",
                "Hayatın dalgalı ama umut dolu bir yolculuk.",
                "Kırılgan bir yaşam çizgisi, dikkatli adımlar gerek."
            ],
            "Akıl Çizgisi": [
                "Zihnin yıldızlar kadar parlak, fikirlerinle ışık saçıyorsun.",
                "Düşüncelerin dengeli, kararların sağlam temellere dayanıyor.",
                "Zihinsel sisler içinde yolunu arıyorsun."
            ],
            "Kalp Çizgisi": [
                "Kalbin sevgiyle dolu, duyguların derin bir deniz gibi.",
                "Duyguların dengede, sevgiyle yürüyorsun.",
                "Kalbinin sesi uzaklardan geliyor, duygularını keşfetmelisin."
            ],
            "Kader Çizgisi": [
                "Yazgın güçlü bir rüzgar gibi seni ileri taşıyor.",
                "Hayatın dış etkilerle şekilleniyor, ama yön senin elinde.",
                "Kaderin belirsiz, kendi yolunu çizmek için cesaret gerek."
            ]
        }
        if name in yorumlar:
            if length > 200:
                return yorumlar[name][0]
            elif length > 100:
                return yorumlar[name][1]
            else:
                return yorumlar[name][2]
        else:
            rastgele = [
                "Gizli bir çizgi, sezgilerin rehberin olabilir.",
                "Bilinmeyen bir yol, macera seni bekliyor.",
                "Geleceğin puslu ama umut dolu bir ışık var."
            ]
            return random.choice(rastgele)

    def analyze_palm(self):
        image = cv2.imread("images/el_goruntusu.jpg")
        self.grid.clear_widgets()
        çizgi_sonuçları = {
            "Kalp Çizgisi": None,
            "Akıl Çizgisi": None,
            "Hayat Çizgisi": None,
            "Kader Çizgisi": None
        }

        if image is None:
            self.grid.add_widget(Label(text="Görüntü bulunamadı.", font_size=20, color=(0, 0, 0, 1)))
            return

        resized = cv2.resize(image, (600, 800))
        h, w = resized.shape[:2]
        crop_x1, crop_x2 = int(w * 0.2), int(w * 0.8)
        crop_y1, crop_y2 = int(h * 0.3), int(h * 0.85)
        palm_crop = resized[crop_y1:crop_y2, crop_x1:crop_x2]

        gray = cv2.cvtColor(palm_crop, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
        adaptive_thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )

        contours, _ = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        palm_height = palm_crop.shape[0]
        region_height = palm_height / 4

        sorted_contours = sorted(contours, key=lambda c: cv2.arcLength(c, True), reverse=True)[:8]  # En uzun 8 çizgiyi al
        
        for cnt in sorted_contours:
            x, y, w, h = cv2.boundingRect(cnt)
            length = cv2.arcLength(cnt, True)
            
            if h > 20 and w > 50:  
               
                center_y = y + h/2
                
                if center_y < region_height and çizgi_sonuçları["Kalp Çizgisi"] is None:
                    çizgi_sonuçları["Kalp Çizgisi"] = self.interpret_line("Kalp Çizgisi", length)
                elif region_height <= center_y < 2*region_height and çizgi_sonuçları["Akıl Çizgisi"] is None:
                    çizgi_sonuçları["Akıl Çizgisi"] = self.interpret_line("Akıl Çizgisi", length)
                elif 2*region_height <= center_y < 3*region_height and çizgi_sonuçları["Hayat Çizgisi"] is None:
                    çizgi_sonuçları["Hayat Çizgisi"] = self.interpret_line("Hayat Çizgisi", length)
                elif center_y >= 3*region_height and çizgi_sonuçları["Kader Çizgisi"] is None:
                    çizgi_sonuçları["Kader Çizgisi"] = self.interpret_line("Kader Çizgisi", length)

        for çizgi in çizgi_sonuçları:
            yorum = çizgi_sonuçları[çizgi]
            if yorum is None:
                yorum = self.interpret_line("Bilinmeyen", 0)
            self.grid.add_widget(Label(text=f"{çizgi}:", font_size=20, color=(0, 0, 0, 1), halign='right'))
            self.grid.add_widget(Label(text=yorum, font_size=20, color=(0, 0, 0, 1), halign='left'))

class PalmistryApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(CameraScreen(name='camera'))
        sm.add_widget(AnalysisScreen(name='analysis'))
        return sm

PalmistryApp().run()
