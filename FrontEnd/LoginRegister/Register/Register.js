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

function validateUsername(value) {
    // 去除首尾空格后检查长度
    return value.trim() !== "";
}
// 验证大学名称是否在列表中
function validateUniversity(value) {
    return universities.some(uni => uni === value);
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
// 表单提交处理
function handleSubmit(formId) {
    const form = document.getElementById(formId);
    let isValid = true;
    const role = formId.replace('Form', ''); // studentForm -> student

    if (formId === 'studentForm') {
        // 验证用户名
        const usernameInput = document.getElementById("studentUsername");
        isValid = validateInput(usernameInput, "studentusernameError",
            "昵称不能为空", validateUsername) && isValid;

        // 验证大学
        const universityInput = document.getElementById("studentUniversity");
        isValid = validateInput(universityInput, "studentUniversityError",
            "请输入有效的大学名称", validateUniversity) && isValid;

        // 验证手机号
        const phoneInput = document.getElementById("studentPhone");
        isValid = validateInput(phoneInput, "studentPhoneError",
            "请输入有效的手机号", validatePhone) && isValid;

        // 验证密码
        const passwordInput = document.getElementById("studentPassword");
        isValid = validateInput(passwordInput, "studentPasswordError", 
            "密码至少包含一个字母和一个数字，长度至少6位", validatePassword) && isValid;

        // 验证确认密码
        const confirmPasswordInput = document.getElementById("studentConfirmPassword");
        isValid = validateInput(confirmPasswordInput, "studentConfirmPasswordError",
            "两次密码不一致", () => validatePasswordsMatch(passwordInput.value, confirmPasswordInput.value)) && isValid;

        // 验证验证码
        const captchaInput = document.getElementById("studentCaptcha");
        isValid = validateInput(captchaInput, "studentCaptchaError", "请输入验证码") && isValid;
    } 
    else if (formId === 'teacherForm') {
        // 验证用户名
        const usernameInput = document.getElementById("teacherUsername");
        isValid = validateInput(usernameInput, "teacherusernameError",
            "昵称不能为空", validateUsername) && isValid;

        // 验证大学
        const universityInput = document.getElementById("teacherUniversity");
        isValid = validateInput(universityInput, "teacherUniversityError",
            "请输入有效的大学名称", validateUniversity) && isValid;

        // 验证手机号
        const phoneInput = document.getElementById("teacherPhone");
        isValid = validateInput(phoneInput, "teacherPhoneError",
            "请输入有效的手机号", validatePhone) && isValid;

        // 验证密码
        const passwordInput = document.getElementById("teacherPassword");
        isValid = validateInput(passwordInput, "teacherPasswordError", 
            "密码至少包含一个字母和一个数字，长度至少6位", validatePassword) && isValid;

        // 验证确认密码
        const confirmPasswordInput = document.getElementById("teacherConfirmPassword");
        isValid = validateInput(confirmPasswordInput, "teacherConfirmPasswordError",
            "两次密码不一致", () => validatePasswordsMatch(passwordInput.value, confirmPasswordInput.value)) && isValid;

        // 验证职称
        const titleInput = document.getElementById("teacherTitle");
        isValid = validateInput(titleInput, "teacherTitleError", "请输入有效的职称") && isValid;

        // 验证系部
        const departmentInput = document.getElementById("teacherDepartment");
        isValid = validateInput(departmentInput, "teacherDepartmentError", "请输入有效的系部") && isValid;

        // 验证验证码
        const captchaInput = document.getElementById("teacherCaptcha");
        isValid = validateInput(captchaInput, "teacherCaptchaError", "请输入验证码") && isValid;
    }

    if (!isValid) {
        const firstError = document.querySelector(".input-error");
        if (firstError) firstError.focus();
        return false;
    }

    try {
        // 构建请求体的辅助函数
        const getFieldValue = (fieldId) => {
            const el = document.getElementById(fieldId);
            return el ? el.value.trim() : '';
        };

        // 根据角色构建不同的请求体
        const requestBody = {
            username: role === 'student' ? getFieldValue("studentUsername") : getFieldValue("teacherUsername"), // 修正这里
            password: getFieldValue(`${role}Password`),
            phone: getFieldValue(`${role}Phone`),
            role: role,
            university: getFieldValue(`${role}University`),
            title: role === 'teacher' ? getFieldValue("teacherTitle") : "",
            department: role === 'teacher' ? getFieldValue("teacherDepartment") : "",
            captcha: getFieldValue(`${role}Captcha`)
        };

        console.log('即将提交的表单数据:', {
            formId: formId,
            requestBody: requestBody,
            timestamp: new Date().toISOString()
        });

        const shouldSubmit = confirm(`确定要提交吗?\n\n可以在控制台查看数据:\n${JSON.stringify(requestBody, null, 2)}`);
        if (!shouldSubmit) {
            console.log('用户取消了提交');
            return false;
        }
        fetch('http://localhost:8000/user/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(requestBody),
            credentials: 'include'
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(result => {
            alert(result.message || '注册成功！');
            window.location.href = '../Login/Login.html';
        })
        .catch(error => {
            alert(`注册失败: ${error.message}`);
            console.error('注册错误:', error);
        });

    } catch (error) {
        alert(`注册失败: ${error.message}`);
        console.error('注册错误:', error);
    }
    
    return false;
}

// 自动完成功能（移除实时验证）
function autocomplete(inp, arr) {
    let currentFocus;

    inp.addEventListener("input", function(e) {
        const val = this.value;
        closeAllLists();

        if (!val) { return false; }
        currentFocus = -1;

        const dropdown = document.createElement("DIV");
        dropdown.setAttribute("id", this.id + "autocomplete-list");
        dropdown.setAttribute("class", "autocomplete-items");
        this.parentNode.appendChild(dropdown);

        // 过滤并显示匹配的大学
        const matches = arr.filter(item => 
            item.toLowerCase().includes(val.toLowerCase())
        ).slice(0, 10);

        if (matches.length === 0) {
            const noResult = document.createElement("DIV");
            noResult.innerHTML = "未找到匹配的大学";
            dropdown.appendChild(noResult);
        } else {
            matches.forEach(match => {
                const item = document.createElement("DIV");
                const startIdx = match.toLowerCase().indexOf(val.toLowerCase());
                if (startIdx !== -1) {
                    item.innerHTML = match.substr(0, startIdx) + 
                                   '<span style="color: rgb(255, 0, 0)">' + 
                                   match.substr(startIdx, val.length) + 
                                   '</span>' + 
                                   match.substr(startIdx + val.length);
                } else {
                    item.innerHTML = match;
                }
                item.innerHTML += "<input type='hidden' value='" + match + "'>";

                item.addEventListener("click", function(e) {
                    inp.value = this.getElementsByTagName("input")[0].value;
                    closeAllLists();
                });

                dropdown.appendChild(item);
            });
        }
    });

    inp.addEventListener("keydown", function(e) {
        let items = document.getElementById(this.id + "autocomplete-list");
        if (items) items = items.getElementsByTagName("div");

        if (e.key === "ArrowDown") {
            currentFocus++;
            addActive(items);
        } else if (e.key === "ArrowUp") {
            currentFocus--;
            addActive(items);
        } else if (e.key === "Enter") {
            e.preventDefault();
            if (currentFocus > -1 && items) {
                items[currentFocus].click();
            }
        }
    });

    function addActive(items) {
        if (!items) return false;
        removeActive(items);
        if (currentFocus >= items.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (items.length - 1);
        items[currentFocus].classList.add("autocomplete-active");
    }

    function removeActive(items) {
        for (let i = 0; i < items.length; i++) {
            items[i].classList.remove("autocomplete-active");
        }
    }

    function closeAllLists(elmnt) {
        const items = document.getElementsByClassName("autocomplete-items");
        for (let i = 0; i < items.length; i++) {
            if (elmnt != items[i] && elmnt != inp) {
                items[i].parentNode.removeChild(items[i]);
            }
        }
    }

    document.addEventListener("click", function(e) {
        closeAllLists(e.target);
    });
}

// 确保school.js加载完成
function checkSchoolJSLoaded() {
    if (typeof schoolList === 'undefined') {
        console.error('school.js未正确加载');
        return false;
    }
    return true;
}

// 显示对应表单
function showForm(role) {
    document.getElementById('studentForm').style.display = 'none';
    document.getElementById('teacherForm').style.display = 'none';
    document.getElementById('adminForm').style.display = 'none';

    document.getElementById(role + 'Form').style.display = 'block';
}

// 刷新验证码
function refreshCaptcha(imgId) {
    var img = document.getElementById(imgId);
    img.src = '/captcha?' + new Date().getTime();
}

// 页面加载完成后初始化
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('studentRoleBtn').focus();

    // 为所有表单添加提交事件
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener("submit", function(e) {
            if (!handleSubmit(this.id)) {
                e.preventDefault();
            }
        });
    });

    if (!checkSchoolJSLoaded()) {
        console.error("无法加载大学数据");
        return;
    }

    // 将大学列表存储在全局变量中
    universities = schoolList[0].school.map(school => school.name);

    const studentUniversityInput = document.getElementById("studentUniversity");
    if (studentUniversityInput) {
        autocomplete(studentUniversityInput, universities);
    }

    const teacherUniversityInput = document.getElementById("teacherUniversity");
    if (teacherUniversityInput) {
        autocomplete(teacherUniversityInput, universities);
    }

    // 默认显示学生表单
    showForm('student');
});