#!/bin/bash

echo_r() {
    printf "\033[31m%s\033[0m\n" "$1"
}

usage() {
    echo    "Usage: sh $0 [--copilot] [--chat] [--remote] [--help] <custom_token> <custom_api_url>"
    echo_r  "  用于设置客户端从代理服务器而不是Github获取copilot token及提示"
    echo    "  <custom_token>: 自定义代理鉴权"
    echo    "  <custom_api_url>: 自定义代理地址"
    echo    "  --chat: 同时开启 copilot chat 功能"
    echo    "  --copilot: 代理 token 获取外，同时同步代理提示"
    echo    "  --remote: 适用于 wsl 或远程连接的 ubuntu 等环境"
    echo    "  --help: 帮助信息"
    exit 1
}

while getopts ":h-:" opt; do
    case "${opt}" in
        -)
            case "${OPTARG}" in
                copilot)
                    COPILOT=true
                ;;
                chat)
                    CHAT=true
                ;;
                remote)
                    REMOTE=true
                ;;
                help)
                    usage
                ;;
                *)
                    echo "Invalid option: --${OPTARG}"
                    usage
                ;;
            esac
        ;;
        h)
            usage
        ;;
        *)
            echo "Invalid option: -$OPTARG"
            usage
        ;;
    esac
done
shift $((OPTIND-1))

if [ $# -ne 2 ]; then
    usage
fi

GITHUB_TOKEN=$1
GITHUB_API_URL=$2

EXTENSIONS_DIR="$HOME/.vscode/extensions"
if [ "$REMOTE" = true ]; then
    EXTENSIONS_DIR="$HOME/.vscode-server/extensions"
fi

if [ ! -d "$EXTENSIONS_DIR" ]; then
    echo_r "ERROR: VSCode extensions directory not found!"
    echo_r "Ps: if you are using wsl, please use --remote option"
    exit 1
fi

COPILOT_DIR=$(ls -lt "$EXTENSIONS_DIR" | grep '^d' | awk '{print $9}' | grep -E '^github\.copilot-[0-9]+\.[0-9]+\.[0-9]+$' | head -n 1)
if [ -z "$COPILOT_DIR" ]; then
    echo_r "ERROR: Copilot extension not found!"
    exit 1
fi

if [ "$CHAT" = true ]; then
    COPILOT_CHAT_DIR=$(ls -lt "$EXTENSIONS_DIR" | grep '^d' | awk '{print $9}' | grep -E '^github\.copilot-chat-[0-9]+\.[0-9]+\.[0-9]+$' | head -n 1)
    if [ -z "$COPILOT_CHAT_DIR" ]; then
        echo_r "ERROR: Copilot chat extension not found!"
        exit 1
    fi
fi

COPILOT_DIR="$EXTENSIONS_DIR/$COPILOT_DIR"
EXTENSION_FILE="$COPILOT_DIR/dist/extension.js"
if [ ! -f "$EXTENSION_FILE" ]; then
    echo_r "ERROR: Copilot extension entry file not found!"
    exit 1
fi

if [ "$CHAT" = true ]; then
    COPILOT_CHAT_DIR="$EXTENSIONS_DIR/$COPILOT_CHAT_DIR"
    EXTENSION_CHAT_FILE="$COPILOT_CHAT_DIR/dist/extension.js"
    if [ ! -f "$EXTENSION_CHAT_FILE" ]; then
        echo_r "ERROR: Copilot chat extension entry file not found!"
        exit 1
    fi
fi

delimiter='|'
sed -ri "s${delimiter}(getTokenUrl\([^)]+\))\{return [^}]+\}${delimiter}\1\{return \"${GITHUB_API_URL}/copilot_internal/v2/token\"\}${delimiter}g" "$EXTENSION_FILE"
sed -ri 's'"${delimiter}"'(getTokenUrl\([^)]+\);try\{[^`]+)Authorization:`[^`]+`'"${delimiter}"'\1Authorization:`token '"${GITHUB_TOKEN}"'`'"${delimiter}"'g' "$EXTENSION_FILE"
# 移除遥测接口
sed -ri "s${delimiter}https://copilot-telemetry.githubusercontent.com/telemetry${delimiter}${delimiter}g" "$EXTENSION_FILE"

if [ "$CHAT" = true ]; then
    delimiter='|'
    sed -ri "s${delimiter}(getTokenUrl\([^)]+\))\{return [^}]+\}${delimiter}\1\{return \"${GITHUB_API_URL}/copilot_internal/v2/token\"\}${delimiter}g" "$EXTENSION_CHAT_FILE"
    sed -ri 's'"${delimiter}"'(getTokenUrl\([^)]+\);try\{[^`]+)Authorization:`[^`]+`'"${delimiter}"'\1Authorization:`token '"${GITHUB_TOKEN}"'`'"${delimiter}"'g' "$EXTENSION_CHAT_FILE"
    # 移除遥测接口
    sed -ri "s${delimiter}https://copilot-telemetry.githubusercontent.com/telemetry${delimiter}${delimiter}g" "$EXTENSION_CHAT_FILE"
    echo "Chat enabled"
fi

if [ "$COPILOT" = true ]; then
    delimiter='|'
    sed -ri "s${delimiter}https://copilot-proxy.githubusercontent.com${delimiter}${GITHUB_API_URL}${delimiter}g" "$EXTENSION_FILE"
    if [ "$CHAT" = true ]; then
        sed -ri "s${delimiter}https://api.githubcopilot.com${delimiter}${GITHUB_API_URL}${delimiter}g" "$EXTENSION_CHAT_FILE"
    fi
    echo "copilot proxy enabled"
fi

echo "done. please restart your vscode."