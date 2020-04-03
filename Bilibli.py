# -*- coding: utf-8 -*-
import random
import time

from selenium import webdriver
from  PIL import Image
from selenium.webdriver import ActionChains


class Bili(object):

	def __init__(self):
		login_url = 'https://passport.bilibili.com/login'
		chrome_path = 'C:\Program Files (x86)\chromedriver\chromedriver.exe'
		self.driver = webdriver.Chrome(executable_path=chrome_path)
		self.driver.get(login_url)

	def __del__(self):
		self.driver.close()

	def show_element(self, element):  # 让验证码图片迅速还原成完整图片
		self.driver.execute_script("arguments[0].style=arguments[1]", element, "display: block;")

	def hide_element(self, element):  # 暂不知用处
		self.driver.execute_script("arguments[0].style=arguments[1]", element, "display: none;")

	def open_login(self):
		try:
			t = random.uniform(0, 0.5)
			time.sleep(1)
			username = self.driver.find_element_by_xpath('//*[@id="login-username"]')
			time.sleep(t)
			username.send_keys('账号')
			time.sleep(t)
			password = self.driver.find_element_by_xpath('//*[@id="login-passwd"]')
			time.sleep(t)
			password.send_keys('密码')
			time.sleep(1)
			login_but = self.driver.find_element_by_xpath('//a[@class="btn btn-login"]')
			login_but.click()
			time.sleep(2)
		except Exception as e:
			print(e)

	def get_image_loction(self):
		# 之所以用三个图片是因为用两个函数处理的图片会形成三个，slice是显示滑块，bg是显示带缺口的图片，fullbg是完整的图片
		# 获取图片验证码位置
		imgx = self.driver.find_element_by_xpath('//canvas[@class="geetest_canvas_slice geetest_absolute"]')
		img1 = self.driver.find_element_by_xpath('//canvas[@class="geetest_canvas_bg geetest_absolute"]')
		img2 = self.driver.find_element_by_xpath('//canvas[@class="geetest_canvas_fullbg geetest_fade geetest_absolute"]')
		# self.hide_element(imgx)
		self.show_element(imgx)
		self.get_image(imgx, 'slice.png')  # 带滑块的验证码图片
		time.sleep(0.2)
		self.get_image(img1, 'bg.png')  # 带滑块的验证码图片
		time.sleep(0.3)
		self.show_element(img2)
		self.get_image(img2, 'fullbg.png')  # 抓取到完整的验证码图片

	def get_image(self, img, name):
		# 一次截图：形成全图
		self.driver.save_screenshot(r'./Images/Bphoto.png')
		# 验证码路径
		loction = img.location
		# 验证码尺寸
		size = img.size
		# 定位验证码四个坐标位置  区块截图左上角在网页中的y坐标,区块截图右下角在网页中的y坐标,区块截图左上角在网页中的x坐标,区块截图右下角在网页中的x坐标
		top, bottom, left, right = loction['y'], loction['y'] + size['height'], loction['x'], loction['x'] + size['width']
		picture = Image.open(r'./Images/Bphoto.png')  # 打开全图
		picture = picture.crop((left, top, right, bottom))  # 二次截图：形成区块截图
		picture.save(r'./Images/%s' % name)  # 保存验证码图片
		time.sleep(0.2)

	def is_pixel_equal(self, bg_image, fullbg_image, x, y):
		"""
		:param bg_image: (Image)缺口图片
		:param fullbg_image: (Image)完整图片
		:param x: (Int)位置x
		:param y: (Int)位置y
		:return: (Boolean)像素是否相同
		"""
		# 获取缺口图片的像素点（按RGE格式）
		bg_pixel = bg_image.load()[x, y]
		# 获取完整图片的像素点（按RGB格式）
		fullbg_pixel = fullbg_image.load()[x, y]
		# 设定一个像素判定值，像素值之差超过这个值就判定像素不同
		threshold = 60
		if (abs(fullbg_pixel[0] - bg_pixel[0] < threshold) and abs(fullbg_pixel[1] - bg_pixel[1] < threshold) and abs(
				fullbg_pixel[2] - bg_pixel[2] < threshold)):
			# 如果差值在判断值之内，返回是相同像素
			return True

		else:
			# 如果差值在判断值之外，返回不是相同像素
			return False

	def get_distance(self, bg_image, fullbg_image):
		"""
		:param: bg_image: 带缺口图片
		:param: fullbg_image: 完整图片
		:return: (Int)滑块与缺口之间的距离
		"""
		# 滑块位置初始设置为 60
		distance = 60
		print(fullbg_image.size[0], fullbg_image.size[1])
		# 遍历像素点横坐标
		for i in range(distance, fullbg_image.size[0]):
			# 遍历像素点纵坐标
			for j in range(fullbg_image.size[1]):
				if not self.is_pixel_equal(bg_image, fullbg_image, i, j):  # 调用is_pixel_equal求带缺口图片与完整图片的像素值差
					# 返回此时横轴坐标就是滑块需要移动的距离
					return i

	def get_trace(self, distance):
		"""
		:param distance: (Int)缺口与滑块之间的距离
		:return: (List)移动轨迹
		"""
		# 创建存放轨迹信息的列表
		trace = []
		# 设置加速的距离
		faster_distance = distance * 1.5
		# 设置初始位置、初始速度、时间间隔
		start, v0, t = 0, 0, 0.1
		# 当尚未移动到终点时
		while start < distance:
			# 如果处于加速阶段
			if start < faster_distance:
				# 设置加速度为2
				a = 12
			# 如果处于减速阶段
			else:
				# 设置加速度为-3
				a = -4
			# 移动的距离公式
			move = v0 * t + 1 / 2 * a * t * t
			# 此刻速度
			v = v0 + a * t
			# 重置初速度
			v0 = v
			# 重置起点
			start += move
			# 将移动的距离加入轨迹列表
			trace.append(round(move))
		# 返回轨迹信息
		return trace

	def move_to_gap(self, trace):
		t = random.uniform(0, 0.5)
		# 得到滑块标签
		slider = self.driver.find_element_by_xpath('//div[@class="geetest_slider_button"]')
		# 使用click_and_hold()方法悬停在滑块上，perform()方法用于执行
		ActionChains(self.driver).click_and_hold(slider).perform()
		for x in trace:
			# 使用move_by_offset()方法拖动滑块，perform()方法用于执行
			ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
		# 模拟人类对准时间
		time.sleep(t)
		# 释放滑块
		ActionChains(self.driver).release().perform()

	def slice(self):
		bg_image = Image.open(r'./Images/bg.png')
		fullbg_image = Image.open(r'./Images/fullbg.png')
		try:
			distance = self.get_distance(bg_image, fullbg_image)
			print('计算偏移量为：%s Px' % distance)
			trace = self.get_trace(int(distance)-5)  # 减值--->防止拉伸过度，此处是处理滑块到缺口的距离，因为初始滑块就与边框有一段距离（猜测）
			print(trace)
			# 移动滑块
			self.move_to_gap(trace)
			time.sleep(0.5)
			# 目的 由于计算偏移量过大导致的验证码拖过，循环减偏移量的值
			while True:
				for i in range(6, 10):
					mspan = self.driver.find_element_by_xpath('//div[@class="geetest_result_content"]').text
					if '请正确拼合图像' in mspan:
						print(mspan)
						time.sleep(3)
						distance = self.get_distance(bg_image, fullbg_image)
						print('计算偏移量为：%s Px' % distance)
						trace = self.get_trace(int(distance)-int(i))  # 减值--->防止拉伸过度，此处是处理滑块到缺口的距离，因为初始滑块就与边框有一段距离（猜测）
						print('减值%s' % i)
						print(trace)
						# 移动滑块
						self.move_to_gap(trace)
						time.sleep(0.5)
					else:
						if '请重试' in mspan:
							print(mspan)
							time.sleep(3)
							distance = self.get_distance(bg_image, fullbg_image)
							print('计算偏移量为：%s Px' % distance)
							trace = self.get_trace(
								int(distance) - int(i))  # 减值--->防止拉伸过度，此处是处理滑块到缺口的距离，因为初始滑块就与边框有一段距离（猜测）
							print('减值%s' % i)
							print(trace)
							# 移动滑块
							self.move_to_gap(trace)
							time.sleep(0.5)
						else:
							break
				break
		except Exception as e:
			print(e)

	def get_html(self):
		time.sleep(2)
		print('---------')
		# link = self.driver.find_element_by_xpath('//*[@id="bili_live"]/div/div[2]/div[1]/div/a[3]')
		# print(link)

	def entrance(self):
		# 登陆 ---> 账号密码 --> 触发滑动验证码
		self.open_login()
		# 获取验证码路径，调用get_image截取验证码图片
		self.get_image_loction()
		# 滑动  ---滑块与缺口距离，判定像素值
		self.slice()
		self.get_html()


if __name__ == '__main__':
	bili = Bili()
	bili.entrance()

