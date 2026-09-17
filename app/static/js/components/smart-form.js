/**
 * 智能表单组件
 * 提供自动验证、动态字段、多步骤表单功能
 */

class SmartForm extends BaseComponent {
    get defaultOptions() {
        return {
            autoValidate: true,
            showErrors: true,
            saveDraft: true,
            multiStep: false,
            submitOnEnter: true,
            realTimeValidation: true,
            errorDelay: 300,
            draftKey: null,
            validationRules: {},
            customValidators: {},
            onValidate: null,
            onSubmit: null,
            onStepChange: null
        };
    }
    
    init() {
        super.init();
        
        // 表单状态
        this.isValid = false;
        this.isDirty = false;
        this.currentStep = 0;
        this.totalSteps = 1;
        this.validationErrors = new Map();
        this.draftTimer = null;
        
        // 查找表单元素
        this.form = this.element.tagName === 'FORM' ? 
            this.element : this.$('form');
        
        if (!this.form) {
            this.error('No form element found');
            return;
        }
        
        // 初始化组件
        this.initializeValidation();
        this.initializeMultiStep();
        this.initializeDraftSaving();
        this.bindEvents();
        this.loadDraft();
    }
    
    /**
     * 初始化验证系统
     */
    initializeValidation() {
        // 内置验证规则
        this.builtInValidators = {
            required: (value, rule) => {
                return value !== null && value !== undefined && value.toString().trim() !== '';
            },
            
            email: (value, rule) => {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return !value || emailRegex.test(value);
            },
            
            minLength: (value, rule) => {
                return !value || value.length >= rule.value;
            },
            
            maxLength: (value, rule) => {
                return !value || value.length <= rule.value;
            },
            
            pattern: (value, rule) => {
                const regex = new RegExp(rule.value);
                return !value || regex.test(value);
            },
            
            number: (value, rule) => {
                return !value || !isNaN(Number(value));
            },
            
            min: (value, rule) => {
                return !value || Number(value) >= rule.value;
            },
            
            max: (value, rule) => {
                return !value || Number(value) <= rule.value;
            },
            
            url: (value, rule) => {
                try {
                    return !value || Boolean(new URL(value));
                } catch {
                    return false;
                }
            },
            
            phone: (value, rule) => {
                const phoneRegex = /^[\d\s\-\+\(\)]+$/;
                return !value || phoneRegex.test(value);
            },
            
            stockCode: (value, rule) => {
                // 6位数字股票代码
                const stockRegex = /^\d{6}$/;
                return !value || stockRegex.test(value);
            }
        };
        
        // 获取验证规则
        this.parseValidationRules();
    }
    
    /**
     * 解析验证规则
     */
    parseValidationRules() {
        const fields = this.$$('[data-validate], [required], input, select, textarea');
        
        fields.forEach(field => {
            const rules = [];
            
            // HTML5原生验证
            if (field.required) {
                rules.push({ type: 'required', message: '此字段为必填项' });
            }
            
            if (field.type === 'email') {
                rules.push({ type: 'email', message: '请输入有效的邮箱地址' });
            }
            
            if (field.minLength) {
                rules.push({ 
                    type: 'minLength', 
                    value: field.minLength,
                    message: `最少输入${field.minLength}个字符`
                });
            }
            
            if (field.maxLength) {
                rules.push({ 
                    type: 'maxLength', 
                    value: field.maxLength,
                    message: `最多输入${field.maxLength}个字符`
                });
            }
            
            if (field.pattern) {
                rules.push({ 
                    type: 'pattern', 
                    value: field.pattern,
                    message: '格式不正确'
                });
            }
            
            // 自定义验证规则
            const customRules = field.dataset.validate;
            if (customRules) {
                try {
                    const parsedRules = JSON.parse(customRules);
                    rules.push(...parsedRules);
                } catch (e) {
                    // 简单规则格式：required|email|minLength:6
                    const simpleRules = customRules.split('|');
                    simpleRules.forEach(rule => {
                        const [type, value] = rule.split(':');
                        rules.push({ 
                            type: type.trim(), 
                            value: value ? value.trim() : null,
                            message: field.dataset[`${type}Message`] || `${type}验证失败`
                        });
                    });
                }
            }
            
            if (rules.length > 0) {
                this.options.validationRules[field.name || field.id] = rules;
            }
        });
    }
    
    /**
     * 初始化多步骤表单
     */
    initializeMultiStep() {
        const steps = this.$$('.form-step, [data-step]');
        
        if (steps.length > 1) {
            this.options.multiStep = true;
            this.totalSteps = steps.length;
            
            // 隐藏除第一步外的所有步骤
            steps.forEach((step, index) => {
                step.style.display = index === 0 ? 'block' : 'none';
                step.dataset.stepIndex = index;
            });
            
            // 创建步骤指示器
            this.createStepIndicator();
            
            // 创建导航按钮
            this.createStepNavigation();
        }
    }
    
    /**
     * 创建步骤指示器
     */
    createStepIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'form-step-indicator';
        indicator.innerHTML = `
            <div class="step-progress">
                ${Array.from({length: this.totalSteps}, (_, i) => `
                    <div class="step-item ${i === 0 ? 'active' : ''}" data-step="${i}">
                        <div class="step-number">${i + 1}</div>
                        <div class="step-title">步骤 ${i + 1}</div>
                    </div>
                `).join('')}
            </div>
        `;
        
        this.form.insertBefore(indicator, this.form.firstChild);
        this.stepIndicator = indicator;
    }
    
    /**
     * 创建步骤导航
     */
    createStepNavigation() {
        const navigation = document.createElement('div');
        navigation.className = 'form-step-navigation';
        navigation.innerHTML = `
            <button type="button" class="btn btn-secondary step-prev" style="display: none;">
                上一步
            </button>
            <button type="button" class="btn btn-primary step-next">
                下一步
            </button>
            <button type="submit" class="btn btn-success step-submit" style="display: none;">
                提交
            </button>
        `;
        
        this.form.appendChild(navigation);
        
        // 绑定导航事件
        this.$('.step-prev').addEventListener('click', () => this.prevStep());
        this.$('.step-next').addEventListener('click', () => this.nextStep());
    }
    
    /**
     * 初始化草稿保存
     */
    initializeDraftSaving() {
        if (this.options.saveDraft) {
            this.draftKey = this.options.draftKey || 
                `form_draft_${window.location.pathname}_${this.form.id || 'default'}`;
        }
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 表单提交
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        
        // 实时验证
        if (this.options.realTimeValidation) {
            this.bindValidationEvents();
        }
        
        // 草稿保存
        if (this.options.saveDraft) {
            this.bindDraftEvents();
        }
        
        // 回车提交
        if (this.options.submitOnEnter) {
            this.form.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey && 
                    !['TEXTAREA'].includes(e.target.tagName)) {
                    if (this.options.multiStep) {
                        if (this.currentStep < this.totalSteps - 1) {
                            e.preventDefault();
                            this.nextStep();
                        }
                    } else {
                        this.form.requestSubmit();
                    }
                }
            });
        }
    }
    
    /**
     * 绑定验证事件
     */
    bindValidationEvents() {
        const fields = this.$$('input, select, textarea');
        
        fields.forEach(field => {
            // 失焦验证
            field.addEventListener('blur', () => {
                this.validateField(field);
            });
            
            // 输入验证（防抖）
            let validationTimeout;
            field.addEventListener('input', () => {
                clearTimeout(validationTimeout);
                validationTimeout = setTimeout(() => {
                    this.validateField(field);
                    this.markDirty();
                }, this.options.errorDelay);
            });
        });
    }
    
    /**
     * 绑定草稿事件
     */
    bindDraftEvents() {
        const fields = this.$$('input, select, textarea');
        
        fields.forEach(field => {
            field.addEventListener('input', () => {
                this.scheduleDraftSave();
            });
        });
        
        // 页面卸载前保存草稿
        window.addEventListener('beforeunload', () => {
            this.saveDraft();
        });
    }
    
    /**
     * 验证单个字段
     */
    validateField(field) {
        const fieldName = field.name || field.id;
        const rules = this.options.validationRules[fieldName] || [];
        const value = field.value;
        const errors = [];
        
        // 执行验证规则
        for (const rule of rules) {
            let isValid = false;
            
            // 内置验证器
            if (this.builtInValidators[rule.type]) {
                isValid = this.builtInValidators[rule.type](value, rule);
            }
            // 自定义验证器
            else if (this.options.customValidators[rule.type]) {
                isValid = this.options.customValidators[rule.type](value, rule, field);
            }
            
            if (!isValid) {
                errors.push(rule.message || `${rule.type}验证失败`);
            }
        }
        
        // 更新错误状态
        if (errors.length > 0) {
            this.validationErrors.set(fieldName, errors);
            this.showFieldErrors(field, errors);
        } else {
            this.validationErrors.delete(fieldName);
            this.clearFieldErrors(field);
        }
        
        // 触发验证事件
        this.emit('fieldValidate', {
            field: field,
            valid: errors.length === 0,
            errors: errors
        });
        
        // 更新表单状态
        this.updateFormState();
    }
    
    /**
     * 显示字段错误
     */
    showFieldErrors(field, errors) {
        if (!this.options.showErrors) return;
        
        // 移除现有错误
        this.clearFieldErrors(field);
        
        // 添加错误样式
        field.classList.add('is-invalid');
        
        // 创建错误容器
        const errorContainer = document.createElement('div');
        errorContainer.className = 'invalid-feedback';
        errorContainer.innerHTML = errors.map(error => 
            `<div class="error-message">${error}</div>`
        ).join('');
        
        // 插入错误信息
        field.parentNode.insertBefore(errorContainer, field.nextSibling);
        
        // 添加数据属性用于后续清理
        errorContainer.dataset.fieldError = field.name || field.id;
    }
    
    /**
     * 清除字段错误
     */
    clearFieldErrors(field) {
        field.classList.remove('is-invalid');
        
        const errorContainer = field.parentNode.querySelector(
            `[data-field-error="${field.name || field.id}"]`
        );
        
        if (errorContainer) {
            errorContainer.remove();
        }
    }
    
    /**
     * 验证整个表单
     */
    validateForm() {
        const fields = this.$$('input, select, textarea');
        let hasErrors = false;
        
        fields.forEach(field => {
            this.validateField(field);
        });
        
        // 检查是否有错误
        hasErrors = this.validationErrors.size > 0;
        
        // 自定义验证回调
        if (this.options.onValidate) {
            const customResult = this.options.onValidate(this.getFormData(), this);
            if (customResult === false) {
                hasErrors = true;
            }
        }
        
        this.isValid = !hasErrors;
        this.updateFormState();
        
        this.emit('validate', {
            valid: this.isValid,
            errors: Array.from(this.validationErrors.entries())
        });
        
        return this.isValid;
    }
    
    /**
     * 更新表单状态
     */
    updateFormState() {
        const submitBtn = this.$('[type="submit"], .step-submit');
        
        if (submitBtn) {
            submitBtn.disabled = !this.isValid;
        }
        
        // 更新表单CSS类
        this.form.classList.toggle('is-valid', this.isValid);
        this.form.classList.toggle('is-invalid', !this.isValid);
        this.form.classList.toggle('is-dirty', this.isDirty);
    }
    
    /**
     * 标记表单为已修改
     */
    markDirty() {
        if (!this.isDirty) {
            this.isDirty = true;
            this.emit('dirty');
            this.updateFormState();
        }
    }
    
    /**
     * 获取表单数据
     */
    getFormData() {
        const formData = new FormData(this.form);
        const data = {};
        
        formData.forEach((value, key) => {
            if (data[key]) {
                // 处理多值字段（如复选框）
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        });
        
        return data;
    }
    
    /**
     * 设置表单数据
     */
    setFormData(data) {
        Object.entries(data).forEach(([key, value]) => {
            const field = this.form.elements[key];
            if (field) {
                if (field.type === 'checkbox' || field.type === 'radio') {
                    field.checked = Boolean(value);
                } else {
                    field.value = value;
                }
            }
        });
        
        this.markDirty();
    }
    
    /**
     * 下一步
     */
    async nextStep() {
        if (!this.options.multiStep || this.currentStep >= this.totalSteps - 1) {
            return;
        }
        
        // 验证当前步骤
        const currentStepFields = this.getCurrentStepFields();
        let isStepValid = true;
        
        currentStepFields.forEach(field => {
            this.validateField(field);
            if (this.validationErrors.has(field.name || field.id)) {
                isStepValid = false;
            }
        });
        
        if (!isStepValid) {
            this.showStepError('请修正错误后继续');
            return;
        }
        
        // 步骤变更事件
        if (this.options.onStepChange) {
            const result = await this.options.onStepChange(
                this.currentStep + 1, 
                this.currentStep, 
                this.getFormData()
            );
            
            if (result === false) {
                return;
            }
        }
        
        // 切换步骤
        this.switchStep(this.currentStep + 1);
    }
    
    /**
     * 上一步
     */
    async prevStep() {
        if (!this.options.multiStep || this.currentStep <= 0) {
            return;
        }
        
        // 步骤变更事件
        if (this.options.onStepChange) {
            const result = await this.options.onStepChange(
                this.currentStep - 1, 
                this.currentStep, 
                this.getFormData()
            );
            
            if (result === false) {
                return;
            }
        }
        
        this.switchStep(this.currentStep - 1);
    }
    
    /**
     * 切换到指定步骤
     */
    switchStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.totalSteps) {
            return;
        }
        
        const steps = this.$$('.form-step, [data-step]');
        
        // 隐藏当前步骤
        if (steps[this.currentStep]) {
            steps[this.currentStep].style.display = 'none';
        }
        
        // 显示新步骤
        if (steps[stepIndex]) {
            steps[stepIndex].style.display = 'block';
        }
        
        // 更新步骤指示器
        this.updateStepIndicator(stepIndex);
        
        // 更新导航按钮
        this.updateStepNavigation(stepIndex);
        
        this.currentStep = stepIndex;
        
        this.emit('stepChange', {
            currentStep: this.currentStep,
            totalSteps: this.totalSteps
        });
    }
    
    /**
     * 更新步骤指示器
     */
    updateStepIndicator(activeStep) {
        if (!this.stepIndicator) return;
        
        const stepItems = this.stepIndicator.$$('.step-item');
        
        stepItems.forEach((item, index) => {
            item.classList.toggle('active', index === activeStep);
            item.classList.toggle('completed', index < activeStep);
        });
    }
    
    /**
     * 更新步骤导航
     */
    updateStepNavigation(currentStep) {
        const prevBtn = this.$('.step-prev');
        const nextBtn = this.$('.step-next');
        const submitBtn = this.$('.step-submit');
        
        if (prevBtn) {
            prevBtn.style.display = currentStep > 0 ? 'inline-block' : 'none';
        }
        
        if (nextBtn) {
            nextBtn.style.display = currentStep < this.totalSteps - 1 ? 'inline-block' : 'none';
        }
        
        if (submitBtn) {
            submitBtn.style.display = currentStep === this.totalSteps - 1 ? 'inline-block' : 'none';
        }
    }
    
    /**
     * 获取当前步骤的字段
     */
    getCurrentStepFields() {
        const currentStepElement = this.$(`[data-step-index="${this.currentStep}"]`);
        
        if (currentStepElement) {
            return currentStepElement.querySelectorAll('input, select, textarea');
        }
        
        return [];
    }
    
    /**
     * 显示步骤错误
     */
    showStepError(message) {
        // 创建或更新错误提示
        let errorAlert = this.$('.step-error-alert');
        
        if (!errorAlert) {
            errorAlert = document.createElement('div');
            errorAlert.className = 'alert alert-danger step-error-alert';
            
            const currentStep = this.$(`[data-step-index="${this.currentStep}"]`);
            if (currentStep) {
                currentStep.insertBefore(errorAlert, currentStep.firstChild);
            }
        }
        
        errorAlert.textContent = message;
        errorAlert.style.display = 'block';
        
        // 3秒后自动隐藏
        setTimeout(() => {
            errorAlert.style.display = 'none';
        }, 3000);
    }
    
    /**
     * 处理表单提交
     */
    async handleSubmit(e) {
        e.preventDefault();
        
        // 验证表单
        if (!this.validateForm()) {
            this.emit('submitError', { errors: Array.from(this.validationErrors.entries()) });
            return;
        }
        
        const formData = this.getFormData();
        
        // 自定义提交处理
        if (this.options.onSubmit) {
            try {
                const result = await this.options.onSubmit(formData, this);
                
                if (result === false) {
                    return;
                }
            } catch (error) {
                this.emit('submitError', { error });
                return;
            }
        }
        
        // 清除草稿
        this.clearDraft();
        
        this.emit('submit', { data: formData });
        
        // 如果没有自定义处理，执行默认提交
        if (!this.options.onSubmit) {
            this.form.submit();
        }
    }
    
    /**
     * 计划草稿保存
     */
    scheduleDraftSave() {
        if (!this.options.saveDraft) return;
        
        clearTimeout(this.draftTimer);
        this.draftTimer = setTimeout(() => {
            this.saveDraft();
        }, 2000); // 2秒延迟保存
    }
    
    /**
     * 保存草稿
     */
    saveDraft() {
        if (!this.options.saveDraft || !this.isDirty) return;
        
        try {
            const draftData = {
                data: this.getFormData(),
                timestamp: Date.now(),
                currentStep: this.currentStep
            };
            
            localStorage.setItem(this.draftKey, JSON.stringify(draftData));
            this.emit('draftSave', draftData);
        } catch (error) {
            this.error('Failed to save draft:', error);
        }
    }
    
    /**
     * 加载草稿
     */
    loadDraft() {
        if (!this.options.saveDraft) return;
        
        try {
            const draftData = localStorage.getItem(this.draftKey);
            
            if (draftData) {
                const parsed = JSON.parse(draftData);
                
                // 检查草稿是否过期（7天）
                const maxAge = 7 * 24 * 60 * 60 * 1000;
                if (Date.now() - parsed.timestamp > maxAge) {
                    this.clearDraft();
                    return;
                }
                
                // 询问用户是否恢复草稿
                if (confirm('发现未完成的表单草稿，是否恢复？')) {
                    this.setFormData(parsed.data);
                    
                    if (this.options.multiStep && parsed.currentStep !== undefined) {
                        this.switchStep(parsed.currentStep);
                    }
                    
                    this.emit('draftLoad', parsed);
                }
            }
        } catch (error) {
            this.error('Failed to load draft:', error);
        }
    }
    
    /**
     * 清除草稿
     */
    clearDraft() {
        if (!this.options.saveDraft) return;
        
        try {
            localStorage.removeItem(this.draftKey);
            this.emit('draftClear');
        } catch (error) {
            this.error('Failed to clear draft:', error);
        }
    }
    
    /**
     * 重置表单
     */
    reset() {
        this.form.reset();
        this.validationErrors.clear();
        this.isDirty = false;
        this.currentStep = 0;
        
        // 清除错误显示
        this.$$('.is-invalid').forEach(field => {
            this.clearFieldErrors(field);
        });
        
        // 重置多步骤
        if (this.options.multiStep) {
            this.switchStep(0);
        }
        
        // 清除草稿
        this.clearDraft();
        
        this.updateFormState();
        this.emit('reset');
    }
    
    /**
     * 添加自定义验证器
     */
    addValidator(name, validator) {
        this.options.customValidators[name] = validator;
    }
    
    /**
     * 获取验证状态
     */
    getValidationState() {
        return {
            isValid: this.isValid,
            isDirty: this.isDirty,
            errors: Array.from(this.validationErrors.entries())
        };
    }
}

// 注册组件
if (window.KronosComponents) {
    KronosComponents.register('smart_form', SmartForm, {
        autoValidate: true,
        showErrors: true,
        saveDraft: true
    });
}