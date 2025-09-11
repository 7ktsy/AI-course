
// 通用验证函数
function validateInput(input, errorId, message, validationFn = null) {
    const errorElement = document.getElementById(errorId);
    const value = input.value.trim();
    let isValid = true;

    if (!value) {
        isValid = false;
        message = "此项为必填项";
    } else if (validationFn && !validationFn(value)) {
        isValid = false;
    }

    if (!isValid) {
        input.classList.add("input-error");
        errorElement.textContent = message;
        errorElement.style.visibility = "visible"; // 显示错误信息
        return false;
    } else {
        input.classList.remove("input-error");
        errorElement.style.visibility = "hidden"; // 隐藏错误信息
        return true;
    }
}

// 验证手机号格式
function validatePhone(value) {
    // 不用验证手机号格式，直接返回true
    return true;
    // const phoneRegex = /^1[3-9]\d{9}$/; // 简单的手机号正则表达式
    // return phoneRegex.test(value);
}

// 验证密码格式
function validatePassword(value) {
    // 简化密码验证，只检查长度
    return value.length >= 6;
    // const passwordRegex = /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{6,}$/; // 至少包含一个字母和一个数字，长度至少6位
    // return passwordRegex.test(value);
}

// 验证验证码
function validateCaptcha(value) {
    // 验证码验证已被禁用
    return true;
}

// 切换表单显示
function showForm(role) {
    // 隐藏所有表单
    document.getElementById('studentForm').style.display = 'none';
    document.getElementById('teacherForm').style.display = 'none';
    document.getElementById('adminForm').style.display = 'none';

    // 显示对应的表单
    document.getElementById(role + 'Form').style.display = 'block';
}

// 刷新验证码
function refreshCaptcha(imgId) {
    // 验证码刷新功能已被禁用
    console.log('验证码功能已被禁用');
}

// 表单提交处理
function handleSubmit(event, formId) {
    event.preventDefault(); // 阻止表单默认提交行为
    
    // 防止重复提交
    if (window.isSubmitting) {
        console.log('正在提交中，请稍候...');
        return false;
    }
    window.isSubmitting = true;

    let isValid = true;
    let formData = {};
    const role = formId.replace('Form', '');

    if (formId === 'studentForm') {
        // 验证学生手机号
        const phoneInput = document.getElementById("studentPhone");
        isValid = validateInput(phoneInput, "studentPhoneError", "请输入有效的手机号", validatePhone) && isValid;

        // 验证学生密码
        const passwordInput = document.getElementById("studentPassword");
        isValid = validateInput(passwordInput, "studentPasswordError", "密码长度至少6位", validatePassword) && isValid;

        // 验证码验证已被禁用
        // const captchaInput = document.getElementById("studentCaptcha");
        // isValid = validateInput(captchaInput, "studentCaptchaError", "验证码错误", validateCaptcha) && isValid;
    } else if (formId === 'teacherForm') {
        // 验证教师手机号
        const phoneInput = document.getElementById("teacherPhone");
        isValid = validateInput(phoneInput, "teacherPhoneError", "请输入有效的手机号", validatePhone) && isValid;

        // 验证教师密码
        const passwordInput = document.getElementById("teacherPassword");
        isValid = validateInput(passwordInput, "teacherPasswordError", "密码长度至少6位", validatePassword) && isValid;

        // 验证码验证已被禁用
        // const captchaInput = document.getElementById("teacherCaptcha");
        // isValid = validateInput(captchaInput, "teacherCaptchaError", "验证码错误", validateCaptcha) && isValid;
    } else if (formId === 'adminForm') {
        // 验证管理员账号
        const usernameInput = document.getElementById("adminUsername");
        isValid = validateInput(usernameInput, "adminUsernameError", "请输入管理员账号") && isValid;

        // 验证管理员密码
        const passwordInput = document.getElementById("adminPassword");
        isValid = validateInput(passwordInput, "adminPasswordError", "密码长度至少6位", validatePassword) && isValid;

        // 验证码验证已被禁用
        // const captchaInput = document.getElementById("adminCaptcha");
        // isValid = validateInput(captchaInput, "adminCaptchaError", "验证码错误", validateCaptcha) && isValid;
    }

    if (!isValid) {
        // 找到第一个错误输入框并聚焦
        const firstError = document.querySelector(".input-error");
        if (firstError) firstError.focus();
        window.isSubmitting = false; // 重置提交状态
        return false;
    }

    try {
        // 在文件顶部添加此辅助函数
        function getFieldValue(fieldId) {
            const el = document.getElementById(fieldId);
            return el ? el.value.trim() : ''; // 安全获取值并去除空格
        }
        // 新增：构建请求数据
        const requestBody = {
            phone: role === 'admin' ? getFieldValue(`${role}Username`) : getFieldValue(`${role}Phone`),
            password: getFieldValue(`${role}Password`)
        };

        // 新增：实际提交逻辑
        console.log('准备发送登录请求:', requestBody);
        fetch('http://localhost:8000/user/login', { // 确保URL正确
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
            // 移除 credentials: 'include' 来避免CORS问题
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                console.log('登录成功，服务器返回:', data);
                //alert('登录成功！');
                
                // 获取后端返回的实际角色
                const actualRole = data.data && data.data.user ? data.data.user.role : role;
                
                // 根据实际用户角色跳转到相应的layout界面
                let redirectUrl;
                switch(actualRole) {
                    case 'student':
                        redirectUrl = '../../WorkStation/Layout.html'; // 学生工作台
                        break;
                    case 'teacher':
                        redirectUrl = '../../WorkStation/Layout.html'; // 教师工作台
                        break;
                    case 'admin':
                        redirectUrl = '../../WorkStation/Layout.html'; // 管理员工作台
                        break;
                    default:
                        redirectUrl = '../../HomePage.html'; // 默认回到首页
                }
                
                // 可以在跳转前保存用户信息到localStorage
                // 注意：后端返回的角色信息在data.user.role中，使用实际的角色而不是前端选择的角色
                localStorage.setItem('userRole', actualRole);
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('userPhone', requestBody.phone);
                
                // 保存访问令牌
                if (data.data && data.data.access_token) {
                    localStorage.setItem('accessToken', data.data.access_token);
                }
                
                // 保存用户信息
                if (data.data && data.data.user) {
                    const userInfo = {
                        id: data.data.user.id,
                        name: data.data.user.username,
                        phone: data.data.user.phone,
                        role: data.data.user.role,
                        university: data.data.user.university,
                        title: data.data.user.title,
                        department: data.data.user.department
                    };
                    localStorage.setItem('userInfo', JSON.stringify(userInfo));
                } else {
                    // 如果后端没有返回用户信息，创建基本的用户信息
                    const basicUserInfo = {
                        phone: requestBody.phone,
                        role: actualRole,
                        name: actualRole === 'admin' ? '管理员' : (actualRole === 'teacher' ? '教师' : '学生')
                    };
                    localStorage.setItem('userInfo', JSON.stringify(basicUserInfo));
                }
                
                console.log('准备跳转到:', redirectUrl);
                window.location.href = redirectUrl;
            })
            .catch(error => {
                window.isSubmitting = false; // 重置提交状态
                alert(`登录失败: ${error.message}`);
                console.error('登录错误:', error);
            });
    } catch (error) {
        window.isSubmitting = false; // 重置提交状态
        alert("登录失败：" + error.message);
        console.error('登录失败:', error);
    }
    return false;
}

// 页面加载完成后初始化
document.addEventListener("DOMContentLoaded", function () {
    // 检查是否已经初始化过，避免重复绑定
    if (window.loginInitialized) {
        return;
    }
    window.loginInitialized = true;
    
    // 为每个角色按钮添加事件监听器
    document.getElementById('studentLoginBtn').addEventListener('click', function () {
        showForm('student');
    });

    document.getElementById('teacherLoginBtn').addEventListener('click', function () {
        showForm('teacher');
    });

    document.getElementById('adminLoginBtn').addEventListener('click', function () {
        showForm('admin');
    });

    // 默认显示学生登录表单
    showForm('student');

    // 为每个表单添加提交事件
    document.getElementById('studentForm').addEventListener("submit", function (event) {
        handleSubmit(event, 'studentForm');
    });

    document.getElementById('teacherForm').addEventListener("submit", function (event) {
        handleSubmit(event, 'teacherForm');
    });

    document.getElementById('adminForm').addEventListener("submit", function (event) {
        handleSubmit(event, 'adminForm');
    });
});