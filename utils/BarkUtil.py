import requests
import json
from loguru import logger


def sendBark(userKey,buyUser,ticketCount,ticketPrice,
             ticketDetail,repartCount:int=3):
    """
        发送Bark消息
        :param userKey: bark用户key
        :param buyUser: 用户名
        :param ticketCount: 数量
        :param ticketPrice: 价格
        :param ticketDetail: 详情
        :param repartCount: 重试次数
    """
    # 会尝试发送3次，直至成功
    from urllib.parse import quote
    from datetime import datetime
    if not userKey:
        return False
    # 支持多用户
    if userKey.find(","):
        userKey = userKey.split(",")
    else:
        userKey = [userKey]
    for toKey in userKey:
        isSuccess = False
        tmpCount = 0
        while not isSuccess:
            try:
                url = "https://api.day.app/push"
                payload = json.dumps({
                "body": f"📝 {ticketDetail}\n🗓 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n🎫 {ticketCount} 张\n💰 ￥{ticketPrice} 元\n",
                "title": "CPP Buy Success🎉",
                "subtitle": f"👑 {buyUser}",
                "device_key": toKey,
                "action": "none",
                "isArchive": "1",
                })
                headers = {
                    'Content-Type': 'application/json; charset=utf-8'
                }
                response = requests.request("POST", url, headers=headers, data=payload)
                if response.status_code == 200:
                    logger.info("推送Bark消息成功.....")
                    isSuccess = True
                    break
            except:
                pass
            finally:
                tmpCount+=1
                if tmpCount >= repartCount:
                    break
    return isSuccess