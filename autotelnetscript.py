"""Chuong trinh dung de chay lenh telnet tu dong cho nhieu thiet bi"""
from telnetlib import Telnet
import time
import json
import os
import socket
import logging


def run_cmd(telnet, cmd, end, success, timeout=1):
    """chay lenh, kiem tra va tra ve ket qua
    telnet : Telnet Obj
    command : lenh can thuc hien (str)
    end_point : diem dung khi dung read_until (str)
    check_point : dieu kien kiem tra xem lenh co thanh cong khong (str)
    timeout : thoi gian cho doc du lieu (int)
    Ket qua tra ve se la dang tuple:
        Neu end_point == "" (chuoi rong): True + b""
        Neu thanh cong: True + noi dung doc duoc (byte)
        Neu that bai: False + noi dung doc duoc (byte)"""

    # Thuc thi lenh
    telnet.write(cmd.encode("ascii") + b"\n")

    # Khong can kiem tra
    if not end:
        time.sleep(timeout)
        return True, b""

    # Kiem tra
    result = telnet.read_until(end.encode("ascii"), timeout)
    if success.encode("ascii") in result:
        return True, result
    else:
        return False, result


def main():
    # Bien mac dinh
    cwd = os.getcwd()
    cmd_dir = "commands"
    host_dir = "hosts"
    # File chua du lieu cac IP can cau hinh
    print("Ten tap tin chua cac IP muon cau hinh, Enter de dung mac dinh ...")
    hosts_f = input("Filename (Mac dinh: hosts.json): ") or "hosts.json"
    os.path.exists(os.path.join(cwd, cmd_dir, hosts_f))
    # File chua du lieu cac cau lenh can thuc hien
    print("Ten tap tin chua cac lenh muon su dung, Enter de dung mac dinh ...")
    commands_f = input(
        "File name (Mac dinh: commands.json): ") or "commands.json"
    os.path.exists(os.path.join(cwd, host_dir, commands_f))

    # Port telnet de ket noi den
    print("Port dung de ket noi Telnet, Enter de dung mac dinh ...")
    telnet_port = int(input("Port (Mac dinh: 23) :") or 23)
    # Thoi gian timeout khi ket noi
    print("Thoi gian cho thiet bi ket noi, Enter de dung mac dinh ...")
    telnet_timeout = int(input("Timeout (Mac dinh: 15s) :") or 15)
    # Thoi gian cho giua cac giai doan quan trong
    print("Thoi gian cho giua cac qua trinh quan trong\n"
          "\t- VD1: Dang nhap xong thi cho de chay lenh dau tien\n"
          "\t- VD2: Lenh cuoi cung truoc khi chuyen qua thiet bi khac\n"
          "Mac dinh la 2s")
    delay = int(input("Delay: ") or "2")

    # Lay danh sach cac IP thiet bi
    with open(os.path.join(cwd, hosts_f)) as json_f:
        hosts: list = json.load(json_f)

    # Lay danh sach cac cau lenh can thuc hien
    with open(os.path.join(cwd, commands_f)) as json_f:
        commands: list = json.load(json_f)

    # Danh sach cac IP gap su co khi cau hinh
    fails = []
    # Danh sach cac IP da cau hinh hoan tat
    successes = []

    for host in hosts:
        print("===***===")
        print(f'Chuan bi cau hinh "{host}"')
        try:
            tn = Telnet(host, telnet_port, telnet_timeout)
            time.sleep(delay)
        except (socket.timeout, OSError):
            logging.warning("Khong the ket noi den thiet bi")
            fails.append(host)
            print("Chuan bi chuyen den thiet bi tiep theo")
            continue

        for command_info in commands:
            # command_info: dict : "cmd", "end", "success", "timeout"
            cmd = command_info["cmd"]
            end = command_info["end"]
            success = command_info["success"]
            timeout = command_info["timeout"]

            print(f'Chay lenh "{cmd}"')
            result, content = run_cmd(tn, cmd, end, success, timeout)

            if result:
                print("Lenh da thuc hien thanh cong")
            else:
                logging.warning("Co loi phat sinh khi thuc hien lenh")
                logging.debug(content.decode("ascii"))
                print("Chuan bi chuyen qua thiet bi khac")
                fails.append(host)
                break
        else:
            print("Da hoan tat cau hinh thiet bi")
            print("Chuan bi chuyen qua thiet bi khac")
            successes.append(host)

        time.sleep(delay)
        tn.close()

    # In ket qua
    print("===***===")
    print("Cac host cau hinh thanh cong:")
    for host in successes:
        print("\t", host)
    print("Cac host gap loi khi cau hinh:")
    for host in fails:
        print("\t", host)


if __name__ == "__main__":
    main()
    input("Press Enter to Quit!")
