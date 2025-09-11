<template>
  <div class="home-page">
    <div id="navi">
      <div id="Name">AI Course</div>
      <div id="searchContainer">
        <div id="searchWrapper">
          <input type="text" id="searchBox" placeholder="搜索课程...">
        </div>
        <button id="searchButton" type="submit">
          <i class="bi-search">搜索</i>
        </button>
      </div>
      <div class="navItem">
        <div class="navIcon">
          <i class="bi-house-door"></i>
        </div>
        <div class="navTxt">主页</div>
      </div>
      <div class="navItem">
        <div class="navIcon">
          <i class="bi bi-book"></i>
        </div>
        <div class="navTxt">我的课程</div>
      </div>
      <div class="navItem">
        <div class="navIcon">
          <i class="bi bi-envelope"></i>
        </div>
        <div class="navTxt">我的消息</div>
      </div>
      <router-link to="/login" class="navItem">
        <div class="navIcon">
          <i class="bi bi-person"></i>
        </div>
        <div class="navTxt">登录</div>
      </router-link>
      <div class="navItem">
        <div class="navIcon">
          <i class="bi bi-question-circle"></i>
        </div>
        <div class="navTxt">帮助</div>
      </div>
    </div>

    <div class="newsContainer">
      <a href="https://example.com" target="_blank">
        <img src="https://i-blog.csdnimg.cn/direct/9731859d2a6d49f7b28ec65cc9e3fea4.png#pic_center"
          alt="Description of Image" class="newsImageLink">
      </a>
    </div>

    <div class="contactAIRoboticsContainer">
      <div class="chatBox">
        <div class="chatHistory" id="chatHistory">
          <iframe
            src="http://localhost:8080/chat/share?shared_id=232bc5ca567911f0b5804a0728688c7b&from=chat&auth=FlNDlkM2MwM2UxMTExZjA5NGUxMGU0NW"
            style="width: 100%; height: 100%; min-height: 450px; border: none;">
          </iframe>
        </div>
      </div>
    </div>

    <footer>
      <div>
        <ul class="youqinglianjie">
          <li><a href="http://www.wenming.cn/" target="_blank">中国文明网</a></li>
          <li><a href="http://www.scwmw.cn" target="_blank">四川文明网</a></li>
          <li><a href="http://shaoer.cntv.cn/" target="_blank">央视网青少年台</a></li>
          <li><a href="http://www.cnfirst.net/" target="_blank">中国儿童教育网</a></li>
          <li><a href="http://www.ccppg.com.cn/" target="_blank">中少在线</a></li>
          <li><a href="http://www.haomahaoba.com/" target="_blank">全国网上家长学校</a></li>
          <li><a href="http://www.zget.org/" target="_blank">中国儿童网</a></li>
          <li><a href="http://www.cncv.org.cn/" target="_blank">中国社区志愿服务网</a></li>
          <li><a href="http://www.w010w.com.cn/" target="_blank">中国网联网</a></li>
          <li><a href="http://www.tjwenming.cn/" target="_blank">天津文明网</a></li>
          <li><a href="http://sd.wenming.cn/" target="_blank">山东文明网</a></li>
          <li><a href="http://edu.sxgov.cn/" target="_blank">黄河新闻网科教频道</a></li>
          <li><a href="http://www.dzrbs.com/" target="_blank">达州日报网</a></li>
          <li><a href="http://www.cqnews.net/" target="_blank">华龙网</a></li>
          <li><a href="http://www.xncmw.cn/" target="_blank">西南传媒网</a></li>
        </ul>
      </div>
      <div>
        <ul class="bottom">
          <li><a href="http://www.kids21.cn/wzdb/gywm/201102/t20110214_39536.htm" target="_blank">版权说明</a></li>
          <li style="color: #fff;">|</li>
          <li><a href="http://www.kids21.cn/wzdb/gywm/201102/t20110214_39536.htm" target="_blank">用户协议</a></li>
          <li style="color: #fff;">|</li>
          <li><a href="http://www.kids21.cn/wzdb/gywm/201102/t20110214_39536.htm" target="_blank">隐私政策</a></li>
          <li style="color: #fff;">|</li>
          <li><a href="http://www.kids21.cn/wzdb/gywm/201102/t20110214_39536.htm" target="_blank">服务中心</a></li>
          <li style="color: #fff;">|</li>
          <li><a href="http://www.kids21.cn/wzdb/gywm/201102/t20110214_39536.htm" target="_blank">关于我们</a></li>
          <li style="color: #fff;">|</li>
          <li><a href="http://www.kids21.cn/wzdb/lxwm/201102/t20110218_45795.htm" target="_blank">关于作品</a></li>
          <li style="color: #fff;">|</li>
          <li><a href="http://www.kids21.cn/wzdb/jrwm/201102/t20110218W_45824.htm" target="_blank">联系我们</a></li>
          <li style="color: #fff;">|</li>
          <li><a href="#top">返回首页</a></li>
        </ul>
      </div>
    </footer>
  </div>
</template>

<script setup>
// Home page component logic
</script>

<style scoped>
/* 复制原有的 HomePage.css 内容 */
@import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css');

#navi {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 70px;
  background-color: #000000;
  display: flex;
  align-items: center;
  z-index: 1000;
}

#Name {
  font-family: "Snap ITC";
  font-size: 20px;
  color: #fff;
  padding-right: 20px;
  margin-left: 20px;
}

#searchContainer {
  display: flex;
  align-items: center;
  margin-right: 20px;
}

#searchWrapper {
  position: relative;
  width: 480px;
}

#searchBox {
  width: 100%;
  height: 40px;
  background-color: #1f1f1f;
  border: none;
  border-radius: 4px;
  padding: 0 15px;
  color: #fff;
  font-size: 14px;
}

#searchButton {
  margin-left: 10px;
  padding: 8px 15px;
  background-color: transparent;
  border: 1px solid #fff;
  border-radius: 4px;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.navItem {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 15px;
  cursor: pointer;
  text-decoration: none;
  color: inherit;
}

.navIcon {
  color: #fff;
  font-size: 20px;
}

.navTxt {
  color: #fff;
  font-size: 12px;
  font-family: 'Times New Roman', Times, serif;
  margin-top: 4px;
}

.newsContainer {
  margin-top: 90px;
  padding: 20px;
  text-align: center;
}

.newsImageLink {
  max-width: 100%;
  height: auto;
}

.contactAIRoboticsContainer {
  margin: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

footer {
  background-color: #000000;
  padding: 20px;
  color: #fff;
  margin-top: 40px;
}

.youqinglianjie {
  list-style: none;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.youqinglianjie a {
  color: #fff;
  text-decoration: none;
}

.bottom {
  list-style: none;
  padding: 0;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.bottom a {
  color: #fff;
  text-decoration: none;
}
</style> 