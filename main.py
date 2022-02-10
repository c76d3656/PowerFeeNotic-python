import requests
import re
import base64

user_account = '1234567897'
user_password = '123456'
money_lower = 10
sendkey = "sendkey"
server_ip_port = "1.1.1.1:1111"

# 将密码使用base64编码，编码后会出现b'password_encode'的字符串，使用正则表达式提取password_encode，但提出出来的是list
password = re.findall('\'(.*?)\'', str(base64.b64encode(user_password.encode('ascii'))))[0]
# form表单的构造
data = {
    'SignType': "SynSno",  # 登陆方式，这里选择的是学工号
    'UserAccount': user_account,  # 即较长的那一段，例子8110210101
    'Password': password,  # 密码一般为身份证后六位，但在上传前需要将其使用base64编码一遍
    'NextUrl': '',  # 决定下一步跳转到哪个页面 具体有那些页面可以登陆http://ecard.csu.edu.cn:8070/Account/Login查看
    'openid': '',  # 表单中必须提交但为空，不知道为什么
    'Schoolcode': 'csu'  # 写死在表单，意义不明
}
# 请求头文件设置
# user-agent标明是正常请求操作
# origin 是网站开启了strict-origin-when-cross-origin策略
# Referer 是网站开启了防止恶意请求操作
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.76',
           'Origin': 'http://ecard.csu.edu.cn:8070',
           'Referer': 'http://ecard.csu.edu.cn:8070/Account/Login'
           }
# post表单提交的target
login_url = 'http://ecard.csu.edu.cn:8070/Account/Login'
# 建立seesion会话窗口，可用于跳转下一页面而不断开连接
session = requests.Session()
resp = session.post(login_url, headers=headers, data=data)
# 下一级页面跳转，来源为 Next_url的base64 decode
# #next_url = 'aHR0cDovL2VjYXJkLmNzdS5lZHUuY246ODA3MC9BdXRvUGF5L1Bvd2VyRmVlL0NzdUluZGV4'
url = 'http://ecard.csu.edu.cn:8070/AutoPay/PowerFee/CsuIndex'
# 获取页面资源
response = session.get(url)
# 通过正则提取页面电费余额信息，但提取出来是list
money = re.findall('<span id="getbanlse" style="color:red">(.*?)</span>', response.content.decode('utf-8'))
# 判断余额是否低于阈值,是则发送通知推送消息提醒
for res_money in money:
    if float(res_money) < money_lower:
        msg = "剩下的电费余额为 " + res_money + " 请尽快充值"
        requests.get("http://" + server_ip_port + "/wecomchan?sendkey=" + sendkey + "&msg=" + msg + "&msg_type=text")
