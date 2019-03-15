# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.filechooser import FileChooser
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import kivy
import requests, json
import os
# host="192.168.0.9"
# port="5000"

host='35.244.123.205'
port="80"

kivy.require('1.10.1')

def run_sql(sql,database=None):
    url = "http://"+host+":"+port+"/run/sql/"
    data = {"sql":sql ,"database":database}
    headers = {"Content-Type" : "application/json"}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r.text



def run_install(_type,scene):
    #_type:
        #(1) scene
        #(2) ap
    url = "http://"+host+":"+port+"/install/"
    data = {"type":_type,"name":scene}
    headers = {"Content-Type" : "application/json"}
    requests.post(url, data=json.dumps(data), headers=headers)

class RootWidget(BoxLayout):
    container = ObjectProperty(None)

class ClientApp(App):
    Scene=None
    Building=None
    Floor=None
    Format=None
    path=None
    def down_database(self):
        scene=self.Scene
        url="http://"+host+':'+port+"/down_database/"
        name=scene+'.csv'
        data={"scene":scene}
        html = requests.post(url,data=data)
        # path=os.getcwd()
        save_path=os.path.join('database',scene)
        # save_path=os.path.join(save_path,building)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file_name=os.path.join(save_path,name)
        with open(file_name, 'wb') as file:
            file.write(html.content)

    def upload_map(self,scene=None,building=None,floor=None,file_path=None):
        url="http://"+host+":"+port+"/upload/"
        floor_name=floor+'.jpg'
        files={"image": (floor_name, open(file_path,"rb"))}
        data={"scene":scene,"building":building}
        requests.post(url,data=data,files=files)

    def update_GUI(self,s1=None,s2=None,s3=None):
        if s1:
            scenes=self.get_scenes()
            scenes=json.loads(scenes)['result']
            if scenes:
                scenes_list=[s['name'] for s in scenes]
                s1.values=scenes_list
        if s2:
            buildings=self.get_buildings()
            buildings=json.loads(buildings)['result']
            if buildings:
                buildings_list=[b['name'] for b in buildings]
                s2.values=buildings_list
        if s3:
            floors=self.get_floors_from_building()
            floors=json.loads(floors)['result']
            if floors:
                floors_list=[f['name'] for f in floors]
                s3.values=floors_list
    def get_path(self,path):
        self.path=path[0]
    def submit_floor(self,name,width_pix,heigh_pix,width_m,heigh_m):
        self.Floor=name
        if self.path==None:
            self.popup.open()
            return None
        self.upload_map(scene=self.Scene,building=self.Building,floor=self.Floor,file_path=self.path)
        self.path=None
        sql="insert into floors(name,building_belonged,map_width_pix,map_heigh_pix,map_width_m,map_heigh_m) values ('%s','%s','%s','%s','%s','%s')" % (self.Floor,self.Building,width_pix,heigh_pix,width_m,heigh_m)
        res=run_sql(sql,self.Scene)
        self.update_GUI(s3=self.s3)


    def get_scenes(self):
        sql='select name from scenes'
        res=run_sql(sql,'wifi_information')
        # res=run_sql("show databases;",None)
        return res
    def add_scene(self,x):
        run_install('scene',x)
        self.update_GUI(s1=self.s1)
    def get_buildings(self):
        sql='select name from buildings'
        res=run_sql(sql,self.Scene)
        return res
    def add_building(self,x):
        sql="insert into buildings(name) values ('%s')" % (str(x))
        run_sql(sql,self.Scene)
        self.update_GUI(s2=self.s2)

    def get_floors_from_building(self):
        sql="select name from floors where building_belonged='%s'" % (str(self.Building))
        res=run_sql(sql,self.Scene)
        return res


    def build(self):
        self.root = Builder.load_file('kv/root.kv')
        screen = Builder.load_file('kv/add_scene.kv')
        self.root.container.add_widget(screen)

        spin1=self.root.ids['spin1']
        spinner1 = Spinner(
            text='None',
            values=(),
            size_hint=(0.9,1))
        spin1.add_widget(spinner1)
        def show_selected_scene(spinner1, text):
            self.Scene=text
            self.update_GUI(s2=self.s2)
        spinner1.bind(text=show_selected_scene)

        spin2=self.root.ids['spin2']
        spinner2 = Spinner(
            text='None',
            values=(),
            size_hint=(0.9,1))
        spin2.add_widget(spinner2)
        def show_selected_building(spinner2, text):
            self.Building=text
            self.update_GUI(s3=self.s3)
        spinner2.bind(text=show_selected_building)

        spin3=self.root.ids['spin3']
        spinner3 = Spinner(
            text='None',
            values=(),
            size_hint=(0.9,1))
        spin3.add_widget(spinner3)

        def show_selected_floor(spinner3, text):
            self.Floor=text
        spinner3.bind(text=show_selected_floor)

        spin4=self.root.ids['spin4']
        spinner4 = Spinner(
            text='Format',
            values=('csv', 'separt csv'),
            size_hint=(0.9,1))
        spin4.add_widget(spinner4)
        def show_selected_format(spinner4, text):
            self.Format=text
        spinner4.bind(text=show_selected_format)
        self.s1=spinner1
        self.s2=spinner2
        self.s3=spinner3
        self.update_GUI(spinner1)

        # add popup
        content = GridLayout(cols=1)
        content_cancel = Button(text='Cancel', size_hint_y=None, height=40)
        content.add_widget(Label(text='Please select map'))
        content.add_widget(content_cancel)
        popup = Popup(title='Error',
                      size_hint=(None, None), size=(256, 256),
                      content=content, disabled=True)
        content_cancel.bind(on_release=popup.dismiss)

        self.popup=popup
    def next_screen(self, screen):
        filename = screen + '.kv'
        Builder.unload_file('kv/' + filename)
        self.root.container.clear_widgets()
        screen = Builder.load_file('kv/' + filename)
        self.root.container.add_widget(screen)

if __name__ == '__main__':
    ClientApp().run()
