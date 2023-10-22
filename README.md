# copilot共享服务

[![GPLv2 License](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/gpl-2.0.html)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 服务介绍

该服务作为代理服务器，中转 copilot 插件的相关请求，支持多个用户共享同一个 copilot 账号，支持非代理情况下使用 copilot 。适用于拥有 copilot 权限的账号使用者，分享 copilot 权限给小伙伴。

~~> **貌似新版插件先校验登录状态后获取 copilot token ，若提示 "Sign in to use GitHub Copilot." 建议登录账号尝试（登录账号无需 copilot 权限）**~~

> 当前脚本以注入账号信息，当 copilot 插件提示登录时，主动点×关闭后 retry 即可
>
> 当前注入信息为: `{"id":"1","account":{"label":"Copilot","id":"1"},"scopes":["user:email"],"accessToken":"accessToken"}`

> 代理服务器需要能够访问 github.com 。

> 如果需要代理服务器代理整个 prompt 的响应，需要考虑服务器的带宽。

### copilot插件逻辑

1. 插件获取 github 账号的 token ，携带 token 请求 `api.github.com` 获取 copilot token 。

    > github token 仅重新下线登录 github 时才会失效。

2. 插件使用 copilot token 请求 copilot 服务，获取 copilot 的响应，即 copilot 的提示内容。
3. 当 copilot token 失效时，插件重新携带 token 请求 copilot token 。

### 代理服务器逻辑

1. 提供代理服务器后具有权限的 github token ，代理服务器可以使用该 token 请求 copilot token 。
2. 使用者修改插件，将对 `api.github.com` 获取 copilot 的请求代理到代理服务器，代理服务器使用 github token 请求 `api.github.com` ，提供 copilot token 。
3. 插件使用代理服务器提供的 copilot token 请求 copilot 服务，获取 copilot 的响应，即 copilot 的提示内容。

    > 同样可以通过修改插件，将对 copilot 服务的请求代理到代理服务器，代理服务器使用 copilot token 请求 copilot 服务，提供 copilot 的响应。

因此实现了一个 github token 可以被多个用户共享，且不需要代理即可使用 copilot 。

### 代理服务器细节

1. 代理服务器可以使用多个 github token ，组成 token 池，减轻单个 token 的压力。
2. 代理服务器可以将已获取的 copilot token 缓存，减少重复获取 copilot token 的请求。

## 使用说明

### 代理服务器

1. 复制 config.sample.py 为 config.py ，并根据实际情况修改其中的配置

    部分配置说明：

    1. `server_config["token"]` ：自定义鉴权，用于拦截非鉴权请求，若无需要可设置为 None 。
    2. `GITHUB_TOKEN` ：即具备 copilot 权限账号的 token ，获取方式详见 [GITHUB TOKEN 获取](#github-token-获取)
    3. `PROXY_COMPLETION_REQUEST`：是否允许代理 copilot prompt 的请求，默认为 False ，减轻代理服务器压力。
    3. `LOG_DEBUG` ：是否以 debug 模式记录日志。

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

### 本地插件修改

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

#### 参数说明

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

## 其他

1. 该仓库参考了 [share-copilot](https://gitee.com/chuangxxt/share-copilot) 和 zhile 大佬的 [cocopilot](https://zhile.io/2023/09/09/github-got-banned.html) , 感恩！

2. 该仓统一使用 [black](https://github.com/psf/black) 作为代码格式化标准，遵循 "less is more" ，使用 [black](https://github.com/psf/black) 原生标准，无任何自定义行为及参数需要。

    Reference:

    - [五彩斑斓的 Black —— Python 代码格式化工具 - muzing 的杂货铺](https://muzing.top/posts/a29e4743/#其他)