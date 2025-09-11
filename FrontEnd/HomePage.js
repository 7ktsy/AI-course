// 检查用户登录状态，从localStorage获取
    let isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';

    // 检查用户是否已登录，并在未登录时跳转到登录页面
    function checkLoginStatusAndRedirect() {
        // 重新检查localStorage中的登录状态
        isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
        
        if (!isLoggedIn) {
            // 如果用户未登录，跳转到登录页面
            window.location.href = "LoginRegister/Login/Login.html";
        } else {
            // 如果已登录，跳转到相应的工作台
            const userRole = localStorage.getItem('userRole');
            window.location.href = "WorkStation/Layout.html";
        }
    }

    // 更新导航栏的登录状态显示
    function updateLoginStatus() {
        const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
        const userRole = localStorage.getItem('userRole');
        const loginNavItem = document.querySelector('a.navItem[href*="Login"]');
        
        if (isLoggedIn && loginNavItem) {
            // 如果已登录，将登录按钮改为用户信息
            const userRoleText = {
                'student': '学生',
                'teacher': '教师',
                'admin': '管理员'
            };
            
            loginNavItem.innerHTML = `
                <div class="navIcon">
                    <i class="bi bi-person-check"></i>
                </div>
                <div class="navTxt">已登录(${userRoleText[userRole] || '用户'})</div>
            `;
            
            // 修改链接，点击后跳转到工作台
            loginNavItem.href = "WorkStation/Layout.html";
        }
    }

    // 插入机器人的欢迎消息（已注释掉，使用iframe替代）
    /*
    function addWelcomeMessage() {
        const chatHistory = document.getElementById('chatHistory');

        // 创建机器人的消息
        const messageDiv = document.createElement('div');
        messageDiv.className = 'messageBot';
        messageDiv.style.marginBottom = '50px';

        const avatarImg = document.createElement('img');
        avatarImg.src = '../Photos/ChatRob.jpg';
        avatarImg.alt = 'Bot Avatar';

        const replayBot = document.createElement('div');
        replayBot.className = 'replayBot';

        const headerBot = document.createElement('div');
        headerBot.className = 'headerBot';

        const nameBot = document.createElement('span');
        nameBot.className = 'nameBot';
        nameBot.textContent = 'ChatBot';

        const timestamp = document.createElement('span');
        timestamp.className = 'timestamp';
        timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const bubbleBot = document.createElement('div');
        bubbleBot.className = 'bubbleBot';
        // bubbleBot.innerHTML = '亲爱的同学:<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;你好，我是你的AI智能老师，很高兴见到你。有任何问题都可以直接请教我！';

        // 组装结构
        headerBot.appendChild(nameBot);
        headerBot.appendChild(timestamp);
        replayBot.appendChild(headerBot);
        replayBot.appendChild(bubbleBot);
        messageDiv.appendChild(avatarImg);
        messageDiv.appendChild(replayBot);

        // 插入到 chatHistory
        chatHistory.appendChild(messageDiv);

        // 滚动到最新消息
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
    */

    // 页面加载完成后初始化
    document.addEventListener("DOMContentLoaded", function() {
        // 更新导航栏的登录状态
        updateLoginStatus();
        
        // 插入机器人的欢迎消息（已注释掉，使用iframe替代）
        // addWelcomeMessage();

        // 获取所有 .navTxt 元素
        const navTxtElements = document.querySelectorAll('.navItem');

        // 为每个 .navTxt 元素添加点击事件监听器
        navTxtElements.forEach(function(element) {
            element.addEventListener('click', function() {
                if (element.textContent.includes("我的课程") || element.textContent.includes("我的消息")) {
                    checkLoginStatusAndRedirect();
                }
            });
        });

        // 获取图片元素
        const contactImage = document.getElementById('contactImage');
        // 获取目标容器
        const contactContainer = document.querySelector('.contactAIRoboticsContainer');

        // 为图片添加点击事件监听器
        contactImage.addEventListener('click', function() {
            // 平滑滚动到目标容器
            contactContainer.scrollIntoView({ behavior: 'smooth' });
        });

        // 更新导航栏登录状态
        updateLoginStatus();
    });

    // 处理用户输入（已注释掉，使用iframe替代）
    /*
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        const userInput = document.getElementById('userInput');
        const chatHistory = document.getElementById('chatHistory');

        // 获取用户输入
        const userMessage = userInput.value.trim();
        if (userMessage === '') {
            return; // 如果输入为空，不做处理
        }

        // 创建用户消息
        const userMessageElement = document.createElement('div');
        userMessageElement.className = 'messageUser';
        userMessageElement.style.marginBottom = '30px';

        const replayUser = document.createElement('div');
        replayUser.className = 'replayUser';

        const headerUser = document.createElement('div');
        headerUser.className = 'headerUser';

        const nameUser = document.createElement('span');
        nameUser.className = 'nameUser';
        nameUser.textContent = 'User';

        const timestampUser = document.createElement('span');
        timestampUser.className = 'timestamp';
        timestampUser.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const bubbleUser = document.createElement('div');
        bubbleUser.className = 'bubbleUser';
        bubbleUser.innerHTML = userMessage;

        headerUser.appendChild(nameUser);
        headerUser.appendChild(timestampUser);
        replayUser.appendChild(headerUser);
        replayUser.appendChild(bubbleUser);

        userMessageElement.appendChild(replayUser);

        const userAvatar = document.createElement('img');
        userAvatar.src = 'user-avatar.jpg'; // 替换为你的用户头像路径
        userAvatar.alt = 'User Avatar';

        userMessageElement.appendChild(userAvatar); // 将头像放在右边

        // 将用户消息插入到 chatHistory
        chatHistory.appendChild(userMessageElement);

        // 滚动到最新消息
        chatHistory.scrollTop = chatHistory.scrollHeight;

        // 模拟回答
        setTimeout(() => {
            // 创建机器人消息
            const botMessageElement = document.createElement('div');
            botMessageElement.className = 'messageBot';
            botMessageElement.style.marginBottom = '20px';

            const replayBot = document.createElement('div');
            replayBot.className = 'replayBot';

            const headerBot = document.createElement('div');
            headerBot.className = 'headerBot';

            const nameBot = document.createElement('span');
            nameBot.className = 'nameBot';
            nameBot.textContent = 'ChatBot';

            const timestampBot = document.createElement('span');
            timestampBot.className = 'timestamp';
            timestampBot.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            const bubbleBot = document.createElement('div');
            bubbleBot.className = 'bubbleBot';
            bubbleBot.innerHTML = getBotResponse(userMessage);

            headerBot.appendChild(nameBot);
            headerBot.appendChild(timestampBot);
            replayBot.appendChild(headerBot);
            replayBot.appendChild(bubbleBot);

            botMessageElement.appendChild(replayBot);

            const botAvatar = document.createElement('img');
            botAvatar.src = '../Photos/ChatRob.jpg'; // 替换为你的机器人头像路径
            botAvatar.alt = 'Bot Avatar';

            botMessageElement.insertBefore(botAvatar, replayBot);

            // 将机器人消息插入到 chatHistory
            chatHistory.appendChild(botMessageElement);

            // 滚动到最新消息
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }, 500); // 模拟延迟响应

        // 清空输入框
        userInput.value = '';
    }
}

// 获取机器人的回答
function getBotResponse(message) {
    switch (message.toLowerCase()) {
        case 'hello':
            return 'Hi there!';
        case 'how are you':
            return 'I am good, thanks for asking!';
        default:
            return 'Sorry, I did not understand that.';
    }
}
*/
