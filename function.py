import winreg
from datetime import datetime, timedelta
import LnkParse3
import os

def raw_to_time(raw_data):
    value = int.from_bytes(raw_data, 'little')#리틀 엔디언으로
    dt = datetime(1601, 1, 1)+timedelta(microseconds=value//10)#단위는 100나노세컨->마이크로세컨
    return dt+timedelta(hours=9)#한국시간 보정
 
def get_user_path():
    users_base_path = r"C:\Users"
    if not os.path.exists(users_base_path):
        return None
    
    # Public, Default 같은 시스템 폴더는 거르고 실제 계정 폴더만 찾음
    for user_name in os.listdir(users_base_path):
        user_path = os.path.join(users_base_path, user_name)
        if os.path.isdir(user_path) and user_name not in ['Public', 'Default', 'Default User', 'All Users', 'desktop.ini']:
            return user_path
    return None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_PATH = os.path.join(LOG_DIR, "usb_report.txt")
def fix_encoding(text):
    if not text: return text
    try:
        # 1. Windows 기본 서구권 인코딩(cp1252)으로 되돌린 뒤 UTF-8로 재해석
        return text.encode('cp1252').decode('utf-8')
    except:
        try:
            # 2. 1번이 안 되면 latin-1 시도
            return text.encode('latin-1').decode('utf-8')
        except:
            # 3. 둘 다 안 되면 그냥 포기하고 원본 반환
            return text
def usbstor(f):
    result = []

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Enum\USBSTOR", 0, winreg.KEY_READ) as keypath:
            count = winreg.QueryInfoKey(keypath)[0]
            for i in range(count):
                device_name = winreg.EnumKey(keypath, i)
                f.write(f"[*]장치 이름: {device_name}\n")
                path2 = r"SYSTEM\CurrentControlSet\Enum\USBSTOR\\"+device_name
                item = {}
                                    
                parts = device_name.split("&")
                info = {}
                for part in parts:
                    if '_' in part:
                        key, value = part.split('_', 1)
                        info[key] = value.replace('_', ' ')
                f.write(f"제조사: {info.get('Ven')}, ")
                f.write(f"모델명: {info.get('Prod')}, ")
                f.write(f"버전: {info.get('Rev')}\n")
                
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path2, 0, winreg.KEY_READ) as keypath2:
                        serial_num = winreg.EnumKey(keypath2, 0)
                        wpd_path = r"SOFTWARE\Microsoft\Windows Portable Devices\Devices"
                        friendly_name = "이름 없음"
                        try:
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, wpd_path, 0, winreg.KEY_READ) as k_wpd:   
                                w_count = winreg.QueryInfoKey(k_wpd)[0]
                                for j in range(w_count): 
                                    wpd_device_name = winreg.EnumKey(k_wpd, j)
                                    if serial_num.lower() in wpd_device_name.lower():
                                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, wpd_path+"\\"+wpd_device_name, 0, winreg.KEY_READ) as friendly_path:
                                            friendly_name, _  = winreg.QueryValueEx(friendly_path, "FriendlyName")
                        except:pass
                        f.write(f"FriendlyName: {friendly_name}\n")
                        f.write(f"시리얼: {serial_num}\n")
                        item = {"vendor": info.get('Ven'),
                        "name": info.get('Prod'),
                        "version": info.get('Rev'),
                        "friendlyname": friendly_name,
                        "serial": serial_num,
                       }
                
                        try:
                            path3 = path2+"\\"+serial_num+"\\Properties\\{83da6326-97a6-4088-9453-a1923f573b29}"
                            try:
                                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path3+"\\0064", 0, winreg.KEY_READ) as keypath_64:
                                    raw_data, data_type = winreg.QueryValueEx(keypath_64, "")
                                    f.write(f"최초 설치 시간:{raw_to_time(raw_data)}\n")
                                    item["first_install"]= raw_to_time(raw_data)
                            except:
                                item["first_install"]= None
                                f.write("최초 설치: 기록 없음\n")  
                            try: 
                                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path3+"\\0066", 0, winreg.KEY_READ) as keypath_66:
                                    raw_data, data_type = winreg.QueryValueEx(keypath_66, "")
                                    f.write(f"마지막 연결 시간:{raw_to_time(raw_data)}\n")
                                    item["last_connect"]=raw_to_time(raw_data)
                            except:
                                item["last_connect"]=None
                                f.write("마지막 연결: 기록 없음\n")
                            try: 
                                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path3+"\\0067", 0, winreg.KEY_READ) as keypath_67:
                                    raw_data, data_type = winreg.QueryValueEx(keypath_67, "")
                                    f.write(f"마지막 제거 시간:{raw_to_time(raw_data)}\n\n")
                                    item["last_removed"] = raw_to_time(raw_data)
                            except:
                                item["last_removed"]=None
                                f.write("마지막 제거: 기록 없음\n\n")
                        except Exception as err:
                            f.write(str(err)+"\n")
                except Exception as err:
                    f.write(str(err)+"\n")
                result.append(item)
        result.sort(key=lambda x: x.get("first_install") or datetime.datetime.min, reverse=True)

                
    except Exception as err:
        f.write(str(err)+"\n") 
    return result  
def lnk_parser():
    users_base_path = r"C:\Users"
    lnk_list = []

    if not os.path.exists(users_base_path):
        return lnk_list

    # 모든 사용자를 뒤져야 continue가 작동함
    for user_name in os.listdir(users_base_path):
        user_path = os.path.join(users_base_path, user_name)
        if not os.path.isdir(user_path) or user_name in ['Public', 'Default', 'Default User', 'All Users', 'desktop.ini']:
            continue

        recent_path = os.path.join(user_path, r"AppData\Roaming\Microsoft\Windows\Recent")
        if not os.path.exists(recent_path):
            continue

        for file in os.listdir(recent_path):
            if file.endswith('.lnk'):
                lnk_path = os.path.join(recent_path, file)
                try:
                    with open(lnk_path, 'rb') as indata:
                        lnk = LnkParse3.lnk_file(indata)
                        json_data = lnk.get_json()
                        f_path = None
                        
                        link_info = json_data.get('link_info', {})
                        if link_info.get('local_base_path'):
                            f_path = fix_encoding(link_info['local_base_path'])
                            
                        if not f_path:
                            data_info = json_data.get('data', {})
                            rel_path = data_info.get('relative_path')
                            if rel_path:
                                f_path = os.path.normpath(os.path.join(recent_path, fix_encoding(rel_path)))
                                
                        stat_info = os.stat(lnk_path)
                        time = datetime.fromtimestamp(stat_info.st_ctime)
                        lnk_list.append({"user": user_name, "name": file, "time": time, "path": f_path})

                except:
                    continue
    lnk_list.sort(key=lambda x: x.get("time") or datetime.datetime.min, reverse=True)
              
    return lnk_list


    
    
                
                    
                   
        


