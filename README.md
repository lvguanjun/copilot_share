# copilot共享服务

[![GPLv2 License](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/gpl-2.0.html)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 服务介绍

该服务作为代理服务器，中转 copilot 插件的相关请求，支持多个用户共享同一个 copilot 账号，支持非代理情况下使用 copilot 。适用于拥有 copilot 权限的账号使用者，分享 copilot 权限给小伙伴。

> **如果只是想使用 copilot ，可直接使用 zhile 大佬的 [CoCopilot插件](https://zhile.io/2023/09/09/github-got-banned.html#more-468)，也可以 vscode 插件商店搜索 `CoCopilot` 安装。感恩大佬，给大佬插件五星好评呀:star::star::star::star::star: 。**

~~> **貌似新版插件先校验登录状态后获取 copilot token ，若提示 "Sign in to use GitHub Copilot." 建议登录账号尝试（登录账号无需 copilot 权限）**~~

> ~~当前脚本已注入账号信息，当 copilot 插件提示登录时，主动点×关闭后 retry 即可。~~
>
> ~~当前注入信息为: `{"id":"1","account":{"label":"Copilot","id":"1"},"scopes":["user:email"],"accessToken":"accessToken"}`~~

> 貌似 `v1.129.0` 版本插件注入账号信息方式优先级不够高，仍然提示登录，建议直接登录账号（无需 copilot 权限），且不再维护脚本方式无需登录需求。如果实在是希望通过脚本实现无需登录，可以参考 [issues 3](https://github.com/lvguanjun/copilot_share/issues/3#issuecomment-1773886757) 小伙伴提出的方案
>
> **不过好消息是，参考 zhile 大佬的 [CoCopilot插件](https://zhile.io/2023/09/09/github-got-banned.html#more-468)，也实现了一个简单的基于 BasicAuth 的企业认证方案，可以通过自定义 [OAuth 2.0认证授权](https://www.ruanyifeng.com/blog/2019/04/oauth_design.html) 实现非登录使用 copilot 需求**


> 代理服务器需要能够访问 github.com 。

> 如果需要代理服务器代理整个 prompt 的响应，需要考虑服务器的带宽。

### copilot插件逻辑

1. 插件获取 github 账号的 token ，携带 token 请求 `api.github.com` 获取 copilot token 。

    > github token 仅重新下线登录 github 时才会失效。

2. 插件使用 copilot token 请求 copilot 服务，获取 copilot 的响应，即 copilot 的提示内容。
3. 当 copilot token 失效时，插件重新携带 token 请求 copilot token 。

### 代理服务器逻辑

1. 代理服务器配置具有权限的 github token ，使用该 token 请求 copilot token 。
2. vscode 插件配置代理服务器地址，从代理服务器获取 copilot token 。
    1. 脚本方案：使用脚本修改插件，将对 `api.github.com` 获取 copilot 的请求覆盖指向为代理服务器，代理服务器使用 github token 请求 `api.github.com` ，提供 copilot token 。
    2. 企业认证方案：通过配置文件配置使用企业认证，将整个 token 获取的请求流程代理到代理服务器。
3. 插件使用代理服务器提供的 copilot token 请求 copilot 服务，获取 copilot 的响应，即 copilot 的提示内容。

    > 1. 同样可以通过脚本修改插件，将对 copilot 服务的请求代理到代理服务器，代理服务器使用 copilot token 请求 copilot 服务，提供 copilot 的响应。
    >
    > 2. 使用配置文件同样可以实现 copilot “提示请求”的代理。详见 [vscode 插件配置](#方案一vscode-插件配置需要服务端开启企业认证支持) 。


因此实现了一个 github token 可以被多个用户共享，且不需要代理即可使用 copilot 。

### 代理服务器细节

1. 代理服务器可以使用多个 github token ，组成 token 池，减轻单个 token 的压力。
2. 代理服务器可以将已获取的 copilot token 缓存，减少重复获取 copilot token 的请求。

## 企业认证方案

通过对 `github.copilot.advanced.authProvider` 的配置，将原来的 github.com 认证流程替换为自定义的 enterprise 认证流程，从而实现非登录使用 copilot 的需求。

如果代理服务器配置 `USE_ENTERPRISE_AUTH` 为 True ，则代理服务器会注册一个 enterprise_auth 蓝图，用于处理认证流程。否则不会注册该蓝图，此时代理服务器仅仅代理 copilot 相关的请求。

## 使用说明

### 代理服务器

1. 复制 config.py.sample 为 config.py ，并根据实际情况修改其中的配置

    部分配置说明：

    1. `server_config["token"]` ：自定义鉴权，用于拦截非鉴权请求，若无需要可设置为 None 。
    2. `GITHUB_TOKEN` ：即具备 copilot 权限账号的 token ，获取方式详见 [GITHUB TOKEN 获取](#github-token-获取)
    3. `PROXY_COMPLETION_REQUEST`：是否允许代理 copilot prompt 的请求，默认为 False ，减轻代理服务器压力。
    4. `USE_ENTERPRISE_AUTH`：是否使用企业认证，若否，则不会注册企业认证的蓝图，详见 [企业认证方案](#企业认证方案)。
    5. `LOG_DEBUG` ：是否以 debug 模式记录日志。

2. 配置虚拟环境

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3. 代理服务器运行

    - 直接运行代理服务器

        ```bash
        # 前台运行
        python app.py
        # 后台运行
        nohup python app.py > nohup.out 2>&1 &
        # 关闭后台运行
        ps -ef | grep app.py
        kill -9 pid
        ```

    - 使用 Gunicorn 进行部署

        - **基础部署**

            ```bash
            # 直接在前台运行
            gunicorn --bind 127.0.0.1:8080 app:app
            ```

            ```bash
            # 在后台运行
            nohup gunicorn --bind 127.0.0.1:8080 app:app > nohup.out 2>&1 &
            ```

        - **高级配置**

            ```bash
            # 指定工作进程数
            gunicorn --bind 127.0.0.1:8080 -w 4 app:app
            ```

        - **使用配置文件**

            ```bash
            # 使用配置文件启动 gunicorn
            nohup gunicorn -c gunicorn_config.py app:app > nohup.out 2>&1 &
            ```

            `gunicorn_config.py`的示例内容：

            ```python
            bind = "127.0.0.1:8080"  # 绑定IP和端口号
            workers = 1  # 工作进程数
            accesslog = "server_access.log"  # 访问日志文件
            errorlog = "server_error.log"  # 错误日志文件
            ```

        > Gunicorn 默认在 8000 端口运行是该工具的预设值。 Gunicorn 不会自动采用 Flask 应用或其他 WSGI 应用设置的其他端口。需要显式地在 Gunicorn 的命令行选项或配置文件中指定端口。
    
    - nginx 反向代理

        当前暂无云服务器，故 nginx 需自行查阅参考配置。

> 说明：uwsgi 部署存在问题，查看服务器响应正常，但插件无法正常使用，且 postman 报错如下，暂无法解决，故删除 uwsgi 部署相关说明。
```
name: "Error"
code: "HPE_INVALID_CHUNK_SIZE"
message: "Parse Error: Invalid character in chunk size"
```

### 本地客户端使用说明

#### 方案一、vscode 插件配置（需要服务端开启企业认证支持）

1. 打开 `settings.josn` 文件
    1. 点击左侧边栏的齿轮图标，选择 Settings。
    2. 在设置标签页的右上角，你会看到一个打开文件的图标，鼠标悬停上去会显示 Open Settings (JSON)。
    3. 点击这个图标，VSCode 就会打开 settings.json 文件。
2. 根据实际的域名或 ip 配置，将以下配置到 `settings.josn` 文件中

    ```python
    "github.copilot.advanced": {
        "authProvider": "github-enterprise",
        # 需要代理 copilot prompt 的请求时设置
        "debug.overrideProxyUrl": "http://127.0.0.1:8080",
        # 需要代理 copilot chat prompt 的请求时设置
        "debug.chatOverrideProxyUrl": "http://127.0.0.1:8080/chat",
    },
    "github-enterprise.uri": "http://user:password@127.0.0.1:8080",
    ```

    1. `debug.overrideProxyUrl` ：代理服务器地址，仅代理“提示请求”时添加。
    2. `debug.chatOverrideProxyUrl` ：代理服务器地址，仅代理 chat “请求”时添加。
    3. `github-enterprise.uri` ：代理服务器地址，其中 `user:password` 为代理服务器的 BasicAuth 鉴权，代理服务器配置了鉴权时添加正确账密，未配置鉴权则需填任意字符串**占位**，例如 `user:password` 。具体原因详见[子域名规避说明](#其他说明)

3. 重载 vscode 窗口
4. 当 copilot 插件提示登录时，点击登录走正常登录流程即可

    当前登录仅仅走了流程，确保插件js正常加载，不会真正登录，因此不需要担心账号泄露。

> ~~说明：该方式配置刚需域名，如果没有域名，可以通过更改本地hosts文件实现。需要同时添加 `example.com` 和 `api.example.com` 的映射。~~


> 重要：**~~如果使用 nginx 反向代理，需要同时配置 `example.com` 和 `api.example.com` 的映射。插件内部会向 `github-enterprise.uri` 的子域名 `api.example.com` 发送请求，如果没有配置 `api.example.com` 的映射，会导致请求失败。~~**

~~nginx配置示例：~~

```
server {
    listen 80;
    server_name example.com api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
    }
}
```

##### 其他说明

1. 当配置正常的 `github-enterprise.uri=http://example.com` 情况下，插件除认证授权逻辑外，其他请求均会发送到 `example.com` 的子域名 `api.example.com` ，因此需要将 `github-enterprise.uri` 配置为域名且需要添加 `api.example.com` 的映射。否则要么错误的 url (such as: api.127.0.0.1)，要么 502 指向不到源站。但配置了 BasicAuth 后，插件不会再向其子域名 `api.example.com` 发送请求，而是直接向域名发请求，因此配置 `github-enterprise.uri` 时，需要带上 BasicAuth 。当然，如果同时配置 `example.com` 和 `api.example.com` 的映射，也可以不配置 BasicAuth ，此时需要关心 dns 和 nginx 的配置，否则会导致请求失败。

   让我们看看为什么配置了 BasicAuth 后，插件不会再向其子域名 `api.example.com` 发送请求，而是直接向域名发请求。/笑

   插件是这样设置的子域名，`api.${domain}` ，因此 `exapmle.com` -> `api.example.com` ，`127.0.0.1` -> `api.127.0.0.1`，那加了 BasicAuth 的域名则 `user:pass@127.0.0.1` -> `api.user:pass@127.0.0.1` ，也就是说， `api.user` 作为了用户名，因此域名指向无变化。

   > **该功能基于 bug 实现**

#### 方案二、脚本插件修改

当前仅提供适用于 Windows, Linux 的vscode插件修改脚本，其他平台的修改请自行修改。

示例：
    
```bash
# 仅代理 token 获取
sh scrpits/vscode.sh 123456 http://127.0.0.1:8080

# 仅代理 token 获取，且支持 copilot chat
sh scrpits/vscode.sh --chat 123456 http://127.0.0.1:8080

# 同时代理 copilot prompt
sh scrpits/vscode.sh --copilot 123456 http://127.0.0.1:8080

# copilot 及 chat 同时代理 copilot prompt
sh scrpits/vscode.sh --chat --copilot 123456 http://127.0.0.1:8080

# 使用 cocopilot 代理 token 获取，且支持 copilot chat
sh scrpits/vscode.sh --chat ghu_ThisIsARealFreeCopilotKeyByCoCopilot https://api.cocopilot.org
```

> `http://127.0.0.1:8080` 即代理服务器地址。

> **Windows 使用 git bash 等类似 bash 的终端运行脚本。**

> **如果是使用 vscode 远程连接 Ubuntu 服务器且副驾驶拓展安装在了远程服务器上，需要添加 `--remote` 选项**

> 脚本原理说明：参考 [share-copilot](https://gitee.com/chuangxxt/share-copilot/blob/master/readme/codeTipsProxy.md)

##### 参数说明

- `custom_token`: 必填，代理服务器自定义鉴权，若服务器无需鉴权，随意提供字符串占位即可
- `custom_api_url`: 必填，代理服务器地址，例如 `http://127.0.0.1:8080`

> 若其他非必填项未填，则插件配置仅仅代理 token 的获取，其他请求不代理。

### GITHUB TOKEN 获取

1. JetBrains 系列 IDE 登录插件后 %userprofile%\AppData\Local\github-copilot\hosts.json 中会记录 token ，以 ghu_ 开头的字符串。

2. vscode 可以登录插件后**抓包获取 token** ，以 gho_ 开头的字符串。

> vscode 玩家如果觉得抓包挺麻烦，可以下载 JetBrains 系列 IDE ，在 JetBrains 系列 IDE 中登录插件后，获取到 token 也可以直接在 vscode 中使用。

## 成功示例

- copilot 代理提示

    ![copilot](readme/copilot.png)

- copilot chat 代理提示

    ![copilot-chat](readme/chat.png)

- server 端展示

    ![server](readme/server.png)

## 功能增强

1. 新增 copilot-chat 代理到 chatgpt ，可以使用 chatgpt-4 模型回答问题。

> 说明：当前 copilot-chat 响应为 `application/json` ，而 chatgpt-4 响应为 `text/event-stream; charset=utf-8` ，当前实测两种响应类型在 vscode 均可以正常对话，但不保证后续版本 vscode 仍然可以正常对话。

> 鸣谢 zhile 大佬的 [pandora](https://github.com/zhile-io/pandora)

## Todo

1. 反代的函数处理采用异步，但是没有使用异步的库，后续考虑使用异步的库进行处理。
2. postman 307 重定向时会丢失 Authorization ，当设置 `PROXY_COMPLETION_REQUEST = False` 时，会无法使用 postman 调试相关“提示请求”。

    客户端问题，vsocde能正常使用，因此当前仅考虑从 postman 查找是否存在选项解决。

3. 通过携带 BasicAuth 的方法规避了部分请求指向 `api.xxx.xxx` 子域名的问题，但目前原因不明，不确保后续版本是否会出现问题。需要查看插件源码，确定插件的请求逻辑。

    基于子域名拼接 bug 规避了刚需域名及子域名映射的问题。详见 [子域名规避说明](#其他说明)

## 其他

1. 该仓库参考了 [share-copilot](https://gitee.com/chuangxxt/share-copilot) 和 zhile 大佬的 [cocopilot](https://zhile.io/2023/09/09/github-got-banned.html) , 感恩！

2. 该仓统一使用 [black](https://github.com/psf/black) 作为代码格式化标准，遵循 "less is more" ，使用 [black](https://github.com/psf/black) 原生标准，无任何自定义行为及参数需要。

    Reference:

    - [五彩斑斓的 Black —— Python 代码格式化工具 - muzing 的杂货铺](https://muzing.top/posts/a29e4743/#其他)