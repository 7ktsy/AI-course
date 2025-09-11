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
    const phoneRegex = /^1[3-9]\d{9}$/; // 简单的手机号正则表达式
    return phoneRegex.test(value);
}

// 验证密码格式
function validatePassword(value) {
    const passwordRegex = /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{6,}$/; // 至少包含一个字母和一个数字，长度至少6位
    return passwordRegex.test(value);
}

// 验证两次密码是否一致
function validatePasswordsMatch(password, confirmPassword) {
    return password === confirmPassword;
}

// 表单提交处理
function handleSubmit(event) {
    event.preventDefault(); // 阻止表单默认提交行为

    let isValid = true;

    // 验证手机号
    const phoneInput = document.getElementById("phone");
    isValid = validateInput(phoneInput, "phoneError", "请输入有效的手机号", validatePhone) && isValid;

    // 验证密码
    const passwordInput = document.getElementById("password");
    isValid = validateInput(passwordInput, "passwordError", "密码至少包含一个字母和一个数字，长度至少6位", validatePassword) && isValid;

    // 验证确认密码
    const confirmPasswordInput = document.getElementById("confirmPassword");
    isValid = validateInput(confirmPasswordInput, "confirmPasswordError", "两次密码不一致", () => validatePasswordsMatch(passwordInput.value, confirmPasswordInput.value)) && isValid;

    // 验证验证码
    const captchaInput = document.getElementById("studentCaptcha");
    isValid = validateInput(captchaInput, "captchaError", "请输入验证码") && isValid;

    if (!isValid) {
        // 找到第一个错误输入框并聚焦
        const firstError = document.querySelector(".input-error");
        if (firstError) firstError.focus();
    }

    if (isValid) {
        alert("表单验证通过，可以提交！");
        // 这里可以继续处理表单提交逻辑，例如发送数据到服务器
    }
}

// 页面加载完成后初始化
document.addEventListener("DOMContentLoaded", function() {
    // 为提交按钮添加点击事件
    const submitButton = document.getElementById("submitBtn");
    if (submitButton) {
        submitButton.addEventListener("click", handleSubmit);
    } else {
        console.error("提交按钮未找到，请检查HTML代码");
    }
});