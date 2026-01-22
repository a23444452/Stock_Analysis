#!/bin/bash

# 台股分析儀表板 - 啟動/關閉腳本
# 用法: ./run.sh [start|stop|restart|status]

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$PROJECT_DIR/.pids"
STREAMLIT_PID="$PID_DIR/streamlit.pid"
API_PID="$PID_DIR/api.pid"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 確保 PID 目錄存在
mkdir -p "$PID_DIR"

# 檢查程序是否運行中
is_running() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# 終止佔用指定 port 的程序
kill_port() {
    local port=$1
    local pids=$(lsof -ti :$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}偵測到 port $port 被佔用，正在終止舊程序...${NC}"
        for pid in $pids; do
            echo -e "  終止 PID: $pid"
            kill "$pid" 2>/dev/null
        done
        sleep 1
        # 檢查是否還有殘留，強制終止
        pids=$(lsof -ti :$port 2>/dev/null)
        if [ -n "$pids" ]; then
            for pid in $pids; do
                kill -9 "$pid" 2>/dev/null
            done
            sleep 1
        fi
        echo -e "${GREEN}✓ 舊程序已終止${NC}"
    fi
}

# 啟動 Streamlit
start_streamlit() {
    if is_running "$STREAMLIT_PID"; then
        echo -e "${YELLOW}Streamlit 已在運行中 (PID: $(cat $STREAMLIT_PID))${NC}"
        return
    fi
    # 檢查並清理佔用 port 的舊程序
    kill_port 8501
    echo -e "${GREEN}啟動 Streamlit...${NC}"
    cd "$PROJECT_DIR"
    nohup streamlit run app.py --server.port 8501 > "$PID_DIR/streamlit.log" 2>&1 &
    echo $! > "$STREAMLIT_PID"
    sleep 2
    if is_running "$STREAMLIT_PID"; then
        echo -e "${GREEN}✓ Streamlit 啟動成功 (PID: $(cat $STREAMLIT_PID))${NC}"
        echo -e "  網址: http://localhost:8501"
    else
        echo -e "${RED}✗ Streamlit 啟動失敗，請檢查 $PID_DIR/streamlit.log${NC}"
    fi
}

# 啟動 API
start_api() {
    if is_running "$API_PID"; then
        echo -e "${YELLOW}API Server 已在運行中 (PID: $(cat $API_PID))${NC}"
        return
    fi
    # 檢查並清理佔用 port 的舊程序
    kill_port 8001
    echo -e "${GREEN}啟動 API Server...${NC}"
    cd "$PROJECT_DIR"
    nohup uvicorn api:app --host 0.0.0.0 --port 8001 > "$PID_DIR/api.log" 2>&1 &
    echo $! > "$API_PID"
    sleep 2
    if is_running "$API_PID"; then
        echo -e "${GREEN}✓ API Server 啟動成功 (PID: $(cat $API_PID))${NC}"
        echo -e "  網址: http://localhost:8001"
        echo -e "  文件: http://localhost:8001/docs"
    else
        echo -e "${RED}✗ API Server 啟動失敗，請檢查 $PID_DIR/api.log${NC}"
    fi
}

# 停止服務
stop_service() {
    local name=$1
    local pid_file=$2

    if is_running "$pid_file"; then
        local pid=$(cat "$pid_file")
        echo -e "${YELLOW}停止 $name (PID: $pid)...${NC}"
        kill "$pid" 2>/dev/null
        sleep 1
        # 如果還在運行，強制終止
        if ps -p "$pid" > /dev/null 2>&1; then
            kill -9 "$pid" 2>/dev/null
        fi
        rm -f "$pid_file"
        echo -e "${GREEN}✓ $name 已停止${NC}"
    else
        echo -e "${YELLOW}$name 未在運行${NC}"
        rm -f "$pid_file"
    fi
}

# 顯示狀態
show_status() {
    echo -e "\n${GREEN}=== 服務狀態 ===${NC}\n"

    if is_running "$STREAMLIT_PID"; then
        echo -e "Streamlit:  ${GREEN}運行中${NC} (PID: $(cat $STREAMLIT_PID)) - http://localhost:8501"
    else
        echo -e "Streamlit:  ${RED}未運行${NC}"
    fi

    if is_running "$API_PID"; then
        echo -e "API Server: ${GREEN}運行中${NC} (PID: $(cat $API_PID)) - http://localhost:8001"
    else
        echo -e "API Server: ${RED}未運行${NC}"
    fi
    echo ""
}

# 顯示日誌
show_logs() {
    local service=$1
    case $service in
        streamlit)
            if [ -f "$PID_DIR/streamlit.log" ]; then
                echo -e "${GREEN}=== Streamlit 日誌 ===${NC}"
                tail -50 "$PID_DIR/streamlit.log"
            else
                echo -e "${YELLOW}找不到 Streamlit 日誌${NC}"
            fi
            ;;
        api)
            if [ -f "$PID_DIR/api.log" ]; then
                echo -e "${GREEN}=== API Server 日誌 ===${NC}"
                tail -50 "$PID_DIR/api.log"
            else
                echo -e "${YELLOW}找不到 API Server 日誌${NC}"
            fi
            ;;
        *)
            echo -e "${GREEN}=== Streamlit 日誌 ===${NC}"
            [ -f "$PID_DIR/streamlit.log" ] && tail -20 "$PID_DIR/streamlit.log"
            echo -e "\n${GREEN}=== API Server 日誌 ===${NC}"
            [ -f "$PID_DIR/api.log" ] && tail -20 "$PID_DIR/api.log"
            ;;
    esac
}

# 顯示使用說明
show_help() {
    echo -e "${GREEN}台股分析儀表板 - 啟動腳本${NC}"
    echo ""
    echo "用法: ./run.sh [指令]"
    echo ""
    echo "指令:"
    echo "  start       啟動所有服務 (Streamlit + API)"
    echo "  stop        停止所有服務"
    echo "  restart     重啟所有服務"
    echo "  status      顯示服務狀態"
    echo "  logs        顯示所有日誌"
    echo "  logs:web    顯示 Streamlit 日誌"
    echo "  logs:api    顯示 API Server 日誌"
    echo "  web         只啟動 Streamlit"
    echo "  api         只啟動 API Server"
    echo "  help        顯示此說明"
    echo ""
}

# 主程式
case "$1" in
    start)
        echo -e "\n${GREEN}=== 啟動所有服務 ===${NC}\n"
        start_streamlit
        start_api
        show_status
        ;;
    stop)
        echo -e "\n${GREEN}=== 停止所有服務 ===${NC}\n"
        stop_service "Streamlit" "$STREAMLIT_PID"
        stop_service "API Server" "$API_PID"
        ;;
    restart)
        echo -e "\n${GREEN}=== 重啟所有服務 ===${NC}\n"
        stop_service "Streamlit" "$STREAMLIT_PID"
        stop_service "API Server" "$API_PID"
        sleep 1
        start_streamlit
        start_api
        show_status
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs all
        ;;
    logs:web|logs:streamlit)
        show_logs streamlit
        ;;
    logs:api)
        show_logs api
        ;;
    web|streamlit)
        start_streamlit
        ;;
    api)
        start_api
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        ;;
esac
