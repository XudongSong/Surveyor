
from kivy.app import App
from kivy.uix.scatterlayout import ScatterPlane
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.graphics import Color, Ellipse,Line
from uandroid import AndroidWifi
import requests,json
import os

wifi_info=AndroidWifi()

Scene="None"
Building="None"
Floor="None"
host="None"
port="None"
Grid_length=5.0

def run_sql(sql,database=None):
    url = "http://"+host+":"+str(port)+"/run/sql/"
    data = {"sql":sql ,"database":database}
    headers = {"Content-Type" : "application/json"}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r.text
def logInfo(s):
    url="http://"+host+":"+str(port)+"/log/"
    data={"info":s}
    headers = {"Content-Type":"application/json"}
    r=requests.post(url,data=json.dumps(data),headers=headers)
    return r.text
class Scatter2(ScatterPlane):
    def __init__(self):
        super(Scatter2,self).__init__()
        self.position_now=None
        self.floor=Image(allow_stretch=True)
        self.floor.auto_bring_to_front=False
        self.do_rotation=False
        self.Grid_length=Grid_length

        self.android_screen_size=(1080,1920)
        self.proportion=None
    def download(self,scene='s1',building="b1",floor="f1"):
        url="http://"+host+':'+port+"/download/"
        floor_name=floor+'.jpg'
        data={"scene":scene,"building":building,"floor":floor_name}
        path=os.path.join('storage', 'emulated', '0')
        save_path=os.path.join(path,'map')
        save_path=os.path.join(save_path,scene)
        save_path=os.path.join(save_path,building)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file_name=os.path.join(save_path,floor_name)
        if not os.path.isfile(floor_name):
            with open(file_name, 'wb') as file:
                html = requests.post(url,data=data)
                file.write(html.content)
    def update_floor_map(self,floor_to_download):
        s=Scene
        b=Building
        self.download(s,b,floor_to_download)

    def show_floor(self,floor_name):

        self.clear_widgets()
        source_floor,size_floor=self.floorManagement(floor_name)
        if not os.path.isfile(source_floor):
            self.update_floor_map(floor_name)
        self.floor.source,self.floor.size=source_floor,size_floor
        self.anchor=Image(source='anchor.png')
        self.add_widget(self.floor)
        self.add_widget(self.anchor)
        sql="select pos_x,pos_y from fingerprints where building_name='%s' and floor_name='%s'"% (str(Building),str(floor_name))
        pots=json.loads(run_sql(sql,Scene))['result']
        self.draw_grid(float(self.Grid_length))
        for p in pots:
            x=p['pos_x']/self.proportion
            y=p['pos_y']/self.proportion
            self.draw_pot(x,y)

    def floorManagement(self,floor_name=None):
        path=os.path.join('storage', 'emulated', '0')
        floor_path=os.path.join(path,'map')
        floor_path=os.path.join(floor_path,Scene)
        floor_path=os.path.join(floor_path,Building)
        picture_name=floor_name+'.jpg'
        floor_path=os.path.join(floor_path,picture_name)
        sql="select map_width_pix,map_heigh_pix,map_width_m,map_heigh_m from floors where building_belonged='%s' and name='%s';"%(Building,Floor)
        res=json.loads(run_sql(sql,Scene))['result'][0]
        self.width_pix=width_pix=res['map_width_pix']
        self.heigh_pix=heigh_pix=res['map_heigh_pix']
        width_m=res['map_width_m']
        heigh_m=res['map_heigh_m']
        self.proportion=float(width_m)/float(width_pix)
        size=(width_pix,heigh_pix)
        return floor_path,size

    def on_touch_down(self, touch):
        self.touchDown = self.to_widget(touch.x, touch.y)
        anchor=self.anchor
        anchor.size=(self.android_screen_size[0]*0.04,self.android_screen_size[1]*0.04)
        if (self.touchDown[0]>0 and self.touchDown[1]>0 and self.touchDown[0]<self.floor.size[0] and self.touchDown[1]<self.floor.size[1]):
            anchor.pos=(self.touchDown[0]-anchor.size[0]/2,self.touchDown[1]-anchor.size[1]/2)
            self.position_now=self.touchDown
        return super(Scatter2, self).on_touch_down(touch)

    # def on_touch_move(self, touch):
    #     self.touchDown = self.to_widget(touch.x, touch.y)
    #     anchor=self.anchor
    #     anchor.size=(self.android_screen_size[0]*0.04,self.android_screen_size[1]*0.04)
    #     if (self.touchDown[0]>0 and self.touchDown[1]>0 and self.touchDown[0]<self.floor.size[0] and self.touchDown[1]<self.floor.size[1]):
    #         anchor.pos=(self.touchDown[0]-anchor.size[0]/2,self.touchDown[1]-anchor.size[1]/2)
    #         self.position_now=self.touchDown
    #     return super(Scatter2, self).on_touch_move(touch)

    def draw_line(self,start_pos,end_pos):
        with self.canvas:
            Color(0,1,0)
            Line(points=(start_pos[0],start_pos[1],end_pos[0],end_pos[1]),width=2)

    def draw_grid(self,grid_lenth_m):
        grid_lenth_pix=grid_lenth_m/self.proportion
        x_num=int(self.width_pix/grid_lenth_pix)+1
        y_num=int(self.heigh_pix/grid_lenth_pix)+1
        for col in range(x_num):
            self.draw_line((col*grid_lenth_pix,0),(col*grid_lenth_pix,self.heigh_pix))
        for row in range(y_num):
            self.draw_line((0,row*grid_lenth_pix),(self.width_pix,row*grid_lenth_pix))

    def draw_pot(self,x,y):
        with self.canvas:
            Color(0, 0, 1)
            d = 7.
            Ellipse(pos=(x - d / 2, y - d / 2), size=(d, d))
class config_widget(GridLayout):
    Builder.load_file("Plano2.kv")

class PlanoApp(App):

    def start_survey(self):
        global Grid_length
        grid_id=self.config_page.ids['grid_id']
        Grid_length=float(grid_id.text)

        ap_used=json.loads(run_sql('select mac,nickname from ap_used',Scene))['result']
        #ap_used=set(ap_used)
        ap_used_mac=[ap['mac'] for ap in ap_used]
        self.ap_used_mac=set(ap_used_mac)
        self.ap_used_mac_nickname={ap['mac']:ap['nickname'] for ap in ap_used}

        self.update_map()
        self.next_screen('show_screen')
        self.spinner_building.values=self.building_list
    #
    # def download(self,scene='s1',building="b1",floor="f1"):
    #     url="http://"+host+':'+port+"/download/"
    #     floor_name=floor+'.jpg'
    #     data={"scene":scene,"building":building,"floor":floor_name}
    #     path=os.path.join('storage', 'emulated', '0')
    #     save_path=os.path.join(path,'map')
    #     save_path=os.path.join(save_path,scene)
    #     save_path=os.path.join(save_path,building)
    #     if not os.path.exists(save_path):
    #         os.makedirs(save_path)
    #     file_name=os.path.join(save_path,floor_name)
    #     if not os.path.isfile(floor_name):
    #         with open(file_name, 'wb') as file:
    #             html = requests.post(url,data=data)
    #             file.write(html.content)
    # def update_floor_map(self,floor_to_download):
    #     s=Scene
    #     b=Building
    #     self.download(s,b,floor_to_download)
    #
    def update_map(self):
        s=Scene
        self.building_list=buindings_list=[item['name'] for item in json.loads(self.get_buildings(s))['result']]
        # for b in buindings_list:
        #     floor_list=[item['name'] for item in json.loads(self.get_floors(scene=s,building=b))['result']]
        #     for f in floor_list:
        #         self.download(s,b,f)

    def init_host_port(self):
        h=self.read_from_json('host')
        p=self.read_from_json('port')
        g=self.read_from_json('grid_length')
        global host,port,Grid_length
        host=h
        port=p
        Grid_length=g

        host_id=self.config_page.ids['host_id']
        port_id=self.config_page.ids['port_id']
        host_id.text=str(h)
        port_id.text=str(p)
        grid_id=self.config_page.ids['grid_id']
        grid_id.text=str(g)


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

    def get_scenes(self):
        sql='select name from scenes'
        res=run_sql(sql,'wifi_information')
        return res

    def get_buildings(self,scene):
        sql="select name from buildings"
        res=run_sql(sql,scene)
        return res

    def get_floors(self,scene,building):
        sql="select name from floors where building_belonged='%s'"% (str(building))
        res=run_sql(sql,scene)
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

    def update_grid_length(self,g):
        global Grid_length
        Grid_length=g

    def connect(self):
        global host,port
        host_id=self.config_page.ids['host_id']
        port_id=self.config_page.ids['port_id']
        host=host_id.text
        port=port_id.text


        if port and host and Grid_length:
            self.update_scene()
            save_data={'host':host,'port':port,'grid_length':Grid_length}
            self.write_to_json(save_data)

    def update_selected_scene(self,s):
        global Scene
        Scene=s

    def next_screen(self, screen):
        global Floor,Building,Scene
        if screen=='config':
            Floor=None
            Building=None
            Scene=None
            self.page.clear_widgets()
            self.config_page=config_widget()
            self.page.add_widget(self.config_page)
            self.init_host_port()
            del self.parent
            return self.page
        elif screen=='show_screen':
            self.init_m()
            self.page.clear_widgets()
            self.page.add_widget(self.back)
            return self.page

    def init_m(self):
        self.parent=parent= Scatter2()

        self.spinner_floor=spinner_floor = Spinner(
            text='Floor',
            background_color=[0,0,1,0.9],
            values=(),
            size_hint=(None,None),
            size=(200, 100),
            pos_hint={'x': 0, 'y': 0})

        self.spinner_building=spinner_building = Spinner(
            text='Building',
            background_color=[0,0,1,0.9],
            values=(),
            # just for positioning in our example
            size_hint=(None,None),
            size=(200, 100),
            pos=(250,0))

        self.config_button=Button(
            text='Config',
            background_color=[1,0,0,0.9],
            size_hint=(None,None),
            size=(200,100),
            pos=(500,0))

        def config_page(instance):
            return self.next_screen('config')
        self.config_button.bind(on_press=config_page)

        self.collect_button=collect_button=Button(
            text='Collect',
            background_color=[1,0,0,0.9],
            size_hint=(None,None),
            size=(200,100),
            pos_hint={'right':1,'y':0})

        def collect_wifi_info(instance):
            datas=wifi_info._get_access_points()
            # logInfo("wifi_info:"+str(datas))
            collected_mac_rss={}
            for d in datas:
                bssid=d['bssid']
                level=d['level']
                try:
                    bssid=str(bssid,encoding='utf-8')
                except:
                    bssid=bssid
                collected_mac_rss[bssid]=level
            position_now_m=(parent.position_now[0]*parent.proportion,parent.position_now[1]*parent.proportion)

            sent_mac_rss={}
            now_mac=[]
            for mac in collected_mac_rss:
                if mac in self.ap_used_mac:
                    now_mac.append(mac)
                    sent_mac_rss[mac]=collected_mac_rss[mac]
            now_nickname=[self.ap_used_mac_nickname[mac] for mac in now_mac]
            now_level=[sent_mac_rss[mac] for mac in now_mac]

            now_level=list(map(str,now_level))
            sql="insert into fingerprints(pos_x,pos_y,floor_name,building_name,user_name,phone_type,%s) VALUES (%s,%s,'%s','%s','root','unknow',%s)"%(','.join(now_nickname),str(position_now_m[0]),str(position_now_m[1]),Floor,Building,','.join(now_level))
            res=run_sql(sql,Scene)
            if res!="0":
                parent.draw_pot(parent.position_now[0],parent.position_now[1])

        collect_button.bind(on_press=collect_wifi_info)

        def show_selected_value(spinner_floor,text):
            global Floor
            Floor=text
            parent.show_floor(text)
        spinner_floor.bind(text=show_selected_value)

        def show_selected_value_building(spinner_building,text):
            global Building
            Building=text
            self.floor_list=[item['name'] for item in json.loads(self.get_floors(scene=Scene,building=Building))['result']]
            self.spinner_floor.values=self.floor_list
        spinner_building.bind(text=show_selected_value_building)

        self.back=back=FloatLayout()
        # self.page.add_widget(self.back)
        back.add_widget(self.parent)
        back.add_widget(self.spinner_floor)
        back.add_widget(self.spinner_building)
        back.add_widget(self.config_button)
        back.add_widget(self.collect_button)

    def build(self):
        self.init_m()
        self.page=BoxLayout()
        return self.next_screen('config')

if __name__ == "__main__":
    PlanoApp().run()
