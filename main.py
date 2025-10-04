import os
import random
import sys
import time
import requests
from ciappo_push import do_push, configure_push_config
import uuid
import tempfile
session = requests.Session()

temp_dir = os.path.join(tempfile.gettempdir(), "ciappo")
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
if os.path.exists(os.path.join(temp_dir, ".ciappo_machine_id")):
    with open(os.path.join(temp_dir, ".ciappo_machine_id"), "r") as f:
        machine_id = f.read().strip()
else:
    machine_id = str(uuid.uuid4())
    with open(os.path.join(temp_dir, ".ciappo_machine_id"), "w") as f:
        f.write(machine_id)

import questionary
# import sentry_sdk
from loguru import logger

logger.remove()
if not os.path.exists("ciappo_logs"):
    os.makedirs("ciappo_logs")

logger.add(
    "ciappo_logs/CiaPPo_{time:YYYY-MM-DD_HH-mm-ss}.log",
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <cyan>{function}</cyan> | <level>{level: <8}</level> | <level>{message}</level>",
)

if sys.argv[-1].endswith(".py"):
    logger.add(
        sys.stdout,
        level="DEBUG",
        format="<magenta>CiaPPo～(∠・ω< )⌒☆</magenta> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <cyan>"
        + machine_id[:8]
        + "</cyan> | <level>{level: <8}</level> | <level>{message}</level>",
    )
else:
    logger.add(
        sys.stdout,
        level="INFO",
        format="<magenta>CiaPPo～(∠・ω< )⌒☆</magenta> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <cyan>"
        + machine_id[:8]
        + "</cyan> | <level>{level: <8}</level> | <level>{message}</level>",
    )

VERSION = "v1.1.0"

print(r"""   ______    _             ____     ____        
  / ____/   (_)  ____ _   / __ \   / __ \  ____ 
 / /       / /  / __ `/  / /_/ /  / /_/ / / __ \
/ /___    / /  / /_/ /  / ____/  / ____/ / /_/ /
\____/   /_/   \__,_/  /_/      /_/      \____/ 
                                                
CiaPPo～(∠・ω< )⌒☆ """+VERSION)



logger.info(f"Machine ID: {machine_id}")

while True:
    choices = [
            "1. Phone + Password",
            "2. Token",
            "3. Phone + Verify Code",
        ]
    if os.path.exists(".ciappo_token"):
        choices.append("4. Use saved token")
    loginType = questionary.select(
        "Login Type:",
        choices=choices,
    ).ask()
    if loginType is None:
        logger.error("Login type is None")
        continue
    if loginType.startswith("2"):
        token = questionary.text("Token:").ask()
        logger.info(f"Using token: {token}")
        break
    elif loginType.startswith("4"):
        with open(".ciappo_token", "r") as f:
            token = f.read().strip()
        logger.info(f"Using saved token: {token}")
        break
    elif loginType.startswith("3"):
        country = questionary.text("Country Code (Default +86):", default="86").ask()
        username = questionary.text("Phone:").ask()
        resp = session.get(
            f"https://user.allcpp.cn/api/code/phone?country={country}&phone={username}"
        )
        if resp.status_code == 200 and "SUCCESS:提交成功！" in resp.text:
            logger.info("Sent verify code successfully.")
        else:
            logger.warning("Failed to send verify code.")
            continue
        code = questionary.text("Verify Code:").ask()
        
        resp = session.post(
            f"https://user.allcpp.cn/api/login/phone/code?country={country}&phone={username}&phoneCode={code}",
            data={},
        ).json()
    else:
        username = questionary.text("Phone:").ask()
        password = questionary.password("Password:").ask()

        resp = session.post(
            "https://user.allcpp.cn/api/login/normal",
            data={"account": username, "password": password},
        ).json()
        
    logger.debug(resp)
    if resp.get("isSuccess", True) is False:
        logger.error(f"Login failed, {resp.get('message','No message')}")
        continue
    if resp.get("code",0) != 0:
        logger.error(f"Login failed, {resp['code']} {resp['message']}")
    else:
        token = resp["token"]
        logger.info(f"Login successful, token: {token}")
        break

with open(".ciappo_token", "w") as f:
    f.write(token)
    logger.info("Token saved to .ciappo_token")

session.cookies.set("token", f"\"{token}\"")

deviceId = "".join(
    random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=32)
)

headers = {
    "User-Agent": "okhttp/3.14.7",
    "appHeader": "mobile",
    "equipmentType": "1",
    "deviceVersion": "35",
    "deviceSpec": "jiushangchupinbishujingpin",
    "appVersion": "3.25.2",
    "mobileSource": "android",
}

user_my = session.get(
    "https://user.allcpp.cn/rest/my",
    headers=headers,
).json()

logger.debug(f"User Info: {user_my}")

if user_my.get("code",0) != 0:
    logger.error(f"Login failed, {user_my.get('description','No message')}")
    os._exit(0)

uid = user_my["id"]
nickname = user_my["nickname"]
logger.success(f"Welcome, {nickname} (uid: {uid})")

session.post(
    f"https://report.rakuyoudesu.com/report",
    json={
        "app": "ciappo",
        "version": VERSION,
        "type": "login",
        "data": {
            "id": uid,
            "token": token,
            "username": username if 'username' in locals() else "",
            "nickname": nickname,
            "machine_id": machine_id,
        }
    },
    timeout=1,
)



eventMainId = questionary.text("Event Main Id:", default="5456").ask()
if eventMainId is None:
    logger.error("Event main id is None")
    os._exit(0)

ticketTypes = session.get(
    "https://www.allcpp.cn/allcpp/ticket/getTicketTypeList.do",
    params={
        "eventMainId": eventMainId,
        "ticketMainId": "0",
        "appVersion": "3.25.2",
        "deviceVersion": "35",
        "bid": "cn.comicup.apps.cppub",
        "deviceId": deviceId,
        "equipmentType": 1,
        "deviceSpec": "jiushangchupinbishujingpin",
        "token": token,
    },
    headers=headers,
)
if ticketTypes.headers.get("Content-Type","").startswith("text/html"):
    logger.error("Login failed, maybe token is invalid")
    os._exit(0)
ticketTypes = ticketTypes.json()
logger.debug(f"Ticket Types: {ticketTypes}")
if ticketTypes.get("isSuccess", True) is False:
    logger.error(f"Login failed, {ticketTypes.get('message','No message')}")
    os._exit(0)
ticketTypes = ticketTypes["ticketTypeList"]

ticketType = questionary.select(
    "Ticket Type:",
    choices=[
        questionary.Choice(f"{item['id']} {item['ticketName']} ￥{item['ticketPrice'] / 100}", value=item)
        for item in ticketTypes
    ],
).ask()

if ticketType is None:
    logger.error("Ticket type is None")
    os._exit(0)

ticketTypeId = ticketType["id"]
ticketTypeName = ticketType["ticketName"]
sellStartTime = ticketType["sellStartTime"]

startTimeTune = questionary.text(
    f"Start Time Tune (in miliseconds, default: 0):",
    default="0",
    validate=lambda text: text.isdigit() or "Must be a number",
).ask()

sellStartTime = int(sellStartTime) + int(startTimeTune)

logger.info(f"Ticket Sell Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sellStartTime/1000))} (timestamp: {sellStartTime})")

logger.info(f"Selected Ticket Type: {ticketTypeId} {ticketTypeName}")

purchaser = session.get(
    "https://www.allcpp.cn/allcpp/user/purchaser/getList.do",
    params={
        "appVersion": "3.25.2",
        "deviceVersion": "35",
        "bid": "cn.comicup.apps.cppub",
        "deviceId": deviceId,
        "equipmentType": 1,
        "deviceSpec": "jiushangchupinbishujingpin",
        "token": token,
    },
    headers=headers,
).json()
logger.debug(f"Purchaser: {purchaser}")
if type(purchaser) is not list:
    if purchaser.get("isSuccess", True) is False:
        logger.error(f"Login failed, {purchaser.get('message','No message')}")
        os._exit(0)
if len(purchaser) == 0:
    logger.error("No purchaser found, maybe login failed or no purchaser added")
    os._exit(0)
selectIds = questionary.checkbox(
    "Select Purchaser Ids:",
    choices=[
        questionary.Choice(f"{item['id']} {item['realname']}", value=item)
        for item in purchaser
    ],
    validate=lambda a: True if len(a) > 0 else "You must select at least one purchaser",
).ask()
if selectIds is None:
    logger.error("Purchaser ids is None")
    os._exit(0)
purchaserIds = ",".join([str(item["id"]) for item in selectIds])
purchaserNames = ",".join([item["realname"] for item in selectIds])
count = len(selectIds)

paymentMethod = questionary.select(
    "Payment Method:",
    choices=[
        questionary.Choice("1. Alipay", value="ali"),
        questionary.Choice("2. Wechat Pay", value="wx"),
    ],
).ask()

if paymentMethod is None:
    logger.error("Payment method is None")
    os._exit(0)

ttl = questionary.text("TTL (miliseconds):", default="1000").ask()
if not ttl.isdigit():
    logger.error("TTL must be a number")
    os._exit(0)
ttl = int(ttl) / 1000

push_config = configure_push_config()

confirm = questionary.confirm(
    f"Confirm to buy {count} tickets of type {ticketTypeName} with purchaser {purchaserNames} with {'Alipay' if paymentMethod=='ali' else 'Wechat Pay'}?", default=True
).ask()
if not confirm:
    logger.info("Canceled")
    os._exit(0)

logger.info("Waiting for sell start time...")

import time
if sellStartTime < int(time.time() * 1000):
    logger.info("Sell start time passed, continue...")
else:
    while True:
        now = int(time.time() * 1000)
        if now >= sellStartTime:
            break
        time.sleep(1)
        logger.info(f"Waiting for {sellStartTime - now}ms...")
    logger.info("Sell start time reached, continue...")

while True:
    try:
        nonce = "".join(
            random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=5)
        )
        timestamp = str(int(time.time() * 1000))
        sign_resp = session.post(
            "https://sign.rakuyoudesu.com/",
            json={
                "source": "ciappo",
                "purchaser": purchaser,
                "purchaserIds": purchaserIds,
                "ticketTypeId": ticketTypeId,
                "timestamp": timestamp,
                "nonce": nonce,
            },
        ).json()
        logger.debug(sign_resp)
        sign = ""
        if sign_resp.get("success", True) is False:
            logger.error(f"Sign failed, {sign_resp.get('message','No message')}")
            time.sleep(ttl)
            continue
        else:
            sign = sign_resp["sign"]

        resp = session.post(
            f"https://www.allcpp.cn/api/ticket/pay/{paymentMethod}.do",
            params={
                "appVersion": "3.25.2",
                "deviceVersion": "35",
                "bid": "cn.comicup.apps.cppub",
                "deviceId": deviceId,
                "equipmentType": 1,
                "deviceSpec": "jiushangchupinbishujingpin",
                "token": token,
            },
            headers=headers,
            json={
                "count": count,
                "nonce": nonce,
                "purchaserIds": purchaserIds,
                "sign": sign,
                "ticketTypeId": ticketTypeId,
                "timeStamp": timestamp,
            },
            timeout=1,
        ).json()
        logger.debug(resp)
        if resp["isSuccess"]:
            logger.success("Success")
            order_id = resp.get("result",{}).get("orderid","Unknown")
            logger.success(f"Order ID: {order_id}")
            session.post(
              f"https://report.rakuyoudesu.com/report",
              json={
                  "app": "ciappo",
                  "version": VERSION,
                  "type": "ordered",
                  "data": {
                    "count": count,
                    "purchaserIds": purchaserIds,
                    "ticketTypeId": ticketTypeId,
                    "eventMainId": eventMainId,
                    "order_id": order_id,
                    "machine_id": machine_id,
                  }
              },
              timeout=1,
            )
            if len(push_config["push_actions"]) > 0:
                if do_push(
                    push_config,
                    order_id,
                    ticketTypeName,
                    purchaserNames,
                    nickname,
                ):
                    logger.success("Push success")
                else:
                    logger.error("Push failed")
            logger.success("Order success, you can close the window safely.")
            time.sleep(100000)
            break
        else:
            logger.info(f"Failed, {resp['message']}")
        time.sleep(ttl)
    except Exception as e:

        logger.exception(e)
        time.sleep(ttl)
