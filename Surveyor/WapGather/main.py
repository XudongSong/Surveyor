#qpy:kivy
import kivy
kivy.require('1.10.1')
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from uandroid import AndroidWifi
wifi_info=AndroidWifi()

from kivy.properties import ObjectProperty
import numpy as np
import os
from kivy.uix.popup import Popup
from kivy.uix.label import Label

import requests, json
threshold=None
appoint_ssid=None
scan_interval=0.1
host=None
port=None
selected_scene=None
class RootWidget(BoxLayout):
    root_root=ObjectProperty(None)

class ScrollViewApp(App):
    dict_ap=dict()
    set_mac=set()
    num=1
    def init_host_port(self):
        h=self.read_from_json('host')
        p=self.read_from_json('port')
        global host,port
        host=h
        port=p
        host_id=self.config_page.ids['host_id']
        port_id=self.config_page.ids['port_id']
        host_id.text=str(h)
        port_id.text=str(p)
    def write_to_json(self,data_json):
        with open('my_config.json', 'w') as f:
            f.write(json.dumps(data_json))
    def read_from_json(self,name):
        if os.path.isfile('my_config.json'):
            with open('my_config.json','r') as f:
                res=json.load(f)
                if res[name]:
                    return res[name]
                else:
                    return None
        else:
            return None
    def run_sql(self,sql,database=None):
        url = "http://"+host+":"+str(port)+"/run/sql/"
        data = {"sql":sql ,"database":database}
        headers = {"Content-Type" : "application/json"}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        return r.text

    def get_scenes(self):
        sql='select name from scenes'
        res=self.run_sql(sql,'wifi_information')
        return res

    def update_scene(self):
        id=self.config_page.ids['scene']
        scenes=self.get_scenes()
        scenes=json.loads(scenes)['result']
        if scenes:
            scenes_list=[s['name'] for s in scenes]
            id.values=scenes_list
    def update_host(self,h):
        global host
        host=h
    def update_port(self,p):
        global port
        port=p
    def connect(self):
        if port and host:
            self.update_scene()
            save_data={'host':host,'port':port}
            self.write_to_json(save_data)
    def update_selected_scene(self,s):

        global selected_scene
        selected_scene=s
    def update_threshold(self,t):
        global threshold
        threshold=t

    def update_appoint_ssid(self,a):
        global appoint_ssid
        appoint_ssid=a

    def update_scan_interval(self,s):
        global scan_interval
        scan_interval=s

    def run_install(self,_type,scene):
        #_type:
        #(1) scene
        #(2) ap
        url = "http://"+host+":"+str(port)+"/install/"
        data = {"type":_type,"name":scene}
        headers = {"Content-Type" : "application/json"}
        requests.post(url, data=json.dumps(data), headers=headers)

    def collect_ap_used(self,bssid,ssid,nickname,rss):
        url = "http://"+host+':'+str(port)+"/run/sql/"
        sql="insert into ap_used(mac,ssid,nickname,max_rss) VALUES ('%s','%s','%s',%d)" % (bssid,ssid,nickname,int(rss))

        data = {"sql":sql ,"database":selected_scene}
        headers = {"Content-Type" : "application/json"}

        r = requests.post(url, data=json.dumps(data), headers=headers)

        return r.text
    def show_wifi_scans(self,t):

        Clock.schedule_interval(self.show,float(scan_interval))
    def show(self,t):
        datas=wifi_info._get_access_points()
        for data in datas:
            ssid=data['ssid']
            bssid=data['bssid']
            level=data['level']
            if not ssid:
                continue
            if not bssid:
                continue
            if bssid not in self.set_mac:
                self.set_mac.add(bssid)
                self.dict_ap[bssid]=[ssid,level]
                self.add_item(str(bssid),str(ssid))
            else:
                if level>self.dict_ap[bssid][1]:
                    self.dict_ap[bssid]=[ssid,level]

    def submit_result(self,t):
        Clock.unschedule(self.show)
        sent_list=[]
        for i,ap in enumerate(self.set_mac):
            sent_list.append([ap,self.dict_ap[ap][0],"MAC"+str(i+1),int(self.dict_ap[ap][1])])
        sent_list=np.array(sent_list)

        if threshold:
            rss_list=[float(i) for i in sent_list[:,3]]
            rss_list=np.array(rss_list)

            sent_list=sent_list[rss_list>int(threshold)]
        if appoint_ssid:
            sent_list=sent_list[sent_list[:,1]==appoint_ssid]

        for item in sent_list:
            res=self.collect_ap_used(*(item))
        self.run_install("ap",selected_scene)

        self.popup_success.open()


    def configure(self,t):
        Clock.unschedule(self.show)
        self.next_screen('config')
    def scanning(self,t):
        Clock.unschedule(self.show)
        self.next_screen('show_screen')

    def add_item(self,ssid,mac):
        def bt(t):
            return Button(text=t,size_hint=(None,None),size=(500,50))
        self.layout.add_widget(bt(ssid))
        self.layout.add_widget(bt(mac))

    def build(self):

        self.layout=layout = GridLayout(cols=2,size_hint=(None,None),size=(1000,1500))
        layout.bind(minimum_height=layout.setter('height'))
        self.root=Builder.load_file('rootwidget.kv')

        self.show_screen=show_screen= ScrollView(size_hint=(None,None),size=(1000,1500),pos_hint={'center_x': .5, 'center_y': .5},do_scroll_x=False)
        show_screen.add_widget(layout)

        stop_config=Button(text='config',size=(500,200),font_size=50)
        stop_config.bind(on_press= self.configure)
        stop_submit_scan=Button(text='submit',size_hint=(None,None),size=(500,200),font_size=50)
        stop_submit_scan.bind(on_press=self.submit_result)

        self.foot=foot=BoxLayout(orientation='horizontal',size_hint=(None,None),size=(1000,200),pos_hint={'center_x': .5, 'center_y': .5})
        foot.add_widget(stop_config)
        foot.add_widget(stop_submit_scan)

        self.scan=scan=Button(text='scan',size_hint=(None,None),size=(500,200),pos_hint={'center_x': .5, 'center_y': .5})
        scan.bind(on_press=self.scanning)

        self.next_screen('config')

        content = GridLayout(cols=1)
        content_cancel = Button(text='Cancel', size_hint_y=None, height=100)
        content.add_widget(Label(text='Submit Success!'))
        content.add_widget(content_cancel)
        self.popup_success=popup = Popup(title='Success',
                      size_hint=(None, None), size=(666, 666),
                      content=content, disabled=True)
        content_cancel.bind(on_release=popup.dismiss)

        content1 = GridLayout(cols=1)
        content1_cancel = Button(text='Cancel', size_hint_y=None, height=100)
        content1.add_widget(Label(text='Error: AP has been selected!'))
        content1.add_widget(content1_cancel)
        self.popup_error=popup1 = Popup(title='Error',
                                         size_hint=(None, None), size=(666, 666),
                                         content=content1, disabled=True)
        content1_cancel.bind(on_release=popup1.dismiss)
        # self.root.root_root.add_widget(scan)
        # self.root.root_root.add_widget(foot)


    def next_screen(self, screen):
        if screen=='config':
            filename = 'config.kv'
            Builder.unload_file(filename)
            self.root.root_root.clear_widgets()
            self.config_page = Builder.load_file(filename)
            self.root.root_root.add_widget(self.config_page)
            self.root.root_root.add_widget(self.scan)
            self.init_host_port()
        elif screen=='show_screen':
            def check_database():
                sql='select * from ap_used;'
                res=self.run_sql(sql,selected_scene)
                res=json.loads(res)['result']
                if len(res):
                    self.popup_error.open()
                    return 0
                else :
                    return 1
            if not check_database():
                self.next_screen('config')

            self.root.root_root.clear_widgets()
            self.root.root_root.add_widget(self.show_screen)
            self.root.root_root.add_widget(self.foot)
            self.show_wifi_scans(1)

if __name__ == '__main__':

    ScrollViewApp().run()
