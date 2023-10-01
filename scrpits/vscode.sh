#!/bin/bash

set -e

echo_r() {
    echo "\033[31m$1\033[0m"
}

usage() {
    echo    "Usage: sh $0 [--copilot] [--chat] [--help] <custom_token> <custom_api_url>"
    echo_r  "  用于设置从代理获取 copilot 相关功能信息"
    echo    "  --chat: 同时开启 copilot chat 功能"
    echo    "  --copilot: 代理 token 获取外，同时同步代理提示"
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
if [ ! -d "$EXTENSIONS_DIR" ]; then
    echo "ERROR: VSCode extensions directory not found!"
    exit 1
fi

COPILOT_DIR=$(ls -lt "$EXTENSIONS_DIR" | grep '^d' | awk '{print $9}' | grep -E '^github\.copilot-[0-9]+\.[0-9]+\.[0-9]+$' | head -n 1)
if [ -z "$COPILOT_DIR" ]; then
    echo "ERROR: Copilot extension not found!"
    exit 1
fi

if [ "$CHAT" = true ]; then
    COPILOT_CHAT_DIR=$(ls -lt "$EXTENSIONS_DIR" | grep '^d' | awk '{print $9}' | grep -E '^github\.copilot-chat-[0-9]+\.[0-9]+\.[0-9]+$' | head -n 1)
    if [ -z "$COPILOT_CHAT_DIR" ]; then
        echo "ERROR: Copilot chat extension not found!"
        exit 1
    fi
fi

COPILOT_DIR="$EXTENSIONS_DIR/$COPILOT_DIR"
EXTENSION_FILE="$COPILOT_DIR/dist/extension.js"
if [ ! -f "$EXTENSION_FILE" ]; then
    echo "ERROR: Copilot extension entry file not found!"
    exit 1
fi

if [ "$CHAT" = true ]; then
    COPILOT_CHAT_DIR="$EXTENSIONS_DIR/$COPILOT_CHAT_DIR"
    EXTENSION_CHAT_FILE="$COPILOT_CHAT_DIR/dist/extension.js"
    if [ ! -f "$EXTENSION_CHAT_FILE" ]; then
        echo "ERROR: Copilot chat extension entry file not found!"
        exit 1
    fi
fi


TMP_FILE="$COPILOT_DIR/dist/extension.js.tmp"
echo "process.env.CODESPACES=\"true\";process.env.GITHUB_TOKEN=\"$GITHUB_TOKEN\";process.env.GITHUB_SERVER_URL=\"https://github.com\";process.env.GITHUB_API_URL=\"$GITHUB_API_URL\";" > "$TMP_FILE"
cat "$EXTENSION_FILE" >> "$TMP_FILE"
mv "$TMP_FILE" "$EXTENSION_FILE"


if [ "$CHAT" = true ]; then
    delimiter='|'
    sed -ri "s${delimiter}getTokenUrl\(e\)\{return e.devOverride\?.copilotTokenUrl\?\?this.tokenUrl\}${delimiter}getTokenUrl\(e\)\{return \"${GITHUB_API_URL}/copilot_internal/v2/token\"\}${delimiter}g" "$EXTENSION_CHAT_FILE"
    echo "Chat enabled"
fi

if [ "$COPILOT" = true ]; then
    delimiter='|'
    sed -ri "s${delimiter}https://copilot-proxy.githubusercontent.com${delimiter}${GITHUB_API_URL}${delimiter}g" "$EXTENSION_FILE"
    if [ "$CHAT" = true ]; then
        sed -ri "s${delimiter}https://copilot-proxy.githubusercontent.com${delimiter}${GITHUB_API_URL}${delimiter}g" "$EXTENSION_CHAT_FILE"
    fi
    echo "copilot proxy enabled"
fi

echo "done. please restart your vscode."