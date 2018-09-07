# mywebapps  
一个实验性的网站，实现自己设想的web应用。目前使用的django框架。   
站点 http://www.mapy.tech

## 问卷调查
### 概述
用到的主要技术：  
后端：[django][]，[allauth][]，[crispy][]，[jinja2][]，[django-redis][]，[werkzeug][]，[uwsgi][]，nginx[]  
前端：[query][]，[bootstrap][]，[font-awesome][]

[werkzeug]: http://werkzeug.pocoo.org/
[allauth]: https://github.com/pennersr/django-allauth
[crispy]: https://django-crispy-forms.readthedocs.io/en/latest/index.html
[jinja2]: http://jinja.pocoo.org/
[uwsgi]: https://github.com/unbit/uwsgi-docs/blob/master/index.rst
[nginx]: http://nginx.org/
[jquery]: https://jquery.com/
[bootstrap]: http://www.bootcss.com/
[font-awesome]: https://fontawesome.io/
[django]: https://www.djangoproject.com/
[django-redis]: https://github.com/bluedazzle/django-redis-doc-chs/blob/master/source/index.rst


完成了主要功能，具体就是：  
  1. 账户功能，使用的allauth
  2. 问卷列表页
  3. 问卷发布页
  4. 问卷详情页，即参与调查页
  5. 结果展示页

可以想到的，待完成的工作：  
  1. 账户功能完善，添加profile页面，邮箱验证，验证码，第三方登录，allauth都可以实现
  2. 问卷功能完善
     * 设置问卷发布时间和结束时间
     * 设置问卷结果是否公开
     * 匿名或者实名投票
     * 保存未发布的问卷，修改未发布的问卷，还是使用发布页面的js完成
     * 结果展示，还未想好如何展示，只是统计了一下数量
     * 样式设置，几乎没什么样式
     * 代码调优
  3. 数据验证，数据有效性验证，前端添加验证代码，因为使用了ajax，后端也要添加验证代码
  4. 扩展，答题系统，添加正确答案字段即可

## 一些关键点
### 模型
项目虽然简单，模型关系还是比较复杂的，主要是为了充分利用数据库中已经存在的数据，减少数据冗余。  
主要的表：

  * 问卷表poll
  * 问题表question，问题三种类型：单选，多选，回答
  * 选项表choice，has_extra_data字段表示选项是否有额为数据，True表示类似"其他，请输入..."这样的选项
  * poll_question表，poll和question多对多关系表，添加index字段表示question在poll中的位置（顺序）
  * 投票表vote，poll_question和choice多对多关系表，添加index字段表示choice在poll_question中的位置（顺序）
  * 回答表answer，有一个poll_question外键，多对一关系
  * 选项的额外数据表extra_data，和vote是一对一关系
  * 用户表user，和vote是多对多关系，和answer是一对多关系，因为投票可以匿名可以实名，user字段可以为空
    user和poll是一对多关系，登录用户才可以发布问卷，user字段不能为空

### 模板
没有使用django自带的模板，因为据说jinja2性能更优
  1. 两种模板可以在同一个项目中使用，搜索顺序就是模板引擎定义的顺序，先搜索到哪个用哪个
  2. 因为jinja2默认没有缓存标签，参考[这里](https://www.kancloud.cn/manual/jinja2/70475)，添加缓存标签

### 视图
分页功能使用了两种方式：
  1. django提供的Paginator
  2. 只提供一个offset变量作为起始位置，每次取分页大小的数量即可

### 中间件
参考[这里](https://blog.csdn.net/qq_39687901/article/details/81387584)，实现了一个全局获得request对象的中间件

### 缓存
  1. 问卷列表页的数据缓存，用django的signals模块，当有有新的问卷post提交并save到数据库时，删除缓存
  2. 问卷详情页的模板片段缓存，jinja2需要扩展缓存标签，其中使用到了werkzeug库

### 前端
因为不是主攻前端，所以写的比较简陋   
遵守的一点是：后端查过的数据不会重复查询，记录到当前js环境变量里，或者保存到本地硬盘，减小服务器压力
  1. bootstrap 支持响应式
  2. crispy 用于表单渲染  
  3. font-awesome 提供一些图标
  4. 发布页的js，用到jquery，问卷发布页的js写的磕磕绊绊，但最终的想要的效果实现了，其实就是前后端分离
  
发布页重点提一下，初衷是为了充分利用数据库中已经存在的数据，选择问题后，会自动向后台查询和当前选择问题相关的选项，除了从后端查询数据， 发布页数据的构建完全和后端分离，构建完使用ajax提交给后端
*大胆的设想一下，人工智能时代，提问后，有人工智能程序生成可能的选项也完全有可能！

>在[这里](https://github.com/Hopetree/izone)借鉴到不少东西，帮忙推广一下！
  
