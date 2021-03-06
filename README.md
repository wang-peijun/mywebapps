# mywebapps  
一个个人实验练习测试学习使用的网站。使用的django框架。
站点 http://47.105.206.72

## 问卷调查
### 概述

完成了主要功能，具体就是：  
  1. 账户的注册登录功能
  2. 问卷列表页
  3. 问卷发布页
  4. 问卷详情页，即参与调查页
  5. 结果展示页
  6. 我发布的问卷页
  7. 问卷搜索功能

待完成的工作：
  1. 第三方登录，allauth可以实现
  2. 问卷功能完善
     * 结果展示，现在只是统计了一下数量
  3. ......

### 一些关键点
#### 模型
项目虽然简单，模型关系还是比较复杂的。
主要的表：

  * 问卷表poll
  * 问题表question，问题三种类型：单选，多选，回答
  * 选项表choice，has_extra_data字段表示选项是否有额为数据，True表示类似"其他，请输入..."这样的选项
  * poll_question表，poll和question多对多关系表，添加index字段表示question在poll中的位置（顺序）
  * 投票表vote，poll_question和choice多对多关系表，添加index字段表示choice在poll_question中的位置（顺序）
  * 回答表answer，有一个poll_question外键，是多对一关系
  * 选项的额外数据表extra_data，和vote是多对一关系
  * 用户表user，和vote是多对多关系，和answer是一对多关系，因为投票可以匿名可以实名，user字段可以为空
    user和poll是多对一关系，登录用户才可以发布问卷，user字段不能为空

#### 模板
使用了两套模板引擎， 因为据说jinja2性能更优，所以尝试一下。两套引擎，可以在同一个项目中使用，搜索顺序就是模板引擎定义的顺序，先搜索到哪个用哪个。

#### 中间件
1. 参考[这里](https://blog.csdn.net/qq_39687901/article/details/81387584)，实现了一个全局获得request对象的中间件
2. 使用中间件在allauth中加入登录和注册时输入验证码验证功能

#### 缓存
使用的是django-redis, 在两个地方使用了缓存:
  1. 问卷列表页的数据缓存，用django的signals模块，当有有新的问卷post提交并save到数据库时，删除缓存
  2. 问卷详情页的模板片段缓存，因为jinja2默认没有缓存标签，参考[这里](https://www.kancloud.cn/manual/jinja2/70475)，添加缓存标签，其中使用到了werkzeug库

#### signal
使用signal，数据更新时删除缓存。

#### 搜索功能使用
使用haystack，whoosh，jieba分词，实现全文搜索功能。

#### 前端
前端写的比较简陋。
  1. bootstrap 支持响应式
  2. crispy 用于表单渲染
  3. font-awesome 提供一些图标
  4. jQuery。主要是问卷发布页，还是比较复杂的

---

用到的主要库：

后端：[django][]，[allauth][]，[crispy][]，[jinja2][]，[django-redis][]，[werkzeug][]，[uWSGI][]，[nginx][], [haystack][], [jieba][], [django-extensions][]

前端：[jquery][]，[bootstrap][]，[font-awesome][]

[werkzeug]: http://werkzeug.pocoo.org/
[allauth]: https://github.com/pennersr/django-allauth
[crispy]: https://django-crispy-forms.readthedocs.io/en/latest/index.html
[jinja2]: http://jinja.pocoo.org/
[uWSGI]: https://github.com/unbit/uwsgi-docs/blob/master/index.rst
[nginx]: http://nginx.org/
[jquery]: https://jquery.com/
[bootstrap]: http://www.bootcss.com/
[font-awesome]: https://fontawesome.io/
[django]: https://www.djangoproject.com/
[django-redis]: https://github.com/bluedazzle/django-redis-doc-chs/blob/master/source/index.rst
[haystack]: http://haystacksearch.org/
[jieba]: https://github.com/fxsjy/jieba
[django-extensions]: https://django-extensions-zh.readthedocs.io/zh_CN/latest/

>在[这里](https://github.com/Hopetree/izone)也学习到不少东西，帮忙推广一下！
>
>调查问卷内容爬取自[问卷星](https://www.wjx.cn/newwjx/mysojump/newselecttemplete.aspx)
  
