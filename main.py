import function
import datetime
import csv

def main():
    LOG_PATH = function.LOG_PATH
    usbstor = function.usbstor
    lnk_parser = function.lnk_parser
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        usb_data = usbstor(f)
        lnk_data = lnk_parser()
        if usb_data:#최초 설치 시간을 기준으로 오름차순 정렬
            usb_data.sort(key=lambda x: x.get("first_install") or datetime.datetime.min, reverse=True)
            CSV_PATH = LOG_PATH.replace('.txt', '.csv')
            
            with open(CSV_PATH, 'w', newline='', encoding='utf-8-sig') as g:
                fieldnames = usb_data[0].keys()
                    
                writer = csv.DictWriter(g, fieldnames=fieldnames)
                    
                writer.writeheader()
                writer.writerows(usb_data)
            
        if lnk_data:#시간을 기준으로 오름차순 정렬
            lnk_data.sort(key=lambda x: x.get("time") or datetime.datetime.min, reverse=True)
            CSV_PATH = LOG_PATH.replace('.txt', '_recent.csv')
            
            with open(CSV_PATH, 'w', newline='', encoding='utf-8-sig') as g:
                fieldnames = lnk_data[0].keys()
                    
                writer = csv.DictWriter(g, fieldnames=fieldnames)
                    
                writer.writeheader()
                writer.writerows(lnk_data)
        
       
                    
                        
                    
            


