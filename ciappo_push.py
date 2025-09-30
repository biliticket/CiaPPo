import httpx
from loguru import logger
import questionary


def push_gotify(url, token, message):
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    data = {
        "message": message
    }
    try:
        with httpx.Client(base_url=url, follow_redirects=True) as client:
            response = client.post("/message", headers=headers, json=data)
            response.raise_for_status()
            logger.debug(response.json())
            return True
    except httpx.HTTPStatusError:
        return False
    except Exception as e:
        logger.debug(e)
        return False


def ob11_push(url, token, send_type, send_target, message):
    headers = {"Content-Type": "application/json"}
    if token is not None and token != "":
        headers["Authorization"] = "Bearer " + token
    if send_type not in ["private", "group"]:
        return False
    data = {
        f"{'user' if send_type == 'private' else 'group'}_id": send_target,
        "message": [
            {"type": "text", "data": {"text": message}}
        ],
    }
    try:
        with httpx.Client(base_url=url, follow_redirects=True) as client:
            response = client.post(f"/send_{send_type}_msg", headers=headers, json=data)
            response.raise_for_status()
            logger.debug(response.json())
            return True if response.json()["retcode"] == 0 else False
    except httpx.HTTPStatusError:
        return False
    except Exception as e:
        logger.debug(e)
        return False


def push_bark(url, key, message, enhanced=False):
    headers = {"Content-Type": "application/json"}
    data = {
        "body": message,
        "title": "【CiaPPo】锁票成功，尽快支付",
        "device_key": key
    }
    if enhanced:
        data["level"] = "critical"
        data["call"] = "1"
        data["volume"] = 10
    try:
        with httpx.Client(base_url=url, follow_redirects=True) as client:
            response = client.post("/push", headers=headers, json=data)
            logger.debug(response.json())
            return True
    except httpx.HTTPStatusError:
        return False
    except Exception as e:
        logger.debug(e)
        return False


def push_ntfy(url, key, title, message):
    headers = {"Content-Type": "application/json"}
    data = {
        "topic": key,
        "message": title,
        "title": message,
        "tags": ["tada", "loudspeaker"],
        "priority": 5
    }
    try:
        with httpx.Client(base_url=url, follow_redirects=True) as client:
            response = client.post("/", headers=headers, json=data)
            logger.debug(response.json())
            return True
    except httpx.HTTPStatusError:
        return False
    except Exception as e:
        logger.debug(e)
        return False


def desktop_notify(title, message, need_sound, sound_path):
    try:
        from notifypy import Notify

        notification = Notify()
        notification.title = title
        notification.message = message
        notification.send()
        if need_sound:
            try:
                from playsound3 import playsound

                logger.debug(f"playing sound...")
                playsound(sound=sound_path, block=False)
            except:
                logger.warning("playsound failed")
        return True
    except BaseException as e:
        logger.debug(e)
        return False


def push_pushplus(token, message, content):
    headers = {"Content-Type": "application/json"}
    data = {
        "token": token,
        "title": message,
        "content": content,
    }
    try:
        response = httpx.post(
            "http://www.pushplus.plus/send", headers=headers, json=data
        )
        response.raise_for_status()
        logger.debug(response.json())
        return True if response.json()["code"] == 200 else False
    except httpx.HTTPStatusError:
        return False
    except Exception as e:
        logger.debug(e)
        return False


def push_server_chan(send_key: str, message, content):
    import re

    if send_key.startswith("sctp"):
        match = re.match(r"sctp(\d+)t", send_key)
        if match:
            num = match.group(1)
            url = f"https://{num}.push.ft07.com/send/{send_key}.send"
        else:
            raise ValueError("Invalid sendkey format for sctp")
    else:
        url = f"https://sctapi.ftqq.com/{send_key}.send"
    params = {
        "title": message,
        "desp": content,
    }
    try:
        response = httpx.get(url, params=params)
        response.raise_for_status()
        logger.debug(response.json())
        return True if response.json()["code"] == 0 else False
    except httpx.HTTPStatusError:
        return False
    except Exception as e:
        logger.debug(e)
        return False


def do_push(
    push_config,
    order_id,
    ticket_name,
    buyer_name,
    username
):
    success = True
    for push_type in push_config["push_actions"]:
        if push_type == "gotify":
            if not push_gotify(
                push_config["gotify"]["server"],
                push_config["gotify"]["token"],
                f"【CiaPPo】锁票成功，尽快支付，点击跳转\n票名: {ticket_name}\n购票人: {buyer_name}\n用户: {username}\n订单ID: {order_id}"
            ):
                success = False
        elif push_type == "ob11":
            if not ob11_push(
                push_config["ob11"]["server"],
                push_config["ob11"]["token"],
                push_config["ob11"]["send_type"],
                push_config["ob11"]["send_target"],
                f"【CiaPPo】锁票成功，尽快支付。\n票名: {ticket_name}\n购票人: {buyer_name}\n用户: {username}\n订单ID: {order_id}",
            ):
                success = False
        elif push_type == "bark":
            if not push_bark(
                push_config["bark"]["server"],
                push_config["bark"]["key"],
                f"【CiaPPo】锁票成功，尽快支付，点击跳转\n票名: {ticket_name}\n购票人: {buyer_name}\n用户: {username}\n订单ID: {order_id}",
                push_config["bark"]["enhanced"],
            ):
                success = False
        elif push_type == "desktop_notify":
            if len(ticket_name) > 45:
                ticket_name = ticket_name[:12] + "..." + ticket_name[-30:]
            if not desktop_notify(
                f"【CiaPPo】锁票成功，尽快支付。",
                f"票名: {ticket_name}\n购票人: {buyer_name} 用户: {username}\n订单ID: {order_id}",
                push_config["desktop_notify"]["need_sound"],
                push_config["desktop_notify"]["sound_path"],
            ):
                success = False
        elif push_type == "pushplus":
            if not push_pushplus(
                push_config["pushplus"]["token"],
                f"【CiaPPo】锁票成功，尽快支付。",
                f"票名: {ticket_name}\n购票人: {buyer_name}\n用户: {username}\n订单ID：{order_id}",
            ):
                success = False
        elif push_type == "server_chan":
            if not push_server_chan(
                push_config["server_chan"]["send_key"],
                f"【CiaPPo】锁票成功，尽快支付。",
                f"票名: {ticket_name}\n购票人: {buyer_name}\n用户: {username}\n订单ID：{order_id}",
            ):
                success = False
        elif push_type == "ntfy":
            if not push_ntfy(
                push_config["ntfy"]["server"],
                push_config["ntfy"]["topic"],
                f"【CiaPPo】锁票成功，尽快支付。",
                f"票名: {ticket_name}\n购票人: {buyer_name}\n用户: {username}\n订单ID: {order_id}"
            ):
                success = False
        elif push_type == "run_command":
            import subprocess

            try:
                command = push_config["run_command"]["command"]
                command = command.replace("ORDER_ID", order_id)
                command = command.replace("TICKET_NAME", ticket_name)
                command = command.replace("BUYER_NAME", buyer_name)
                command = command.replace("USERNAME", username)
                logger.debug(f"run command: {command}")
                subprocess.run(command)
            except Exception as e:
                logger.debug(e)
                success = False

    return success

def configure_push_config():
    actions = questionary.checkbox(
        "Select push methods (use space to select, enter to confirm, leave empty to disable):",
        choices=[
            "Gotify",
            "OneBot11",
            "Bark",
            "Ntfy",
            "Desktop Notify",
            "PushPlus",
            "ServerChan",
            "Run Command",
        ],
    ).ask()
    if actions is None:
        logger.info("Disabled push")
        return {
            "push_actions": []
        }
    push_config = {"push_actions": []}
    if "Gotify" in actions:
        push_config["push_actions"].append("gotify")
        gotify_config = {}
        gotify_config["server"] = questionary.text(
            "Gotify server:",
            validate=lambda text: (
                text.startswith("http://")
                or text.startswith("https://")
            )
            and text.count("/") == 2,
        ).ask()
        gotify_config["token"] = questionary.text(
            "Gotify token:"
        ).ask()
        if (
            gotify_config["server"] == None
            or gotify_config["token"] == None
        ):
            push_config["push_actions"].remove("gotify")
            logger.info("Canceled")
            return {
                "push_actions": []
            }
        push_config["gotify"] = gotify_config
    if "OneBot11" in actions:
        push_config["push_actions"].append("ob11")
        ob11_config = {}
        ob11_config["server"] = questionary.text(
            "OneBot11 server:",
            validate=lambda text: (
                text.startswith("http://")
                or text.startswith("https://")
            )
            and text.count("/") == 2,
        ).ask()
        ob11_config["token"] = questionary.text(
            "OneBot11 token:"
        ).ask()
        ob11_config["send_type"] = questionary.select(
            "OneBot11 send type:",
            choices=[
                "Private Message",
                "Group Message",
            ],
        ).ask()
        if ob11_config["send_type"] == "Private Message":
            ob11_config["send_type"] = "private"
        elif ob11_config["send_type"] == "Group Message":
            ob11_config["send_type"] = "group"
        else:
            logger.error("Invalid send type")
            return {
                "push_actions": []
            }
        ob11_config["send_target"] = questionary.text(
            "OneBot11 send target:",
            validate=lambda text: text.isdigit(),
        ).ask()
        ob11_config["send_target"] = int(ob11_config["send_target"])
        if (
            ob11_config["send_target"] == None
            or ob11_config["token"] == None
            or ob11_config["server"] == None
        ):
            push_config["push_actions"].remove("ob11")
            logger.info("Canceled")
            return {
                "push_actions": []
            }
        push_config["ob11"] = ob11_config
    if "Bark" in actions:
        push_config["push_actions"].append("bark")
        bark_config = {}
        default_server = "https://api.day.app"
        bark_config["server"] = questionary.text(
            "Bark server:",
            default=default_server,
            validate=lambda text: (
                text.startswith("http://")
                or text.startswith("https://")
            )
            and text.count("/") == 2,
        ).ask()
        bark_config["key"] = questionary.text(
            "Bark key:",
            validate=lambda text: text.count("/") == 0,
        ).ask()
        bark_config["enhanced"] = questionary.confirm(
            "Bark enhanced mode (critical level, sound, etc.)?",
        ).ask()
        if (
            bark_config["key"] == None
            or bark_config["server"] == None
            or bark_config["enhanced"] == None
        ):
            push_config["push_actions"].remove("bark")
            logger.info("Canceled")
            return {
                "push_actions": []
            }
        push_config["bark"] = bark_config
    if "Ntfy" in actions:
        push_config["push_actions"].append("ntfy")
        ntfy_config = {}
        default_server = "https://ntfy.sh"
        ntfy_config["server"] = questionary.text(
            "Ntfy server:",
            default=default_server,
            validate=lambda text: (
                text.startswith("http://")
                or text.startswith("https://")
            )
            and text.count("/") == 2,
        ).ask()
        ntfy_config["topic"] = questionary.text(
            "Ntfy topic:"
        ).ask()
        if (
            ntfy_config["topic"] == None
            or ntfy_config["server"] == None
        ):
            push_config["push_actions"].remove("ntfy")
            logger.info("Canceled")
            return {
                "push_actions": []
            }
        push_config["ntfy"] = ntfy_config
    if "Desktop Notify" in actions:
        push_config["push_actions"].append("desktop_notify")
        desktop_notify_config = {}
        desktop_notify_config["need_sound"] = questionary.confirm(
            "Need sound?",
        ).ask()
        if desktop_notify_config["need_sound"]:
            # make sure only a-zA-Z0-9_.- are in the file name
            import re

            desktop_notify_config["sound_path"] = questionary.path(
                "Sound file path:",
                validate=lambda text: bool(
                    re.match(r"^[a-zA-Z0-9_.-]+$", text)
                ),
            ).ask()
            if desktop_notify_config["sound_path"] == None:
                logger.info("Canceled")
                desktop_notify_config["sound_path"] = ""
        else:
            desktop_notify_config["sound_path"] = ""
        push_config["desktop_notify"] = desktop_notify_config
    if "PushPlus" in actions:
        push_config["push_actions"].append("pushplus")
        pushplus_config = {}
        pushplus_config["token"] = questionary.text(
            "PushPlus token:"
        ).ask()
        if pushplus_config["token"] == None:
            push_config["push_actions"].remove("pushplus")
            logger.info("Canceled")
            return {
                "push_actions": []
            }
        push_config["pushplus"] = pushplus_config
    if "ServerChan" in actions:
        push_config["push_actions"].append("server_chan")
        server_chan_config = {}
        server_chan_config["send_key"] = questionary.text(
            "ServerChan send key:",
        ).ask()
        if server_chan_config["send_key"] == None:
            push_config["push_actions"].remove("server_chan")
            logger.info("Canceled")
            return {
                "push_actions": []
                }
        push_config["server_chan"] = server_chan_config
    if "Run Command" in actions:
        push_config["push_actions"].append("run_command")
        run_command_config = {}
        logger.info("Warning: Please make sure you know what you are doing. This feature is intended for advanced users only.\nPlease add commands that are compatible with your operating system. You may choose to include the predefined ORDER_ID in your commands; the software will automatically replace it with the actual order number.")
        run_command_config["command"] = questionary.text(
            "Command to run:",
            validate=lambda text: text != "",
        ).ask()
        if run_command_config["command"] == None:
            push_config["push_actions"].remove("run_command")
            logger.info("Canceled")
            return {
                "push_actions": []
            }
        push_config["run_command"] = run_command_config
    return push_config
