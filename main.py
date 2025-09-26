import os
import random
import time
import requests
session = requests.Session()

import questionary
# import sentry_sdk
from loguru import logger

print(r"""   ______    _             ____     ____        
  / ____/   (_)  ____ _   / __ \   / __ \  ____ 
 / /       / /  / __ `/  / /_/ /  / /_/ / / __ \
/ /___    / /  / /_/ /  / ____/  / ____/ / /_/ /
\____/   /_/   \__,_/  /_/      /_/      \____/ 
                                                
CiaPPo～(∠・ω< )⌒☆ v1.0.0""")

while True:
    loginType = questionary.select(
        "Login Type:",
        choices=[
            "1. Phone + Password",
            "2. Token",
        ],
    ).ask()
    if loginType is None:
        logger.error("Login type is None")
        continue
    if loginType.startswith("2"):
        token = questionary.text("Token:").ask()
        logger.info(f"Using token: {token}")
        break
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

confirm = questionary.confirm(
    f"Confirm to buy {count} tickets of type {ticketTypeName} with purchaser {purchaserNames} with {'Alipay' if paymentMethod=='ali' else 'Wechat Pay'}?", default=True
).ask()
if not confirm:
    logger.info("Canceled")
    os._exit(0)

while True:
    try:
        nonce = "".join(
            random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=5)
        )
        timestamp = str(int(time.time() * 1000))
        sign_resp = session.post(
            "https://sign.rakuyoudesu.com/",
            json={
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
        ).json()
        logger.debug(resp)
        if resp["isSuccess"]:
            logger.success("Success")
            break
        else:
            logger.info(f"Failed, {resp['message']}")
        time.sleep(ttl)
    except Exception as e:
        logger.error(f"Exception: {e}")
        time.sleep(ttl)
