// 菜单配置
const menuConfig = {
    student: [
        {
            id: 'dashboard',
            icon: 'bi-house',
            text: '首页概览',
            path: '/dashboard'
        },
        {
            id: 'courses',
            icon: 'bi-book',
            text: '我的课程',
            path: '/courses'
        },
        {
            id: 'homework',
            icon: 'bi-pencil-square',
            text: '我的作业',
            path: '/homework'
        },
        {
            id: 'practice',
            icon: 'bi-lightning',
            text: '实时练习',
            path: '/practice'
        },
        {
            id: 'grades',
            icon: 'bi-graph-up',
            text: '成绩查询与分析',
            path: '/grades'
        },
        {
            id: 'ai-assistant',
            icon: 'bi-robot',
            text: '学习助手',
            path: '/ai-assistant'
        }
    ],
    teacher: [
        {
            id: 'dashboard',
            icon: 'bi-house',
            text: '首页概览',
            path: '/dashboard'
        },
        {
            id: 'courses',
            icon: 'bi-book',
            text: '我的课程',
            path: '/courses'
        },
        {
            id: 'class-management',
            icon: 'bi-people',
            text: '班级管理',
            path: '/class-management'
        },
        {
            id: 'preparation',
            icon: 'bi-journal-text',
            text: '备课管理',
            path: '/preparation'
        },
        {
            id: 'homework-management',
            icon: 'bi-pencil-square',
            text: '作业批改',
            path: '/homework-management'
        },
        {
            id: 'question-bank',
            icon: 'bi-collection',
            text: '题库管理',
            path: '/question-bank'
        },
        {
            id: 'learning-analysis',
            icon: 'bi-bar-chart',
            text: '学情分析',
            path: '/learning-analysis'
        },
        {
            id: 'resources',
            icon: 'bi-folder2',
            text: '教学资源',
            path: '/resources'
        }
    ],
    admin: [
        {
            id: 'dashboard',
            icon: 'bi-house',
            text: '系统概览',
            path: '/dashboard'
        },
        {
            id: 'user-management',
            icon: 'bi-people',
            text: '用户管理',
            path: '/user-management'
        },
        {
            id: 'course-management',
            icon: 'bi-book',
            text: '课程管理',
            path: '/course-management'
        },
        {
            id: 'question-bank',
            icon: 'bi-collection',
            text: '题库管理',
            path: '/question-bank'
        },
        {
            id: 'system-settings',
            icon: 'bi-gear',
            text: '系统设置',
            path: '/system-settings'
        }
    ]
};

// 用户信息
let currentUser = {
    name: '',
    role: '',
    avatar: ''
};

// 初始化函数
function init() {
    // 获取用户信息
    getCurrentUser();
    // 加载菜单
    loadMenu();
    // 绑定事件
    bindEvents();
}

// 获取当前用户信息
function getCurrentUser() {
    // 从localStorage获取真实的用户信息
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const userRole = localStorage.getItem('userRole');
    const userInfo = localStorage.getItem('userInfo');
    
    if (!isLoggedIn || !userRole) {
        // 如果未登录，跳转到登录页面
        window.location.href = '../LoginRegister/Login/Login.html';
        return;
    }
    
    // 设置当前用户信息
    if (userInfo) {
        try {
            const parsedUserInfo = JSON.parse(userInfo);
            currentUser = {
                name: parsedUserInfo.name || parsedUserInfo.username || (userRole === 'admin' ? '管理员' : (userRole === 'teacher' ? '教师' : '学生')),
                role: userRole,
                avatar: 'assets/avatar-default.png',
                phone: parsedUserInfo.phone || localStorage.getItem('userPhone'),
                id: parsedUserInfo.id,
                university: parsedUserInfo.university,
                title: parsedUserInfo.title,
                department: parsedUserInfo.department
            };
        } catch (error) {
            console.error('解析用户信息失败:', error);
            currentUser = {
                name: userRole === 'admin' ? '管理员' : (userRole === 'teacher' ? '教师' : '学生'),
                role: userRole,
                avatar: 'assets/avatar-default.png'
            };
        }
    } else {
        currentUser = {
            name: userRole === 'admin' ? '管理员' : (userRole === 'teacher' ? '教师' : '学生'),
            role: userRole,
            avatar: 'assets/avatar-default.png'
        };
    }
    
    console.log('当前用户信息:', currentUser);
    updateUserInfo();
}

// 更新用户信息显示
function updateUserInfo() {
    document.querySelector('.user-name').textContent = currentUser.name;
    document.querySelector('.user-role').textContent = getRoleName(currentUser.role);
    document.querySelector('.user-avatar').src = currentUser.avatar;
}

// 获取角色显示名称
function getRoleName(role) {
    const roleNames = {
        student: '学生',
        teacher: '教师',
        admin: '管理员'
    };
    return roleNames[role] || role;
}

// 加载菜单
function loadMenu() {
    const menuContainer = document.querySelector('.menu-container');
    const menuItems = menuConfig[currentUser.role] || [];
    
    console.log('加载菜单 - 用户角色:', currentUser.role);
    console.log('菜单项:', menuItems);
    
    menuContainer.innerHTML = menuItems.map(item => `
        <div class="menu-item" data-id="${item.id}">
            <i class="bi ${item.icon}"></i>
            <span>${item.text}</span>
        </div>
    `).join('');
}

// 绑定事件
function bindEvents() {
    // 菜单项点击
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', handleMenuClick);
    });

    // 设置按钮点击
    document.querySelector('.settings').addEventListener('click', handleSettings);

    // 退出登录点击
    document.querySelector('.logout').addEventListener('click', handleLogout);

    // 通知点击
    document.querySelector('.notification').addEventListener('click', handleNotification);
}

// 处理菜单点击
function handleMenuClick(event) {
    const menuItem = event.currentTarget;
    // 移除其他菜单项的active类
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    // 添加active类到当前点击的菜单项
    menuItem.classList.add('active');
    
    // 更新面包屑
    updateBreadcrumb(menuItem.querySelector('span').textContent);
    
    // 加载对应的内容
    loadContent(menuItem.dataset.id);
}

// 更新面包屑
function updateBreadcrumb(text) {
    document.querySelector('.breadcrumb').innerHTML = `
        <span class="breadcrumb-item">首页</span>
        <span class="breadcrumb-item">${text}</span>
    `;
}

// 加载内容
function loadContent(menuId) {
    const contentBody = document.querySelector('.content-body');
    // 这里应该根据menuId加载对应的组件或页面
    contentBody.innerHTML = `<h2>正在加载 ${menuId} 内容...</h2>`;
}

// 处理设置按钮点击
function handleSettings() {
    // 实现设置功能
    console.log('打开设置面板');
}

// 处理退出登录
function handleLogout() {
    if (confirm('确定要退出登录吗？')) {
        // 清除localStorage中的登录信息
        localStorage.removeItem('isLoggedIn');
        localStorage.removeItem('userRole');
        localStorage.removeItem('userInfo');
        localStorage.removeItem('userPhone');
        localStorage.removeItem('accessToken');
        
        // 跳转到登录页面
        window.location.href = '../LoginRegister/Login/Login.html';
    }
}

// 处理通知点击
function handleNotification() {
    // 实现通知面板显示逻辑
    console.log('打开通知面板');
}

// 初始化用户信息显示
// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init); 