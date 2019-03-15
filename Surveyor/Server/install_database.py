from mysqlhelper import UserModel
model=UserModel()

def Install_database_configuration():
    model.run('create database wifi_information')
    model.run('create table if not exists users(id int unsigned primary key auto_increment,name varchar(40) not null unique,password varchar(40) not null)','wifi_information')
    model.run('create table if not exists scenes(id int unsigned primary key auto_increment,name varchar(40) not null unique);','wifi_information')
def Install_scene(name):
    model.run('create database '+str(name))
    model.run('create table buildings(id int unsigned primary key auto_increment, name varchar(40))',str(name))
    model.run('create table floors(id int unsigned primary key auto_increment, name varchar(40) not null,building_belonged varchar(40) not null,map_width_pix int unsigned not null, map_heigh_pix int unsigned not null,map_width_m int unsigned not null, map_heigh_m int unsigned not null)',str(name))
    model.run('create table ap_used(id int unsigned primary key auto_increment, mac varchar(100) not null unique,ssid varchar(100) not null,nickname varchar(100) not null unique,max_rss int not null)',str(name))
#
    model.run('create table fingerprints(id int unsigned primary key auto_increment, pos_x float not null, pos_y float not null, floor_name varchar(40) not null, building_name varchar(40) not null,user_name varchar(40),phone_type varchar(40),createtime datetime NULL DEFAULT CURRENT_TIMESTAMP )',str(name))

def add_ap_used_to_scene(name):
    ap_count=model.run('select nickname from ap_used order by id desc',str(name))
    for i in ap_count:
        model.run("alter table fingerprints add "+str(i['nickname'])+" int default 100 after id;",str(name))

# model.run("insert into fingerprints(pos_x,pos_y,floor_id,building_id,user_name,phone_type) VALUES (10,20,3,1,'xudong','huawei')",'wifi_scenes_1')

# model.run('alter table fingerprints add mac1 tinyint default 0 after id;','wifi_scenes_1')

# model.run("insert into ap_used(mac,ssid,nickname) VALUES ('11:22:33:11:22:33','home','mac1')",'wifi_scenes_1')
# model.run("insert into ap_used(mac,ssid,nickname) VALUES ('22:22:33:11:22:33','home','mac2')",'wifi_scenes_1')
# model.run("insert into ap_used(mac,ssid,nickname) VALUES ('33:22:33:11:22:33','home','mac3')",'wifi_scenes_1')


