# B站滑动验证码模拟登陆
使用selenium 的webdriver

使用PIL的Image来打开保存的图片

调用webdriver的ActionChains来模拟按住按钮然后滑动按钮

思路：1、先模拟登陆输入账号&密码触发出滑动验证码；2、截取验证码图片（分3个-->slice显示滑块，bg带缺口的图片，fullbg完整的图片）<需要调用方法self.driver.execute_script("arguments[0].style=arguments[1]", element, "display: block;")来获取完整的验证码图片>；计算滑块与缺口的距离-->使用完整图片与带缺口图片之间的像素对比来计算出迁移量；模拟鼠标悬停并拖动滑块，完成验证码的验证即可。
