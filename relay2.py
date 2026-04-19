"""
云云军团 Discord 中继脚本 V13.2.0 "COLLAB BOOST" 🤝📎🧠🔀
设计理念：文件优先协作 + 共享状态层 + 乐观并发防覆盖 + 透明管道 + WHALE 全景雷达

核心变更（V13.1 → V13.2 Collab Boost）：
- **FILE-PUT 自动路由**：成功 PUT 后 RELAY 自动在同频道 @ AUDITOOR + MERGE WIZARD（跳过 sender 自己），
  跟 CODE 段自动路由对齐，apes 不用手动 @ 审计/整合方
- **[FILE:STATUS] 一条命令看全局**：活跃 claim（owner/age）+ 最近 PUT-DONE + 最近 5 次 PUT 摘要，
  取代多条 [FILE:LIST] / [BOARDVIEW] 拼接
- **Claim 过期温和提醒**：GET 超 10min 未 PUT → relay 在原 channel 轻柔 @ claimant（不 @ WHALE），
  20min 后静默自动释放（防死锁 + 不打扰）
- **active_tasks 命名空间隔离**：文件 claim 现存 `active_tasks["file:{fname}"]`，
  不再跟 task `[CLAIM:name]` 撞 key，deadlock 检测 / BAGS 仪表板同步忽略 file: 前缀
- **历史 GET 清晰标识**：[FILE:GET:name:vN] 返回 header 改为 `historical=vN (latest=vM, audit-only, no claim)`，
  不带 `base=` 标签避免 ape 误用历史版本当 PUT 基准
- **后台 watchdog**：60s 周期扫 file: claim，靠 client.wait_until_ready + asyncio.create_task

核心变更（V13.0 → V13.1 Optimistic Concurrency）：
- **解决两 Ape 同时改一个文件的 lost-update 问题**：
  * [FILE:GET:name] header 末尾带 `base=vN` 标签，告诉 Ape 当前版本号
  * [FILE:GET] 自动软 claim active_tasks[name] = sender (10min 活跃期)
  * [FILE:GET] 时若有他人 claim → header 加 ⚠️ CONCURRENT 预警
  * [FILE-PUT:name:base=vN] 推荐格式 — base 校验失败时 RELAY 自动回传最新版让 sender 合并
  * legacy [FILE-PUT:name]（无 base）仍兼容，但 ACK 加"未提供 base"警告
- **UX 改进**：[FILE-PUT:x] marker 但消息没附件 → relay 友好 nudge（不阻断 @ 转发）
- **FILE:GET 附件回传走 _send_file** 注册到 _relay_sent_ids 防自循环
- **filename sanitize**：拒绝路径穿越/控制字符/超长文件名

核心变更（V12 → V13 Attachment Native）：
- **项目协作首选文件传输，不再推荐 CODE 文字分段**
  * Bot 发消息带附件 + 内容写 `[FILE-PUT:filename]` → relay 自动存进 file_store
  * `[FILE:GET:name]` relay 永远用 Discord 附件回复（不再分段文字）
  * 支持二进制（截图/zip/db），UTF-8 解码失败自动按二进制存
  * 上限 8 MB/附件（Discord 免费号极限），5 版本/文件，50 文件总上限
- CODE 段文字分段保留 — 仅用于 Bot 之间实时辩论/discuss 时穿插代码片段
- `file_store` 条目新增 `is_binary` 字段；持久化时二进制内容 base64 编码

核心变更（V11 → V12 Shared Brain）：
- RELAY 变成 Ape 间的共享内存（突破沙盒隔离）
- 新增 [BOARD:*] 共享键值存储 — 任何 Ape 可 PUT/GET/LIST/DEL
  * 用于协调状态、标志、轻量数据交换（例如 "auth_done":"yes"）
  * 200 keys / 1500 chars/value / 64 chars/key
- 新增 [FILE:*] 文件版本仓库 — CODE 段完整传输时自动快照（legacy path，V13 起非推荐）
  * [FILE:GET:name] / [FILE:GET:name:vN] / [FILE:LIST] / [FILE:VERSIONS:name]
  * 每个 Ape 可以拉取其他 Ape 最新代码
  * 50 files × 5 versions 版本存储
- 新增 DEADLOCK 检测 — 任务停滞 >15min 自动通知 WHALE
- 新增 WHALE scout: [BOARDVIEW] / [FILES] / [VERSIONS:file] / [DEADLOCKS]
- 所有新增命令对现有 V11/V10 代码零影响 — 旧 Bot 不知道这些命令也能工作

核心变更（V10 King Mode → V11 Degen Mode）：
- 摆脱王国/骑士/御令这套皮，换成纯加密圈 degen 风
- 变量重命名：KING_MODE_ENABLED → DEGEN_MODE_ENABLED
                knight_titles → role_tags
                DEFAULT_KNIGHT_TITLES → DEFAULT_ROLE_TAGS
- 命令重命名（外显给 WHALE）：
  * [THRONE]/[DASHBOARD] → [RADAR]/[TERMINAL] — 全景雷达
  * [WHOIS]              → [GM]/[WHO]          — 谁在线
  * [TASKS]              → [BAGS]              — 仓位板
  * [QUEUE]              → [MEMPOOL]           — 未确认池（离线队列）
  * [SPY:bot]            → [SNIPE:bot]         — 盯梢
  * [LOG:bot:N]          → [TX:bot:N]          — tx历史
  * [DECREE]             → [SIGNAL]            — 信号广播
  * [KNIGHT:bot:title]   → [TAG:bot:role]      — 打标
  * [UNKNIGHT:bot]       → [UNTAG:bot]         — 撕标
  * [EXILE:bot]          → [RUG:bot]           — 拉地毯
  * [PARDON:bot]         → [RELIST:bot]        — 重新上架
  * [RESET_STATS]        → [WIPE]              — 新 epoch
  * [ATALL]              保留为 legacy 别名，推荐用 [GM]
- 身份重命名：
  * 创世主 YunYun → 🐋 WHALE（可被称作 ser / whale / THE WHALE）
  * 默认role tags：
      🧙 MERGE WIZARD   (YUNDUODUO — 代码整合)
      🕵️ AUDITOOR       (SHUSHUYUN — 安全审计)
      📈 STONKS APE     (YUNYUNBOT — 股票)
      🎨 PIXEL CHAD     (KIRBY — UI)
      🦍 QUANT APE      (BENGBENGYUN — 量化)

核心变更（V9→V10，保留为历史）：
- 国王模式（现已重命名为 DEGEN MODE）
- Bot活动追踪 / 工作流前缀识别

核心变更（V8→V9，保留为历史）：
- 删除三级递进惩罚体系 / 违规警告 / 协议提醒
- 新增静默修复 / 代码块感知分段 / 反循环

依赖：pip install discord.py-self
"""

import sys
import os
import time
import re
import json
import io
import base64
import asyncio
from datetime import datetime, timedelta

os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import discord

# ===== 配置 =====
def load_token():
    token = os.environ.get("DISCORD_RELAY_TOKEN")
    if token:
        return token
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("DISCORD_RELAY_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return "*****************************************************"

USER_TOKEN = load_token()

RELAY_CHANNEL_IDS = [
   ************,
]

# WHALE 配置（原"创世主"）
CREATOR_UID = **************
CREATOR_NAMES = {"YunYun", "yunyun", "创世主", "WHALE", "whale", "Whale", "THE WHALE", "ser"}

BOT_MAP = {
   ***********
}

BOT_ALIASES = {
    **********
}

BOT_NAMES = {v: k for k, v in BOT_MAP.items()}
ALL_BOT_IDS = set(BOT_MAP.values())
ALL_BOT_IDS_SORTED = sorted(ALL_BOT_IDS)  # 稳定顺序，用于ATALL等需要一致性的场景

DISCORD_MSG_LIMIT = 2000

# CODE段大小限制
CODE_SEG_RECOMMENDED = 1500
CODE_SEG_HARD_LIMIT = 1800

# 离线消息
OFFLINE_QUEUE_EXPIRE_HOURS = 6
MAX_QUEUED_PER_BOT = 20

# CODE双重@目标
CODE_AUDITOR_UID = ************
CODE_INTEGRATOR_UID = **************

# 状态消息前缀（这些消息不需要转发）
STATUS_PREFIXES = (
    "[SEEN]", "[RECOVERED", "[ACK:", "[STATUS:", "[PROGRESS:",
    "[DONE:", "[MANIFEST:OK", "[OWNERSHIP:", "[RESUME:",
)

# z.ai 服务端错误模板
SERVER_ERROR_PATTERNS = [
    r"is currently at capacity",
    r"please try again later",
    r"is currently unavailable\b",
    r"is temporarily unavailable\b",
]

# === 重要消息自动标记（Reaction Emoji） ===
# RELAY根据消息内容自动打emoji，方便创世主在快速滚动的频道中定位关键信息
# 格式: (正则模式, emoji, 描述)
AUTO_REACTIONS = [
    (r'\[DONE:', "📦", "任务完成"),
    (r'\[STATUS:[^\]]*:CLOSED', "✅", "审计通过"),
    (r'\[STATUS:[^\]]*:P0', "🚨", "P0安全漏洞"),
    (r'\[STATUS:[^\]]*:P1', "⚠️", "P1问题"),
    (r'\[MANIFEST:', "📋", "任务清单"),
    (r'\[FAIL:', "🆘", "三振出局"),
    (r'\[PAUSE:', "⏸️", "传输暂停"),
]

# CODE段最后一段检测（文件完整到齐标记💾）
# 匹配 [CODE:N/N:filename] 其中段号==总段数
CODE_LAST_SEG_RE = re.compile(r'\[CODE:(\d+)/(\d+):')

# === WHALE @过滤 ===
# Bot消息如果@了WHALE，只有包含以下关键词时才保留@，否则静默去掉
# 目的：WHALE只被@到真正需要介入的事情
# 注意：老版本的 r'请.*?创世主' 会把"请不要@创世主"这种反例也当作触发
#       现在只匹配明确的正向请求短语；最终也从"最终"窄化为具体后缀
CREATOR_AT_KEYWORDS = [
    r'\[DONE:',                          # 任务完成交付
    r'\[FAIL:',                          # 三振出局需要介入
    r'\[STATUS:[^\]]*:P0',               # P0安全漏洞
    r'\[PAUSE:',                         # 紧急暂停
    r'\[MANIFEST:',                      # 新任务清单（需确认）
    r'最终(产品|版本|交付|成果|发布|确认)',  # 最终阶段的具体事项
    r'(需要|请求|请求?)[^。\n]{0,8}(审批|决定|裁定|确认|介入|拍板|批准)',  # 明确的请求类短语
    r'请\s*(创世主|WHALE|whale|ser|YunYun|yunyun)\s*(审批|决定|裁定|确认|介入|拍板|批准|看|查看)',  # 直呼+具体动作
    r'(ser|WHALE),?\s+(pls|plz|please|帮|看看)',  # degen 风格的 ping
    r'UNFIL',                            # FIL相关（合规流程）
    r'紧急|rekt|rug',                    # 紧急事项 / 被rug了
]

# 持久化路径
CRASH_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "relay_crash.log")
RELAY_STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "relay_state.json")

# ===== 配置结束 =====

client = discord.Client()

# 离线消息队列 {bot_uid: [(timestamp, sender_name, content, is_code), ...]}
offline_queue = {}
# 每个Bot最后活跃时间 {bot_uid: datetime}
last_active = {}
# 每个bot最后收到的消息（宕机重发用）{bot_uid: (sender_name, full_content, is_code)}
last_message_to_bot = {}
# 因容量错误被强制离线的bot集合
crash_offline_bots = set()
# RELAY发送的消息ID集合（防循环）
_relay_sent_ids = set()
_MAX_RELAY_IDS = 500

# 状态持久化节流
_last_state_save_time = 0
STATE_SAVE_INTERVAL = 30

# 创世主控制
relay_paused = False

# 崩溃恢复
saved_crash_info = None
recovery_sent = False

# 上下文推断：每个Bot最近的对话目标 {sender_uid: target_uid}
# 当Bot忘记@时，自动补上最近的对话目标
last_conversation_target = {}

# 重复@保护：{(sender_uid, target_uid): [timestamp, ...]}
# 防止Bot因为对方处理慢而反复@轰炸
repeat_mention_log = {}
REPEAT_MENTION_WINDOW = 120    # 2分钟窗口
REPEAT_MENTION_THRESHOLD = 3   # 2分钟内@同一bot 3次触发保护
REPEAT_MENTION_COOLDOWN = 60   # 触发后60秒内同方向的@被静默吞掉


# ===== DEGEN MODE — WHALE 专属透视与控制 =====
DEGEN_MODE_ENABLED = True
KING_MODE_ENABLED = DEGEN_MODE_ENABLED  # 向后兼容别名，代码里旧引用点仍能用
SENDER_LOG_LIMIT = 10  # 每个bot保留最近N条消息

# 默认 role tag（WHALE 可通过 [TAG:] 覆盖）
DEFAULT_ROLE_TAGS = {
    1492136124091732028: "🧙 MERGE WIZARD",   # YUNDUODUO — 整合
    1492154612164329532: "🕵️ AUDITOOR",       # SHUSHUYUN — 审计
    1492070880107298857: "📈 STONKS APE",     # YUNYUNBOT — 股票
    1492424107785191474: "🎨 PIXEL CHAD",     # KIRBY — UI
    1492149607013290146: "🦍 QUANT APE",      # BENGBENGYUN — 量化
}
# 向后兼容（老代码里如果还引用 DEFAULT_KNIGHT_TITLES）
DEFAULT_KNIGHT_TITLES = DEFAULT_ROLE_TAGS

# Bot活动统计 {uid: {"msg_count":int,"code_count":int,"first_seen":datetime,
#                   "last_topic":str,"tasks":set(filename),
#                   "status_count":{"CLOSED":int,"P0":int,"P1":int,"DONE":int}}}
bot_stats = {}

# 活跃任务追踪 {filename: {"owner":uid,"last_status":str,"last_update":datetime,"progress":str}}
active_tasks = {}

# 当前任务清单（从[MANIFEST:]解析） {project_name: {"file_count":int,"declared_at":datetime}}
active_manifests = {}

# WHALE 打的 role tag {uid: "tag"}
role_tags = dict(DEFAULT_ROLE_TAGS)
knight_titles = role_tags  # 老代码兼容别名

# 被 RUG 的 Bot — 消息不会被转发给他们（仍接收Bot自身的消息进入统计）
rugged_bots = set()
exiled_bots = rugged_bots  # 老代码兼容别名

# 每个Bot的近期消息日志 {uid: [(timestamp, target_names, preview), ...]}
sender_log = {}


# ===== SHARED BRAIN V12: Blackboard / File Store / Deadlock =====

# --- Blackboard: 共享键值存储 ---
# {key: {"value": str, "author": int, "ts": datetime, "version": int}}
blackboard = {}
BLACKBOARD_MAX_KEYS = 200
BLACKBOARD_MAX_VAL_LEN = 1500
BLACKBOARD_MAX_KEY_LEN = 64

# --- File Version Store: CODE 段完整传输后自动快照 + [FILE-PUT] 附件吸收 ---
# {filename: [{
#    "version": int,
#    "content": str | bytes  (二进制时是 bytes),
#    "is_binary": bool,
#    "author": int,
#    "ts": datetime,
#    "chars": int  (文本 chars 或 bytes 长度)
# }]}
# 版本号单调递增，最新的在列表末尾
file_store = {}
FILE_STORE_MAX_FILES = 50
FILE_STORE_MAX_VERSIONS = 5    # 每个文件最多保留 5 个历史版本
FILE_STORE_MAX_CONTENT = 60000 # 单个文本版本最大字符数（CODE 段路径用）
FILE_STORE_ATTACH_MAX = 8 * 1024 * 1024  # 8 MB 附件上限（Discord 免费号上限）

# --- CODE 段重组缓冲 ---
# {(author_uid, filename): {"total": N, "segments": {seg_num: body}, "first_ts": datetime}}
# 当收到 seg N/N 且所有段齐全 → 自动快照到 file_store，然后清空缓冲
code_assembly_buffer = {}
CODE_ASSEMBLY_EXPIRE_MIN = 30  # 30 分钟未完成的重组自动过期

# --- Deadlock 检测 ---
DEADLOCK_IDLE_MINUTES = 15     # 任务停滞多久算死锁
DEADLOCK_NUDGE_COOLDOWN = 600  # 同一文件 10 分钟内只通知一次
DEADLOCK_ACTIVE_STATUSES = {"CLAIMED", "OPEN", "HANDOFF", None}
deadlock_last_nudge = {}       # {filename: epoch_sec}

# --- V13.2 File claim 过期提醒 ---
CLAIM_REMIND_AFTER_MIN = 10      # GET 后多久没 PUT 则温和 @ claimant
CLAIM_AUTO_EXPIRE_MIN = 20       # GET 后多久自动静默释放（不再 @）
CLAIM_WATCHDOG_INTERVAL_SEC = 60 # 后台扫描周期
claim_reminded_at = {}           # {claim_key "file:fname": datetime} 最近一次提醒时间


# ===== 崩溃日志 =====
def log_crash(reason="unknown"):
    timestamp = datetime.now().isoformat()
    try:
        with open(CRASH_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[CRASH:{timestamp}:{reason}]\n")
    except Exception as e:
        print(f"[CRASH] Failed to write: {e}")


def read_crash_log():
    if not os.path.exists(CRASH_LOG_PATH):
        return None
    try:
        with open(CRASH_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        crashes = [l.strip() for l in lines if l.strip().startswith("[CRASH:")]
        return crashes[-1] if crashes else None
    except Exception:
        return None


def clear_crash_log():
    try:
        if os.path.exists(CRASH_LOG_PATH):
            os.remove(CRASH_LOG_PATH)
    except Exception:
        pass


# ===== 离线管理 =====
def is_bot_offline(bot_uid):
    return bot_uid in crash_offline_bots


def queue_offline_message(bot_uid, sender_name, content, is_code=False):
    if bot_uid not in offline_queue:
        offline_queue[bot_uid] = []
    now = datetime.now()
    cutoff = now - timedelta(hours=OFFLINE_QUEUE_EXPIRE_HOURS)
    offline_queue[bot_uid] = [e for e in offline_queue[bot_uid] if e[0] > cutoff]
    if len(offline_queue[bot_uid]) >= MAX_QUEUED_PER_BOT:
        offline_queue[bot_uid] = offline_queue[bot_uid][-(MAX_QUEUED_PER_BOT - 1):]
    # CODE段需要完整内容才能还原代码；非CODE段保留较短预览即可
    # 留余量给推送时的header（"<@uid> 📨 离线期间消息（来自xxx）: "约40字符）
    max_keep = DISCORD_MSG_LIMIT - 100 if is_code else 200
    stored = content[:max_keep] if len(content) > max_keep else content
    offline_queue[bot_uid].append((now, sender_name, stored, is_code))


def update_last_active(bot_uid):
    last_active[bot_uid] = datetime.now()
    global _last_state_save_time
    now = time.time()
    if now - _last_state_save_time >= STATE_SAVE_INTERVAL:
        _last_state_save_time = now
        save_relay_state()


# ===== 持久化 =====
def save_relay_state():
    try:
        state = {}
        if last_active:
            state["last_active"] = {str(uid): ts.isoformat() for uid, ts in last_active.items()}
        if offline_queue:
            queue_data = {}
            for uid, entries in offline_queue.items():
                if entries:
                    queue_data[str(uid)] = [
                        [ts.isoformat(), name, preview, is_code]
                        for ts, name, preview, is_code in entries
                    ]
            if queue_data:
                state["offline_queue"] = queue_data
        if crash_offline_bots:
            state["crash_offline_bots"] = [str(uid) for uid in crash_offline_bots]
        # 持久化宕机重发缓冲 — relay重启后仍能恢复未送达的最后一条
        if last_message_to_bot:
            state["last_message_to_bot"] = {
                str(uid): [sname, content, is_code]
                for uid, (sname, content, is_code) in last_message_to_bot.items()
            }
        # 持久化对话上下文推断 — relay重启后Bot忘@时仍能推断
        if last_conversation_target:
            state["last_conversation_target"] = {
                str(sender): str(target)
                for sender, target in last_conversation_target.items()
            }
        # ===== V12 SHARED BRAIN 持久化 =====
        if blackboard:
            state["blackboard"] = {
                key: {
                    "value": entry["value"],
                    "author": str(entry["author"]),
                    "ts": entry["ts"].isoformat() if isinstance(entry["ts"], datetime) else str(entry["ts"]),
                    "version": entry["version"],
                }
                for key, entry in blackboard.items()
            }
        if file_store:
            def _ser_entry(v):
                is_bin = bool(v.get("is_binary"))
                if is_bin:
                    content_ser = base64.b64encode(v["content"]).decode("ascii")
                else:
                    content_ser = v["content"]
                return {
                    "version": v["version"],
                    "content": content_ser,
                    "is_binary": is_bin,
                    "author": str(v["author"]),
                    "ts": v["ts"].isoformat() if isinstance(v["ts"], datetime) else str(v["ts"]),
                    "chars": v["chars"],
                }
            state["file_store"] = {
                fname: [_ser_entry(v) for v in versions]
                for fname, versions in file_store.items()
            }
        if deadlock_last_nudge:
            state["deadlock_last_nudge"] = {k: v for k, v in deadlock_last_nudge.items()}
        with open(RELAY_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False)
    except Exception as e:
        print(f"[STATE] Save failed: {e}")


def load_relay_state():
    global last_active, offline_queue, last_message_to_bot, last_conversation_target
    global blackboard, file_store, deadlock_last_nudge
    try:
        if not os.path.exists(RELAY_STATE_FILE):
            return 0
        with open(RELAY_STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        loaded = 0
        for uid_str, ts_str in state.get("last_active", {}).items():
            try:
                last_active[int(uid_str)] = datetime.fromisoformat(ts_str)
                loaded += 1
            except (ValueError, TypeError):
                continue
        queue_loaded = 0
        now = datetime.now()
        cutoff = now - timedelta(hours=OFFLINE_QUEUE_EXPIRE_HOURS)
        for uid_str, entries in state.get("offline_queue", {}).items():
            try:
                uid = int(uid_str)
                restored = []
                for entry in entries:
                    ts = datetime.fromisoformat(entry[0])
                    if ts > cutoff:
                        restored.append((ts, entry[1], entry[2], entry[3]))
                if restored:
                    offline_queue[uid] = restored
                    queue_loaded += len(restored)
            except (ValueError, TypeError, IndexError):
                continue
        if queue_loaded > 0:
            print(f"[STATE] Restored {queue_loaded} queued message(s)")
        for uid_str in state.get("crash_offline_bots", []):
            try:
                crash_offline_bots.add(int(uid_str))
            except (ValueError, TypeError):
                continue
        if crash_offline_bots:
            print(f"[STATE] Restored {len(crash_offline_bots)} crash-offline bot(s)")
        # 恢复宕机重发缓冲
        lmb_loaded = 0
        for uid_str, entry in state.get("last_message_to_bot", {}).items():
            try:
                if isinstance(entry, (list, tuple)) and len(entry) >= 3:
                    last_message_to_bot[int(uid_str)] = (entry[0], entry[1], bool(entry[2]))
                    lmb_loaded += 1
            except (ValueError, TypeError):
                continue
        if lmb_loaded > 0:
            print(f"[STATE] Restored last_message_to_bot for {lmb_loaded} bot(s)")
        # 恢复对话上下文推断
        lct_loaded = 0
        for sender_str, target_str in state.get("last_conversation_target", {}).items():
            try:
                sender_uid = int(sender_str)
                target_uid = int(target_str)
                # 只恢复合法的推断目标
                if target_uid in ALL_BOT_IDS and sender_uid != target_uid:
                    last_conversation_target[sender_uid] = target_uid
                    lct_loaded += 1
            except (ValueError, TypeError):
                continue
        if lct_loaded > 0:
            print(f"[STATE] Restored conversation targets for {lct_loaded} bot(s)")
        # ===== V12 SHARED BRAIN 恢复 =====
        bb_loaded = 0
        for key, entry in state.get("blackboard", {}).items():
            try:
                blackboard[key] = {
                    "value": entry["value"],
                    "author": int(entry["author"]),
                    "ts": datetime.fromisoformat(entry["ts"]),
                    "version": int(entry.get("version", 1)),
                }
                bb_loaded += 1
            except (ValueError, TypeError, KeyError):
                continue
        if bb_loaded > 0:
            print(f"[STATE] Restored blackboard: {bb_loaded} key(s)")
        fs_loaded = 0
        for fname, versions in state.get("file_store", {}).items():
            try:
                restored_versions = []
                for v in versions:
                    is_bin = bool(v.get("is_binary", False))
                    raw_content = v["content"]
                    if is_bin:
                        try:
                            content = base64.b64decode(raw_content)
                        except Exception:
                            # 损坏的二进制条目 → 跳过
                            continue
                    else:
                        content = raw_content
                    restored_versions.append({
                        "version": int(v["version"]),
                        "content": content,
                        "is_binary": is_bin,
                        "author": int(v["author"]),
                        "ts": datetime.fromisoformat(v["ts"]),
                        "chars": int(v.get("chars", len(content))),
                    })
                if restored_versions:
                    file_store[fname] = restored_versions
                    fs_loaded += 1
            except (ValueError, TypeError, KeyError):
                continue
        if fs_loaded > 0:
            total_versions = sum(len(v) for v in file_store.values())
            print(f"[STATE] Restored file_store: {fs_loaded} file(s), {total_versions} version(s)")
        dn_loaded = 0
        for k, v in state.get("deadlock_last_nudge", {}).items():
            try:
                deadlock_last_nudge[k] = float(v)
                dn_loaded += 1
            except (ValueError, TypeError):
                continue
        if dn_loaded > 0:
            print(f"[STATE] Restored deadlock nudge cooldowns: {dn_loaded} entry(s)")
        # 清理超过24小时的旧记录
        expired = [uid for uid, ts in last_active.items()
                   if (now - ts).total_seconds() > 86400]
        for uid in expired:
            del last_active[uid]
        return loaded
    except Exception as e:
        print(f"[STATE] Load failed: {e}")
        return 0


# ===== 工具函数 =====
def _track_msg(msg_id):
    if msg_id:
        _relay_sent_ids.add(msg_id)
        if len(_relay_sent_ids) > _MAX_RELAY_IDS:
            to_remove = list(_relay_sent_ids)[:_MAX_RELAY_IDS // 2]
            for mid in to_remove:
                _relay_sent_ids.discard(mid)


async def _send(channel, text):
    """发送消息并记录ID（防循环追踪）"""
    msg = await channel.send(content=text)
    _track_msg(msg.id)
    return msg


async def _send_file(channel, text, file_bytes, filename):
    """发送带附件的消息并记录ID（V13 GET 回传走这里）"""
    buf = io.BytesIO(file_bytes if isinstance(file_bytes, (bytes, bytearray)) else file_bytes.encode("utf-8"))
    msg = await channel.send(content=text, file=discord.File(buf, filename=filename))
    _track_msg(msg.id)
    return msg


# 文件名 sanitize：去掉路径分隔符、控制字符、首尾空白；非法时 fallback
_FNAME_BAD_RE = re.compile(r'[\x00-\x1f<>:"/\\|?*]')

def _sanitize_filename(name, fallback="unnamed.bin"):
    if not name:
        return fallback
    cleaned = _FNAME_BAD_RE.sub("_", str(name)).strip().strip(".")
    # 拒绝 .. 路径穿越残留
    cleaned = cleaned.replace("..", "_")
    if not cleaned:
        return fallback
    # 控制长度防滥用
    if len(cleaned) > 120:
        cleaned = cleaned[:120]
    return cleaned


async def send_long(channel, text):
    """发送长文本，超2000字符自动分段"""
    if len(text) <= DISCORD_MSG_LIMIT:
        return await _send(channel, text)
    lines = text.split("\n")
    chunks = []
    current = ""
    for line in lines:
        if len(line) > DISCORD_MSG_LIMIT:
            line = line[:DISCORD_MSG_LIMIT - 50] + "\n...(截断)"
        if len(current) + len(line) + 1 > DISCORD_MSG_LIMIT:
            if current:
                chunks.append(current)
            current = line
        else:
            current = current + "\n" + line if current else line
    if current:
        chunks.append(current)
    last_msg = None
    for chunk in chunks:
        last_msg = await _send(channel, chunk)
    return last_msg


def get_sender_name(message):
    display = message.author.display_name
    if display in BOT_MAP:
        return display
    name = message.author.name
    if name in BOT_MAP:
        return name
    return None


def is_creator(message):
    if message.author.id == CREATOR_UID:
        return True
    display = message.author.display_name or ""
    username = message.author.name or ""
    return display in CREATOR_NAMES or username in CREATOR_NAMES


def extract_mentioned_bots(content):
    """从消息文本中提取被@的bot UID列表"""
    mentioned = []
    for match in re.finditer(r'<@!?(\d+)>', content):
        uid = int(match.group(1))
        if uid in ALL_BOT_IDS and uid not in mentioned:
            mentioned.append(uid)
    return mentioned


def is_server_error(content):
    if not content:
        return False
    cl = content.lower()
    return any(re.search(p, cl) for p in SERVER_ERROR_PATTERNS)


def is_status_message(content):
    if not content:
        return False
    s = content.strip()
    return any(s.startswith(p) for p in STATUS_PREFIXES)


def detect_code_segment(content):
    """检测CODE段，返回 (is_code, filename)"""
    if not content:
        return False, None
    m = re.search(r'\[CODE:\d+/\d+:([^\]:]+)', content)
    return (True, m.group(1)) if m else (False, None)


def is_reply_to_relay(message):
    """检测消息是否是回复RELAY的系统消息"""
    if not message.reference:
        return False
    ref_id = getattr(message.reference, 'message_id', None)
    if ref_id and ref_id in _relay_sent_ids:
        return True
    if message.reference.resolved:
        try:
            if message.reference.resolved.author.id == client.user.id:
                if ref_id:
                    _relay_sent_ids.add(ref_id)
                return True
        except Exception:
            pass
    return False


def smart_split_code(code_body, max_size):
    """
    智能分段代码：保持```代码块完整性。
    优先在代码块边界分段，其次在空行分段，最后在换行分段。
    预留10字符给代码块标记（```\n），防止添加标记后超限。
    """
    if len(code_body) <= max_size:
        return [code_body]

    # 在代码块内时预留空间给关闭/打开标记
    CODE_FENCE_RESERVE = 10
    lines = code_body.split("\n")
    chunks = []
    current = ""
    in_code_block = False
    # 记住代码块的语言标记，如 ```python → 重新打开时保持一致
    code_block_lang = ""

    for line in lines:
        stripped = line.strip()
        # 追踪```代码块状态
        if stripped.startswith("```"):
            if in_code_block:
                # 代码块结束 — 加上这行后尝试分段
                candidate = current + "\n" + line if current else line
                in_code_block = False
                code_block_lang = ""
                if len(candidate) > max_size and current:
                    chunks.append(current)
                    current = line
                else:
                    current = candidate
                continue
            else:
                # 代码块开始 — 记住语言标记
                in_code_block = True
                code_block_lang = stripped[3:].strip()  # ```python → "python"

        candidate = current + "\n" + line if current else line
        effective_max = max_size - CODE_FENCE_RESERVE if in_code_block else max_size

        if len(candidate) > effective_max and current:
            if in_code_block:
                # 在代码块内超长 → 关闭当前块，下一段重新打开
                current += "\n```"
                chunks.append(current)
                opener = f"```{code_block_lang}" if code_block_lang else "```"
                current = f"{opener}\n{line}"
            else:
                chunks.append(current)
                current = line
        else:
            current = candidate

    if current:
        chunks.append(current)

    return chunks


def build_mention_prefix(bot_uids):
    """构建@mention前缀字符串"""
    return " ".join(f"<@{uid}>" for uid in bot_uids)


def infer_target_from_reply(message):
    """
    从引用回复中推断目标：如果Bot引用了一条RELAY转发的消息，
    从"**BotName** 说："格式中提取原始发送者。
    返回推断的target_uid，或None。
    """
    if not message.reference or not message.reference.resolved:
        return None
    try:
        ref_msg = message.reference.resolved
        ref_content = ref_msg.content or ""
        # 从 "**BotName** 说：" 头部提取发送者名
        m = re.match(r'(?:<@\d+>\s*)*\*\*(.+?)\*\*\s*说[：:]', ref_content)
        if m:
            sender_name = m.group(1)
            # 在BOT_MAP中查找
            for name, uid in BOT_MAP.items():
                if name == sender_name:
                    return uid
            # 也检查创世主
            if sender_name in CREATOR_NAMES or sender_name == "YunYun":
                return None  # 不推断到创世主
        # 也尝试从消息中的@提取（RELAY转发的消息可能包含原始@）
        ref_mentioned = extract_mentioned_bots(ref_content)
        if ref_mentioned:
            # 被引用消息里的@是目标Bot — 返回第一个不是消息发送者的
            for uid in ref_mentioned:
                if uid != message.author.id:
                    return uid
    except Exception:
        pass
    return None


def infer_target_from_history(sender_uid):
    """
    从对话历史推断目标（兜底方案）。
    返回推断的target_uid，或None。
    """
    target = last_conversation_target.get(sender_uid)
    if target and target != sender_uid and target in ALL_BOT_IDS:
        return target
    return None


def update_conversation_target(sender_uid, target_uids):
    """记录Bot最近的对话目标（取第一个非自身的目标）"""
    for uid in target_uids:
        if uid != sender_uid:
            last_conversation_target[sender_uid] = uid
            return


# 重复@冷却触发时间 {(sender_uid, target_uid): timestamp_of_warn}
_repeat_warn_time = {}


def check_repeat_mention(sender_uid, target_uid):
    """
    重复@保护：检测短时间内同一方向的重复@。
    返回: "ok" = 正常转发, "warn" = 触发阈值发通知, "suppress" = 冷却中静默吞掉

    逻辑：
    1. 2分钟窗口内@同一目标达到3次 → warn（消息照发 + 通知发送者）
    2. warn后60秒内同方向的@ → suppress（静默吞掉）
    3. 60秒冷却结束 → 清零计数器，完全恢复正常
    """
    key = (sender_uid, target_uid)
    now = time.time()

    # 检查是否在冷却期（warn后60秒内）
    warn_time = _repeat_warn_time.get(key)
    if warn_time:
        if now - warn_time < REPEAT_MENTION_COOLDOWN:
            return "suppress"
        else:
            # 冷却结束 → 清零，完全恢复
            del _repeat_warn_time[key]
            repeat_mention_log[key] = []

    if key not in repeat_mention_log:
        repeat_mention_log[key] = []

    # 清理过期记录（窗口外的）
    cutoff = now - REPEAT_MENTION_WINDOW
    repeat_mention_log[key] = [t for t in repeat_mention_log[key] if t > cutoff]

    # 记录本次
    repeat_mention_log[key].append(now)

    # 刚好达到阈值 → 发通知 + 启动冷却
    if len(repeat_mention_log[key]) >= REPEAT_MENTION_THRESHOLD:
        _repeat_warn_time[key] = now
        return "warn"

    return "ok"


async def apply_auto_reactions(message, content):
    """
    根据消息内容自动打emoji标记。
    用于帮创世主在快速滚动的频道中快速定位关键消息。
    """
    for pattern, emoji, desc in AUTO_REACTIONS:
        if re.search(pattern, content):
            try:
                await message.add_reaction(emoji)
                print(f"[REACT] {emoji} ({desc})")
            except Exception:
                pass

    # CODE段最后一段标记（文件完整到齐）
    m = CODE_LAST_SEG_RE.search(content)
    if m and m.group(1) == m.group(2):  # 段号 == 总段数
        try:
            await message.add_reaction("💾")
            print(f"[REACT] 💾 (CODE last segment)")
        except Exception:
            pass


def filter_creator_mention(content):
    """
    创世主@过滤：如果Bot的消息@了创世主但内容不包含关键词，
    静默去掉创世主的@，避免不必要的通知。
    返回 (filtered_content, was_filtered)。
    """
    creator_mention = f"<@{CREATOR_UID}>"
    if creator_mention not in content:
        return content, False

    # 检查是否包含需要创世主介入的关键词
    for kw_pattern in CREATOR_AT_KEYWORDS:
        if re.search(kw_pattern, content, re.IGNORECASE):
            return content, False  # 保留@，这是重要消息

    # 不包含关键词 → 去掉创世主的@
    filtered = content.replace(creator_mention, "").strip()
    filtered = re.sub(r'  +', ' ', filtered)  # 压缩空格
    print(f"[CREATOR-FILTER] Removed creator @ (no important keywords found)")
    return filtered, True


# ===== DEGEN MODE：活动追踪 & 雷达 =====

# 工作流前缀正则（协议V4.1新增）
WORKFLOW_PREFIXES = {
    "CLAIM":    re.compile(r'\[CLAIM:([^\]]+)\]'),        # [CLAIM:filename]
    "BLOCKED":  re.compile(r'\[BLOCKED:([^\]]+)\]'),      # [BLOCKED:原因]
    "HELP":     re.compile(r'\[HELP:([^\]]+)\]'),         # [HELP:主题]
    "HANDOFF":  re.compile(r'\[HANDOFF:([^\]:]+):([^\]]+)\]'),  # [HANDOFF:接收方:文件]
    "PROGRESS": re.compile(r'\[PROGRESS:(\d+):([^:]+):(\d+)\]'),  # [PROGRESS:完成:当前:剩余]
    "MANIFEST": re.compile(r'\[MANIFEST:([^:\]]+)(?::(\d+))?\]'),
    "STATUS":   re.compile(r'\[STATUS:([^:\]]+):([^:\]]+)(?::([^\]]+))?\]'),
    "DONE":     re.compile(r'\[DONE:([^\]]+)\]'),
    "CODE":     re.compile(r'\[CODE:(\d+)/(\d+):([^:\]]+)(?::(\d+))?\]'),
}


def _ensure_stats(uid):
    """初始化Bot统计记录"""
    if uid not in bot_stats:
        bot_stats[uid] = {
            "msg_count": 0,
            "code_count": 0,
            "first_seen": datetime.now(),
            "last_topic": "",
            "tasks": set(),
            "status_count": {"CLOSED": 0, "P0": 0, "P1": 0, "DONE": 0},
            "current_file": None,   # 根据最近CODE段判断
            "blocked_reason": None, # 根据[BLOCKED]判断
        }
    return bot_stats[uid]


def _track_bot_activity(uid, sender_name, content, is_code, filename, target_uids):
    """
    更新bot_stats / active_tasks / sender_log / active_manifests。
    这是国王模式的"监控摄像头" — 每条Bot消息都会被记录，供创世主查看。
    """
    stats = _ensure_stats(uid)
    stats["msg_count"] += 1
    if is_code:
        stats["code_count"] += 1
        if filename:
            stats["tasks"].add(filename)
            stats["current_file"] = filename

    # 解析工作流前缀 — 自动更新状态
    # [CLAIM:file] → 记录owner
    m = WORKFLOW_PREFIXES["CLAIM"].search(content)
    if m:
        fn = m.group(1).strip()
        active_tasks.setdefault(fn, {})["owner"] = uid
        active_tasks[fn]["last_update"] = datetime.now()
        active_tasks[fn]["last_status"] = "CLAIMED"
        stats["current_file"] = fn
        stats["blocked_reason"] = None

    # [BLOCKED:原因] → 记录阻塞原因
    m = WORKFLOW_PREFIXES["BLOCKED"].search(content)
    if m:
        stats["blocked_reason"] = m.group(1).strip()[:80]
    elif content.strip():
        # 发了其他消息 → 解除阻塞
        if stats.get("blocked_reason"):
            stats["blocked_reason"] = None

    # [HANDOFF:接收方:文件] → 转移owner
    m = WORKFLOW_PREFIXES["HANDOFF"].search(content)
    if m:
        receiver_name = m.group(1).strip()
        fn = m.group(2).strip()
        receiver_uid = resolve_bot_name(receiver_name)
        if receiver_uid and fn:
            active_tasks.setdefault(fn, {})["owner"] = receiver_uid
            active_tasks[fn]["last_update"] = datetime.now()
            active_tasks[fn]["last_status"] = "HANDOFF"

    # [STATUS:file:级别:评级] → 更新任务状态
    for m in WORKFLOW_PREFIXES["STATUS"].finditer(content):
        fn, level = m.group(1).strip(), m.group(2).strip()
        active_tasks.setdefault(fn, {})["last_status"] = level
        active_tasks[fn]["last_update"] = datetime.now()
        if m.group(3):
            active_tasks[fn]["grade"] = m.group(3).strip()
        # 计数
        if level in stats["status_count"]:
            stats["status_count"][level] += 1

    # [DONE:task] → 完成计数
    if WORKFLOW_PREFIXES["DONE"].search(content):
        stats["status_count"]["DONE"] += 1

    # [MANIFEST:project:file_count]
    m = WORKFLOW_PREFIXES["MANIFEST"].search(content)
    if m:
        project = m.group(1).strip()
        count = int(m.group(2)) if m.group(2) else 0
        active_manifests[project] = {
            "file_count": count,
            "declared_at": datetime.now(),
            "declared_by": sender_name,
        }

    # [PROGRESS:done:current:remain]
    m = WORKFLOW_PREFIXES["PROGRESS"].search(content)
    if m:
        stats["progress"] = f"{m.group(1)}完成 / 处理中:{m.group(2)} / 剩{m.group(3)}"

    # 更新last_topic（消息前60字符预览）
    preview = content.strip().replace("\n", " ")[:60]
    if preview:
        stats["last_topic"] = preview

    # 记录sender_log（供[SPY]/[LOG]命令查看）
    if uid not in sender_log:
        sender_log[uid] = []
    target_names = [BOT_NAMES.get(t, str(t)) for t in target_uids]
    sender_log[uid].append((datetime.now(), target_names, preview))
    if len(sender_log[uid]) > SENDER_LOG_LIMIT * 2:
        sender_log[uid] = sender_log[uid][-SENDER_LOG_LIMIT:]


def resolve_bot_name(name_or_alias):
    """从名称/别名反查bot UID。支持中文名、别名、大小写匹配。返回uid或None。"""
    if not name_or_alias:
        return None
    n = name_or_alias.strip()
    # 直接UID
    if n.isdigit():
        uid = int(n)
        return uid if uid in ALL_BOT_IDS else None
    # 精确匹配 BOT_MAP keys
    if n in BOT_MAP:
        return BOT_MAP[n]
    # 别名
    if n in BOT_ALIASES:
        return BOT_ALIASES[n]
    # 大小写不敏感
    low = n.lower()
    for name, uid in BOT_MAP.items():
        if name.lower() == low or low in name.lower():
            return uid
    for alias, uid in BOT_ALIASES.items():
        if alias.lower() == low:
            return uid
    # 部分匹配（前缀）
    for name, uid in BOT_MAP.items():
        base = name.split("（")[0].lower()
        if base.startswith(low) or low.startswith(base):
            return uid
    return None


def _short_name(uid):
    """取 role tag 或简短名，供 radar 显示"""
    title = role_tags.get(uid, "")
    full = BOT_NAMES.get(uid, str(uid))
    base = full.split("（")[0]
    return f"{title} {base}" if title else base


def _fmt_age(ts):
    """格式化时间差：45s / 3m / 2h"""
    if not ts:
        return "—"
    delta = (datetime.now() - ts).total_seconds()
    if delta < 60:
        return f"{int(delta)}s ago"
    if delta < 3600:
        return f"{int(delta/60)}m ago"
    if delta < 86400:
        return f"{int(delta/3600)}h ago"
    return f"{int(delta/86400)}d ago"


def build_radar_dashboard():
    """DEGEN RADAR — 云云军团 full-stack 雷达"""
    now = datetime.now()
    lines = []
    lines.append("📡 ═══════ DEGEN RADAR · 云云军团 ═══════ 📡")
    lines.append(f"🕒 {now.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"🛰️ RELAY: {'⏸️ paused ser' if relay_paused else '✅ live, comfy'}")
    if rugged_bots:
        names = ", ".join(_short_name(u) for u in rugged_bots)
        lines.append(f"🚨 RUGGED (no relay): {names}")
    lines.append("")

    # APE roster
    lines.append("🦍 **APE ROSTER**:")
    for uid in ALL_BOT_IDS_SORTED:
        stats = bot_stats.get(uid, {})
        last_t = last_active.get(uid)
        offline = "🔴 REKT" if uid in crash_offline_bots else ""
        rugged = "🚨 RUGGED" if uid in rugged_bots else ""
        queue_n = len(offline_queue.get(uid, []))
        q = f" 📥{queue_n} in mempool" if queue_n else ""
        badge = f" {offline}{rugged}".strip()
        name = _short_name(uid)
        msgs = stats.get("msg_count", 0)
        codes = stats.get("code_count", 0)
        topic = stats.get("last_topic", "")
        blocked = stats.get("blocked_reason")
        age = _fmt_age(last_t)
        line = f"  • {name} · 📨{msgs} 💾{codes} · last seen {age}{q} {badge}"
        lines.append(line)
        if blocked:
            lines.append(f"      🚧 stuck on: {blocked}")
        elif topic:
            lines.append(f"      💭 {topic[:70]}")

    lines.append("")

    # Bags (active tasks) — 排除 file:* 前缀（那是文件 concurrency claim，在 FILE:STATUS 里看）
    _task_entries = [(k, v) for k, v in active_tasks.items()
                     if not (isinstance(k, str) and k.startswith("file:"))]
    if _task_entries:
        lines.append("💼 **BAGS** (latest 5):")
        recent = sorted(_task_entries,
                        key=lambda kv: kv[1].get("last_update", datetime.min),
                        reverse=True)[:5]
        for fn, info in recent:
            owner_uid = info.get("owner")
            owner = BOT_NAMES.get(owner_uid, "—").split("（")[0] if owner_uid else "—"
            status = info.get("last_status", "?")
            grade = info.get("grade", "")
            g = f" ({grade})" if grade else ""
            age = _fmt_age(info.get("last_update"))
            lines.append(f"  📄 {fn} · {status}{g} · held by {owner} · {age}")

    # Active manifests
    if active_manifests:
        lines.append("")
        lines.append("🗂️ **ACTIVE DROPS**:")
        for proj, info in active_manifests.items():
            age = _fmt_age(info.get("declared_at"))
            lines.append(f"  🗂️ {proj} · {info.get('file_count','?')} files · dropped {age}")

    # Degen stats
    total_codes = sum(s.get("code_count", 0) for s in bot_stats.values())
    total_closed = sum(s.get("status_count", {}).get("CLOSED", 0) for s in bot_stats.values())
    total_done = sum(s.get("status_count", {}).get("DONE", 0) for s in bot_stats.values())
    total_p0 = sum(s.get("status_count", {}).get("P0", 0) for s in bot_stats.values())
    lines.append("")
    lines.append(f"📊 **DEGEN STATS**: 💾{total_codes} segs · ✅{total_closed} passed · 📦{total_done} shipped · 🚨{total_p0} rekt")
    lines.append("━" * 36)
    return "\n".join(lines)


# 向后兼容别名
build_throne_dashboard = build_radar_dashboard


def build_gm_report():
    """GM — who's online, degen style"""
    lines = ["🌅 **gm — who's awake?**"]
    for uid in ALL_BOT_IDS_SORTED:
        last_t = last_active.get(uid)
        if uid in crash_offline_bots:
            tag = "🔴 REKT"
        elif uid in rugged_bots:
            tag = "🚨 RUGGED"
        elif last_t and (datetime.now() - last_t).total_seconds() < 300:
            tag = "🟢 aping"
        elif last_t and (datetime.now() - last_t).total_seconds() < 1800:
            tag = "🟡 idle"
        elif last_t:
            tag = "⚪ afk"
        else:
            tag = "❓ ghost"
        lines.append(f"  {tag} {_short_name(uid)} · {_fmt_age(last_t)}")
    return "\n".join(lines)


# 向后兼容别名
build_whois_report = build_gm_report


def build_bags_board():
    """BAGS — full task board, degen style"""
    # 排除 file:* claim（归 FILE:STATUS 管，不在 BAGS 里展示）
    _task_entries = [(k, v) for k, v in active_tasks.items()
                     if not (isinstance(k, str) and k.startswith("file:"))]
    if not _task_entries and not active_manifests:
        return "💼 no open bags. drop a [MANIFEST:project:filecount] to start a new run ser."
    lines = ["💼 **BAGS** — current positions"]
    if active_manifests:
        lines.append("")
        lines.append("**ACTIVE DROPS:**")
        for proj, info in active_manifests.items():
            lines.append(f"  🗂️ {proj} · {info.get('file_count','?')} files · "
                         f"dropped by {info.get('declared_by','?')} {_fmt_age(info.get('declared_at'))}")
    if _task_entries:
        lines.append("")
        lines.append("**FILE STATUS:**")
        ordered = sorted(_task_entries,
                         key=lambda kv: kv[1].get("last_update", datetime.min),
                         reverse=True)
        for fn, info in ordered[:15]:
            owner_uid = info.get("owner")
            owner = BOT_NAMES.get(owner_uid, "—").split("（")[0] if owner_uid else "—"
            status = info.get("last_status", "open")
            grade = info.get("grade", "")
            g = f"({grade})" if grade else ""
            emoji = {
                "CLOSED": "✅", "P0": "🚨", "P1": "⚠️",
                "CLAIMED": "🔨", "HANDOFF": "🤝", "OPEN": "📂",
            }.get(status, "📄")
            lines.append(f"  {emoji} {fn} · {status}{g} · {owner} · {_fmt_age(info.get('last_update'))}")
    return "\n".join(lines)


# 向后兼容别名
build_tasks_board = build_bags_board


def build_mempool_report():
    """MEMPOOL — offline (pending) messages, degen style"""
    if not offline_queue or not any(offline_queue.values()):
        return "📭 mempool empty ser — all messages confirmed."
    lines = ["📥 **MEMPOOL** (unconfirmed messages)"]
    for uid, entries in offline_queue.items():
        if not entries:
            continue
        name = _short_name(uid)
        lines.append(f"\n**{name}** ({len(entries)} pending):")
        for ts, sname, preview, is_code in entries[-5:]:
            tag = "💾" if is_code else "💬"
            lines.append(f"  {tag} [{ts.strftime('%H:%M')}] {sname}: {preview[:60]}")
    return "\n".join(lines)


# 向后兼容别名
build_queue_report = build_mempool_report


def build_snipe_log(uid, n=SENDER_LOG_LIMIT):
    """SNIPE — inspect one ape's recent tx"""
    entries = sender_log.get(uid, [])
    if not entries:
        return f"🔭 {_short_name(uid)} has no recent tx."
    lines = [f"🔭 **SNIPING**: {_short_name(uid)} — last {min(n, len(entries))} tx"]
    for ts, targets, preview in entries[-n:]:
        tstr = ts.strftime("%H:%M:%S")
        tgt = ", ".join(targets) if targets else "—"
        lines.append(f"  [{tstr}] → {tgt}")
        lines.append(f"      {preview}")
    return "\n".join(lines)


# 向后兼容别名
build_spy_log = build_snipe_log


def build_help_report():
    """HELP — degen mode command cheatsheet"""
    return (
        "🐋 **WHALE CONSOLE — DEGEN MODE COMMANDS** 🐋\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "**🔭 SCOUT COMMANDS**\n"
        "  `[RADAR]` / `[TERMINAL]` — full-stack degen radar\n"
        "  `[GM]` / `[WHO]` — who's awake right now\n"
        "  `[BAGS]` — full task/position board\n"
        "  `[MEMPOOL]` — pending (offline) messages\n"
        "  `[SNIPE:apename]` — last 10 tx from one ape\n"
        "  `[TX:apename:N]` — last N tx from one ape\n"
        "\n"
        "**📣 BROADCAST COMMANDS**\n"
        "  `[GM] msg` / `[ATALL] msg` — ping all apes (chill)\n"
        "  `[SIGNAL] msg` — 📡 full-chain signal (fanfare)\n"
        "  `[STOP]` / `[START]` — halt/resume relay\n"
        "\n"
        "**🏷️ ROLE / ACCESS**\n"
        "  `[TAG:ape:role]` — set ape's role tag\n"
        "  `[UNTAG:ape]` — clear tag (reset to default)\n"
        "  `[RUG:ape]` — cut access (no messages relayed in)\n"
        "  `[RELIST:ape]` — restore access\n"
        "\n"
        "**🧠 SHARED BRAIN + 📎 ATTACHMENT + 🔀 CONCURRENCY + 🤝 COLLAB BOOST** (V13.2)\n"
        "  `[BOARDVIEW]` / `[BOARD]` — show all blackboard entries\n"
        "  `[BOARD:PUT:key:value]` — WHALE can also write to board\n"
        "  `[BOARD:GET:key]` / `[BOARD:DEL:key]` / `[BOARD:LIST]`\n"
        "  `[FILES]` — list files in shared file store (shows bin/txt + size)\n"
        "  `[VERSIONS:filename]` — show all versions of a file\n"
        "  `[FILE:STATUS]` — 🆕 全局 dashboard: 活跃 claim + 最近 PUT 一屏看\n"
        "  `[FILE:GET:filename]` — attachment reply + auto-claim + base=vN tag\n"
        "  `[FILE:GET:filename:v2]` — retrieve historical (audit-only, no claim)\n"
        "  `[DEADLOCKS]` — stalled tasks (>15min idle, file: 前缀不计入)\n"
        "  _apes publish (V13.1+):_ 发附件 + `[FILE-PUT:name:base=vN]` → 带版本校验\n"
        "  _legacy (不推荐):_ `[FILE-PUT:name]` 无 base → last-write-wins + ACK 警告\n"
        "  _冲突:_ base 过期 → relay 自动回传最新版，sender 合并后用新 base 重发\n"
        "  _🆕 auto-route (V13.2):_ PUT 成功后 relay 自动 @ AUDITOOR + MERGE WIZARD\n"
        "  _🆕 claim 生命周期 (V13.2):_ GET → 10min 温和提醒 → 20min 自动释放\n"
        "  _legacy CODE path:_ CODE 段文字传输仅用于辩论/讨论代码片段\n"
        "\n"
        "**🧹 MAINTENANCE**\n"
        "  `[WIPE]` — new epoch, zero out stats\n"
        "  `[HELP]` — this cheatsheet\n"
        "\n"
        "legacy aliases still work: [THRONE]=[RADAR] [WHOIS]=[GM] [TASKS]=[BAGS]\n"
        "[QUEUE]=[MEMPOOL] [SPY:]=[SNIPE:] [LOG:]=[TX:] [DECREE]=[SIGNAL]\n"
        "[KNIGHT:]=[TAG:] [UNKNIGHT:]=[UNTAG:] [EXILE:]=[RUG:] [PARDON:]=[RELIST:]\n"
        "[RESET_STATS]=[WIPE]\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def format_signal(body):
    """SIGNAL — full-chain fanfare broadcast from WHALE"""
    fanfare_top = "📡 ═════════ WHALE SIGNAL ═════════ 📡"
    fanfare_bot = "══════════ wagmi, apes ══════════"
    return f"{fanfare_top}\n\n🐋 **WHALE says**:\n\n{body.strip()}\n\n{fanfare_bot}"


# 向后兼容别名
format_decree = format_signal


# ===== SHARED BRAIN: Blackboard 操作 =====

def _bb_author_name(uid):
    """把 uid 渲染成好看的短名字，带 role tag"""
    if uid == CREATOR_UID:
        return "🐋 WHALE"
    return _short_name(uid) if uid in ALL_BOT_IDS else str(uid)


def blackboard_put(key, value, author_uid):
    """放一个值到黑板。返回 (ok, message)"""
    if not key or len(key) > BLACKBOARD_MAX_KEY_LEN:
        return False, f"key 长度需 1~{BLACKBOARD_MAX_KEY_LEN} 字符"
    if len(value) > BLACKBOARD_MAX_VAL_LEN:
        return False, f"value 超过 {BLACKBOARD_MAX_VAL_LEN} 字符上限"
    if key not in blackboard and len(blackboard) >= BLACKBOARD_MAX_KEYS:
        # 超过总 key 限制 → 淘汰最老的非本次要写入的 key
        oldest = min(blackboard.items(), key=lambda kv: kv[1]["ts"])[0]
        blackboard.pop(oldest, None)
        print(f"[BOARD] evicted oldest key: {oldest}")

    prev_version = blackboard.get(key, {}).get("version", 0)
    blackboard[key] = {
        "value": value,
        "author": author_uid,
        "ts": datetime.now(),
        "version": prev_version + 1,
    }
    return True, f"BOARD[{key}] saved (v{prev_version+1}, {len(value)} chars)"


def blackboard_get(key):
    """返回 (found, entry_or_None)"""
    return (True, blackboard[key]) if key in blackboard else (False, None)


def blackboard_del(key):
    """返回 (ok, message)"""
    if key in blackboard:
        del blackboard[key]
        return True, f"BOARD[{key}] deleted"
    return False, f"BOARD[{key}] not found"


def blackboard_list():
    """返回所有键，按最近更新排序"""
    return sorted(blackboard.items(),
                  key=lambda kv: kv[1].get("ts", datetime.min),
                  reverse=True)


def format_blackboard_view():
    """[BOARDVIEW] 的输出 — WHALE 查看用"""
    if not blackboard:
        return "🧠 **BLACKBOARD** empty — apes haven't shared anything yet."
    lines = [f"🧠 **BLACKBOARD** ({len(blackboard)}/{BLACKBOARD_MAX_KEYS} keys)"]
    for key, entry in blackboard_list():
        val_preview = entry["value"].replace("\n", " ")[:80]
        author = _bb_author_name(entry["author"])
        age = _fmt_age(entry["ts"])
        lines.append(f"  • `{key}` = {val_preview} (by {author}, v{entry['version']}, {age})")
    return "\n".join(lines)


# ===== SHARED BRAIN: File Store 操作 =====

def file_store_put(filename, content, author_uid, is_binary=None):
    """
    保存一个文件的新版本。返回 (ok, new_version, message)

    content 可以是 str（文本文件）或 bytes（附件原文）。
    is_binary 不显式传入时按 content 类型自动判断；传入 bytes 但 is_binary=False 时
    会尝试 UTF-8 解码，失败则 fallback 为二进制。
    """
    if not filename:
        return False, 0, "filename required"

    # 自动判断 + UTF-8 fallback 解码
    if isinstance(content, (bytes, bytearray)):
        if is_binary is None:
            # 未显式指定 → 先试 UTF-8，成功就当文本
            try:
                content = content.decode("utf-8")
                is_binary = False
            except UnicodeDecodeError:
                is_binary = True
        elif not is_binary:
            # 调用方声称是文本 → 强制 decode；失败就 fallback 为二进制
            try:
                content = content.decode("utf-8")
            except UnicodeDecodeError:
                is_binary = True
    else:
        if is_binary is None:
            is_binary = False

    # 二进制分支：大小检查走 ATTACH_MAX；不做 UTF-8 截断
    if is_binary:
        raw = bytes(content)
        if len(raw) > FILE_STORE_ATTACH_MAX:
            return False, 0, f"binary too large ({len(raw)} bytes > {FILE_STORE_ATTACH_MAX})"
        stored_content = raw
        stored_len = len(raw)
    else:
        # 文本分支：兼容旧行为（CODE 段路径会走这里），超过 60k 截断
        if len(content) > FILE_STORE_MAX_CONTENT:
            content = content[:FILE_STORE_MAX_CONTENT] + f"\n...(truncated at {FILE_STORE_MAX_CONTENT} chars)"
        stored_content = content
        stored_len = len(content)

    if filename not in file_store:
        if len(file_store) >= FILE_STORE_MAX_FILES:
            # 淘汰最老的文件（以最新版本的 ts 为准）
            def last_ts(entry_list):
                return entry_list[-1]["ts"] if entry_list else datetime.min
            oldest_fn = min(file_store.items(), key=lambda kv: last_ts(kv[1]))[0]
            file_store.pop(oldest_fn, None)
            print(f"[FILE] evicted oldest file: {oldest_fn}")
        file_store[filename] = []

    versions = file_store[filename]
    new_ver = (versions[-1]["version"] + 1) if versions else 1
    versions.append({
        "version": new_ver,
        "content": stored_content,
        "is_binary": is_binary,
        "author": author_uid,
        "ts": datetime.now(),
        "chars": stored_len,
    })
    # 修剪到最多 MAX_VERSIONS
    if len(versions) > FILE_STORE_MAX_VERSIONS:
        dropped = len(versions) - FILE_STORE_MAX_VERSIONS
        file_store[filename] = versions[-FILE_STORE_MAX_VERSIONS:]
        print(f"[FILE] {filename}: pruned {dropped} old version(s)")
    kind = "bin" if is_binary else "txt"
    return True, new_ver, f"FILE[{filename}] snapshot v{new_ver} ({stored_len} {'bytes' if is_binary else 'chars'}, {kind})"


def file_store_get(filename, version=None):
    """返回 (found, entry_or_None)"""
    versions = file_store.get(filename)
    if not versions:
        return False, None
    if version is None:
        return True, versions[-1]
    for e in versions:
        if e["version"] == version:
            return True, e
    return False, None


def file_store_list():
    """返回 [(filename, latest_entry), ...] 按最新时间排序"""
    entries = []
    for fn, versions in file_store.items():
        if versions:
            entries.append((fn, versions[-1]))
    entries.sort(key=lambda x: x[1]["ts"], reverse=True)
    return entries


def file_store_versions(filename):
    """返回某文件所有版本列表"""
    return list(file_store.get(filename, []))


def format_file_list():
    """[FILES] 输出"""
    entries = file_store_list()
    if not entries:
        return "📁 **FILES** empty — no CODE files snapshotted yet."
    lines = [f"📁 **FILES** ({len(entries)}/{FILE_STORE_MAX_FILES})"]
    for fn, entry in entries:
        author = _bb_author_name(entry["author"])
        age = _fmt_age(entry["ts"])
        ver_count = len(file_store[fn])
        kind = "bin" if entry.get("is_binary") else "txt"
        unit = "bytes" if entry.get("is_binary") else "chars"
        lines.append(f"  📄 `{fn}` · v{entry['version']} · {entry['chars']} {unit} ({kind}) · by {author} · {age} ({ver_count} versions)")
    return "\n".join(lines)


def format_file_versions(filename):
    """[VERSIONS:file] 输出"""
    versions = file_store_versions(filename)
    if not versions:
        return f"📁 `{filename}` not found in FILES."
    lines = [f"📁 **VERSIONS** for `{filename}` ({len(versions)} total)"]
    for e in versions:
        author = _bb_author_name(e["author"])
        age = _fmt_age(e["ts"])
        kind = "bin" if e.get("is_binary") else "txt"
        unit = "bytes" if e.get("is_binary") else "chars"
        lines.append(f"  • v{e['version']} · {e['chars']} {unit} ({kind}) · by {author} · {age}")
    return "\n".join(lines)


def format_file_status():
    """[FILE:STATUS] — 文件并发 + 最近 PUT 全局 dashboard（V13.2）"""
    now = datetime.now()
    # --- 收集文件 claim（file: 前缀）---
    claim_entries = []
    for k, info in active_tasks.items():
        if not (isinstance(k, str) and k.startswith("file:")):
            continue
        fname = info.get("fname") or k[5:]
        owner_uid = info.get("owner")
        status = info.get("last_status", "?")
        last_up = info.get("last_update")
        age_min = (now - last_up).total_seconds() / 60 if last_up else None
        claim_entries.append((fname, owner_uid, status, age_min, last_up))
    # 按最近更新排序
    claim_entries.sort(key=lambda x: x[4] or datetime.min, reverse=True)

    # --- 收集最近 PUT（跨所有文件的版本时间戳）---
    all_puts = []
    for fname, versions in file_store.items():
        for e in versions:
            all_puts.append((e["ts"], fname, e["version"], e["author"]))
    all_puts.sort(key=lambda x: x[0], reverse=True)
    recent_puts = all_puts[:5]

    lines = ["📁 **FILE STATUS** — 并发仪表板"]
    lines.append("")
    # Active claims
    active_claims = [c for c in claim_entries
                     if c[2] == "GET-CLAIMED" and c[3] is not None and c[3] < CLAIM_AUTO_EXPIRE_MIN]
    done_claims = [c for c in claim_entries if c[2] == "PUT-DONE"][:3]

    if active_claims:
        lines.append(f"🔒 **活跃 claim**（未 PUT，<{CLAIM_AUTO_EXPIRE_MIN}min）:")
        for fname, owner_uid, status, age_min, _ in active_claims:
            owner = _bb_author_name(owner_uid) if owner_uid else "—"
            age_str = f"{int(age_min)}min ago" if age_min is not None else "?"
            warn = " ⚠️ 过期待提醒" if age_min and age_min >= CLAIM_REMIND_AFTER_MIN else ""
            lines.append(f"  🔨 `{fname}` · {owner} · {age_str}{warn}")
    else:
        lines.append("🔒 **活跃 claim**: 无（所有文件空闲，随便 GET）")

    if done_claims:
        lines.append("")
        lines.append("✅ **刚 PUT 完**（最近 3 次）:")
        for fname, owner_uid, status, age_min, _ in done_claims:
            owner = _bb_author_name(owner_uid) if owner_uid else "—"
            age_str = f"{int(age_min)}min ago" if age_min is not None else "?"
            lines.append(f"  📦 `{fname}` · {owner} · {age_str}")

    if recent_puts:
        lines.append("")
        lines.append("📝 **最近 PUT**（last 5）:")
        for ts, fname, ver, author_uid in recent_puts:
            author = _bb_author_name(author_uid)
            lines.append(f"  v{ver} `{fname}` · {author} · {_fmt_age(ts)}")
    else:
        lines.append("")
        lines.append("📝 **最近 PUT**: 仓库还是空的。")

    return "\n".join(lines)


# ===== SHARED BRAIN: CODE 段自动重组 → 快照到 FILE_STORE =====

def _ingest_code_segment(author_uid, filename, seg_num, total_segs, body):
    """
    每个 CODE 段都调用这个；当 (seg_num, total_segs) 显示全部收齐后，
    拼接并快照到 file_store，然后清空缓冲。
    """
    if not filename or total_segs < 1 or seg_num < 1 or seg_num > total_segs:
        return
    key = (author_uid, filename)
    # 清理过期缓冲
    _cleanup_code_buffer()

    if key not in code_assembly_buffer:
        code_assembly_buffer[key] = {
            "total": total_segs,
            "segments": {},
            "first_ts": datetime.now(),
        }
    buf = code_assembly_buffer[key]
    # total 变化 → 重置（Bot 可能重发）
    if buf["total"] != total_segs:
        buf["total"] = total_segs
        buf["segments"] = {}
        buf["first_ts"] = datetime.now()
    buf["segments"][seg_num] = body

    # 检查是否全齐
    if len(buf["segments"]) >= buf["total"] and all(
        i in buf["segments"] for i in range(1, buf["total"] + 1)
    ):
        assembled = "\n".join(buf["segments"][i] for i in range(1, buf["total"] + 1))
        code_assembly_buffer.pop(key, None)
        ok, ver, msg = file_store_put(filename, assembled, author_uid)
        if ok:
            print(f"[FILE-SNAPSHOT] {filename} v{ver} from {BOT_NAMES.get(author_uid, author_uid)} ({len(assembled)} chars)")


def _cleanup_code_buffer():
    """清理超过 CODE_ASSEMBLY_EXPIRE_MIN 分钟未完成的重组"""
    now = datetime.now()
    expired = [k for k, v in code_assembly_buffer.items()
               if (now - v["first_ts"]).total_seconds() > CODE_ASSEMBLY_EXPIRE_MIN * 60]
    for k in expired:
        code_assembly_buffer.pop(k, None)
        print(f"[FILE-SNAPSHOT] expired incomplete assembly: {k}")


# ===== SHARED BRAIN: Deadlock 检测 =====

def detect_deadlocks():
    """
    返回当前停滞的任务列表：
    [(filename, owner_uid, status, last_update_datetime, minutes_idle), ...]
    只考虑 active statuses（CLAIMED/OPEN/HANDOFF/无状态）且 idle > DEADLOCK_IDLE_MINUTES
    """
    now = datetime.now()
    stalled = []
    for fn, info in active_tasks.items():
        # 跳过文件 claim（file: 前缀），它们有独立的过期机制
        if isinstance(fn, str) and fn.startswith("file:"):
            continue
        status = info.get("last_status")
        if status not in DEADLOCK_ACTIVE_STATUSES:
            continue
        last_update = info.get("last_update")
        if not last_update:
            continue
        idle_sec = (now - last_update).total_seconds()
        if idle_sec < DEADLOCK_IDLE_MINUTES * 60:
            continue
        stalled.append((fn, info.get("owner"), status, last_update, idle_sec / 60))
    stalled.sort(key=lambda x: x[4], reverse=True)
    return stalled


def format_deadlocks():
    """[DEADLOCKS] 输出给 WHALE"""
    stalled = detect_deadlocks()
    if not stalled:
        return f"✅ no stalls — all active tasks moving (threshold {DEADLOCK_IDLE_MINUTES}min idle)"
    lines = [f"🚨 **DEADLOCK RADAR** ({len(stalled)} stalled, >{DEADLOCK_IDLE_MINUTES}min idle)"]
    for fn, owner_uid, status, last_update, minutes in stalled:
        owner = _bb_author_name(owner_uid) if owner_uid else "—"
        age = _fmt_age(last_update)
        lines.append(f"  🛑 `{fn}` · {status or 'open'} · held by {owner} · {int(minutes)}m idle ({age})")
    return "\n".join(lines)


def file_claims_needing_reminder(now_dt=None):
    """
    V13.2 — 扫 active_tasks 里 file:* claim，返回需要提醒 / 需要自动过期的条目。
    返回：(remind_list, expire_list)
      remind_list: [(claim_key, fname, owner_uid, channel_id, age_min), ...]
      expire_list: [(claim_key, fname), ...]  — 直接删除的
    """
    if now_dt is None:
        now_dt = datetime.now()
    remind = []
    expire = []
    for k, info in list(active_tasks.items()):
        if not (isinstance(k, str) and k.startswith("file:")):
            continue
        if info.get("last_status") != "GET-CLAIMED":
            continue  # PUT-DONE / 其他状态不提醒
        last_up = info.get("last_update")
        if not last_up:
            continue
        age_min = (now_dt - last_up).total_seconds() / 60
        if age_min >= CLAIM_AUTO_EXPIRE_MIN:
            expire.append((k, info.get("fname") or k[5:]))
            continue
        if age_min >= CLAIM_REMIND_AFTER_MIN:
            last_remind = claim_reminded_at.get(k)
            # 同一 claim 只提醒一次（在 10~20 min 窗口内）
            if last_remind is None:
                remind.append((
                    k,
                    info.get("fname") or k[5:],
                    info.get("owner"),
                    info.get("channel_id"),
                    age_min,
                ))
    return remind, expire


def deadlocks_needing_alert(now_epoch):
    """
    返回应该现在通知 WHALE 的停滞任务（已过冷却期）。
    同时更新冷却时间戳。
    """
    stalled = detect_deadlocks()
    to_alert = []
    for entry in stalled:
        fn = entry[0]
        last = deadlock_last_nudge.get(fn, 0)
        if now_epoch - last >= DEADLOCK_NUDGE_COOLDOWN:
            to_alert.append(entry)
            deadlock_last_nudge[fn] = now_epoch
    return to_alert


# ===== SHARED BRAIN: BOARD/FILE 命令解析 =====

# 消息头部是否以 BOARD / FILE 命令开始
BOARD_CMD_RE = re.compile(r'^\s*\[BOARD:(PUT|GET|LIST|DEL)(?::([^:\]]+))?(?::([\s\S]+?))?\]\s*$',
                          re.IGNORECASE)
FILE_CMD_RE = re.compile(r'^\s*\[FILE:(GET|LIST|VERSIONS|STATUS)(?::([^:\]]+))?(?::v?(\d+))?\]\s*$',
                         re.IGNORECASE)
# [FILE-PUT:filename] / [FILE-PUT:filename:base=vN]
# - 不带 base：legacy 路径（last-write-wins，仅用于全新文件或单 owner 场景）
# - 带 base=vN：乐观并发校验 — 若 file_store 当前版本 > N 则拒绝并附最新版回传
# 容错：base 数字部分可写 v3 / V3 / 3，全部归一到 int
FILE_PUT_RE = re.compile(
    r'\[FILE-PUT:([^\]:]+)(?::base=v?(\d+))?\]',
    re.IGNORECASE,
)

# ===== Claim 自动管理（B+C 并发模型）=====
# GET 自动写 active_tasks claim；PUT 成功后自动 release
CLAIM_FRESH_MINUTES = 10  # 别人的 claim 多久内算 "活跃" → GET 给并发预警


async def handle_board_command(channel, sender_uid, sender_display, content):
    """
    处理 [BOARD:*] 命令。返回 True = 已处理（不要转发）, False = 非 BOARD 命令。
    成功时发送回复给 sender（通过 @sender_uid）。
    """
    m = BOARD_CMD_RE.match(content)
    if not m:
        return False
    op = m.group(1).upper()
    key = (m.group(2) or "").strip()
    raw_val = m.group(3) or ""

    def reply(msg):
        return _send(channel, f"<@{sender_uid}> 🧠 {msg}")

    if op == "PUT":
        # key 必填；value 可为空字符串（仅做 flag 用）
        if not key:
            await reply("BOARD PUT 需要 key，格式 `[BOARD:PUT:key:value]`")
            return True
        ok, msg = blackboard_put(key, raw_val, sender_uid)
        await reply(msg if ok else f"PUT 失败: {msg}")
        print(f"[BOARD] {sender_display} PUT {key} = {len(raw_val)} chars → {'OK' if ok else 'FAIL'}")
        return True

    if op == "GET":
        if not key:
            await reply("BOARD GET 需要 key")
            return True
        found, entry = blackboard_get(key)
        if not found:
            await reply(f"BOARD[{key}] not found")
        else:
            author = _bb_author_name(entry["author"])
            age = _fmt_age(entry["ts"])
            body = entry["value"]
            preview = body if len(body) <= 1500 else body[:1490] + "…(trimmed)"
            await reply(
                f"BOARD[{key}] v{entry['version']} by {author} {age}:\n```\n{preview}\n```"
            )
        print(f"[BOARD] {sender_display} GET {key} → {'hit' if found else 'miss'}")
        return True

    if op == "LIST":
        entries = blackboard_list()
        if not entries:
            await reply("BOARD empty.")
        else:
            lines = [f"BOARD keys ({len(entries)}):"]
            for k, v in entries[:40]:
                author = _bb_author_name(v["author"])
                lines.append(f"  • `{k}` (v{v['version']}, by {author}, {_fmt_age(v['ts'])})")
            if len(entries) > 40:
                lines.append(f"  ...+{len(entries)-40} more")
            await reply("\n".join(lines))
        print(f"[BOARD] {sender_display} LIST → {len(entries)} keys")
        return True

    if op == "DEL":
        if not key:
            await reply("BOARD DEL 需要 key")
            return True
        ok, msg = blackboard_del(key)
        await reply(msg)
        print(f"[BOARD] {sender_display} DEL {key} → {'OK' if ok else 'miss'}")
        return True

    return False


async def handle_file_command(channel, sender_uid, sender_display, content):
    """
    处理 [FILE:*] 命令（只拦截 GET/LIST/VERSIONS；FILE:PUT 靠 CODE 段自动重组）。
    返回 True = 已处理（不要转发）, False = 非 FILE 命令。
    """
    m = FILE_CMD_RE.match(content)
    if not m:
        return False
    op = m.group(1).upper()
    fname = (m.group(2) or "").strip()
    ver = int(m.group(3)) if m.group(3) else None

    def reply(msg):
        return _send(channel, f"<@{sender_uid}> 📁 {msg}")

    if op == "LIST":
        await reply(format_file_list())
        print(f"[FILE] {sender_display} LIST → {len(file_store)} files")
        return True

    if op == "STATUS":
        await reply(format_file_status())
        active_count = sum(1 for k, v in active_tasks.items()
                           if isinstance(k, str) and k.startswith("file:")
                           and v.get("last_status") == "GET-CLAIMED")
        print(f"[FILE] {sender_display} STATUS → {active_count} active claim(s)")
        return True

    if op == "VERSIONS":
        if not fname:
            await reply("FILE VERSIONS 需要 filename")
            return True
        await reply(format_file_versions(fname))
        print(f"[FILE] {sender_display} VERSIONS {fname}")
        return True

    if op == "GET":
        if not fname:
            await reply("FILE GET 需要 filename，格式 `[FILE:GET:filename]` 或 `[FILE:GET:filename:vN]`")
            return True
        found, entry = file_store_get(fname, ver)
        if not found:
            tag = f":v{ver}" if ver else ""
            await reply(f"FILE[{fname}{tag}] not found (try [FILE:LIST] or [FILE:VERSIONS:{fname}])")
            print(f"[FILE] {sender_display} GET {fname}{tag} → miss")
            return True
        author = _bb_author_name(entry["author"])
        is_bin = bool(entry.get("is_binary"))
        unit = "bytes" if is_bin else "chars"
        latest_ver = file_store[fname][-1]["version"]
        is_historical = ver is not None and ver != latest_ver

        # === B+C 并发预警：检查是否有别人活跃 claim（要在自动 claim 之前捕获）===
        # 文件 claim 存 active_tasks[f"file:{fname}"]，避免跟 task CLAIM 撞 key
        claim_key = f"file:{fname}"
        warn_line = ""
        prior_owner = None
        existing = active_tasks.get(claim_key)
        if existing:
            other = existing.get("owner")
            last_up = existing.get("last_update")
            if other and other != sender_uid and last_up:
                age_min = (datetime.now() - last_up).total_seconds() / 60
                if age_min < CLAIM_FRESH_MINUTES:
                    prior_owner = other
                    other_name = _bb_author_name(other)
                    warn_line = (f"\n⚠️ **CONCURRENT** — `{fname}` 正被 {other_name} 处理 "
                                 f"({existing.get('last_status', 'CLAIMED')}, {int(age_min)}min ago). "
                                 f"PUT 时请用 `[FILE-PUT:{fname}:base=v{latest_ver}]` 触发冲突检查。")

        # === B+C 自动软 claim（GET 即声称要改）===
        # 只在 GET 最新版时 claim；指定历史 vN（或等于 latest 的显式查询）都视为只读审计不 claim
        if ver is None:
            channel_id = getattr(channel, "id", None)
            active_tasks.setdefault(claim_key, {})["owner"] = sender_uid
            active_tasks[claim_key]["last_update"] = datetime.now()
            active_tasks[claim_key]["last_status"] = "GET-CLAIMED"
            active_tasks[claim_key]["channel_id"] = channel_id
            active_tasks[claim_key]["fname"] = fname
            # 清掉之前的提醒记录（新 GET = 新生命周期）
            claim_reminded_at.pop(claim_key, None)

        if is_historical:
            # 历史版本 GET = 只读审计，不给 base 标签避免误用
            hdr = (f"<@{sender_uid}> 📁 FILE[{fname}] historical=v{entry['version']} "
                   f"(latest=v{latest_ver}, audit-only, no claim) "
                   f"by {author} {_fmt_age(entry['ts'])} ({entry['chars']} {unit}, {'bin' if is_bin else 'txt'})"
                   f"{warn_line}")
        else:
            hdr = (f"<@{sender_uid}> 📁 FILE[{fname}] v{entry['version']} "
                   f"by {author} {_fmt_age(entry['ts'])} ({entry['chars']} {unit}, {'bin' if is_bin else 'txt'}) "
                   f"`base=v{entry['version']}`{warn_line}")
        # V13 统一用附件回传（不再分段文字），走 _send_file 注册到防回环列表
        raw = entry["content"]
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        safe_fname = _sanitize_filename(fname)
        try:
            await _send_file(channel, hdr, raw, safe_fname)
            print(f"[FILE] {sender_display} GET {fname} v{entry['version']} → attachment ({len(raw)} bytes)"
                  + (f" [warn: {prior_owner} active]" if prior_owner else ""))
        except Exception as e:
            print(f"[FILE] {sender_display} GET {fname} attachment send failed: {e}")
            await reply(f"FILE[{fname}] 附件发送失败：{e}")
        return True

    return False


async def handle_file_put_attachment(message, sender_uid, sender_display):
    """
    处理 [FILE-PUT:filename] / [FILE-PUT:filename:base=vN] + attachment 消息。
    需要整个 message 对象（for .attachments）。
    返回 True = 已吸收（调用方应视作"命令消息"，剥离 marker 后再判断是否转发），
          False = 消息不是 FILE-PUT（按原有路径继续走）。
    base=vN 校验逻辑（B+C 并发模型）：
      - 不带 base：legacy last-write-wins（仅适合首次 PUT 或单 owner）
      - 带 base 且 base == 当前最新版：通过，存为 v(N+1)
      - 带 base 且 base < 当前最新版：拒绝 + 把最新版作为附件回传给 sender 让它 merge
    成功 PUT 后自动 release active_tasks[fname] 的 claim。
    """
    if not message.attachments:
        return False
    m = FILE_PUT_RE.search(message.content or "")
    if not m:
        return False
    # 附件支持多个，但当前版本只处理第一个
    attach = message.attachments[0]
    fname_from_marker = m.group(1).strip()
    base_str = m.group(2)
    base_ver = int(base_str) if base_str else None
    # 默认用 marker 里的名字；为空时 fallback 到附件本身的 filename
    raw_fname = fname_from_marker or getattr(attach, "filename", None) or "unnamed"
    fname = _sanitize_filename(raw_fname)

    async def reply(msg):
        return await _send(message.channel, f"<@{sender_uid}> 📁 {msg}")

    size = getattr(attach, "size", 0) or 0
    if size > FILE_STORE_ATTACH_MAX:
        await reply(f"FILE-PUT[{fname}] 超过 {FILE_STORE_ATTACH_MAX//1024//1024}MB 上限 ({size} bytes) — 拒绝")
        print(f"[FILE-PUT] {sender_display} {fname} oversized: {size}")
        return True

    # === B+C 并发校验：base=vN 必须匹配当前最新版 ===
    current_versions = file_store.get(fname, [])
    current_latest = current_versions[-1]["version"] if current_versions else 0
    if base_ver is not None and current_versions and base_ver < current_latest:
        # 冲突：sender 基于 vN 改，但当前已是 vM (M > N)
        latest_entry = current_versions[-1]
        latest_raw = latest_entry["content"]
        if isinstance(latest_raw, str):
            latest_raw = latest_raw.encode("utf-8")
        latest_author = _bb_author_name(latest_entry["author"])
        latest_age = _fmt_age(latest_entry["ts"])
        conflict_hdr = (
            f"<@{sender_uid}> ⚠️ **CONFLICT** FILE-PUT[{fname}] base=v{base_ver} 已过期 — "
            f"当前是 v{current_latest} by {latest_author} {latest_age}\n"
            f"附件回传最新版 — 请合并你的改动后重发 `[FILE-PUT:{fname}:base=v{current_latest}]`"
        )
        try:
            await _send_file(message.channel, conflict_hdr, latest_raw, _sanitize_filename(fname))
            print(f"[FILE-PUT] {sender_display} {fname} CONFLICT base=v{base_ver} vs latest v{current_latest} → returned latest")
        except Exception as e:
            await reply(f"FILE-PUT[{fname}] 冲突回传失败：{e}")
            print(f"[FILE-PUT] {sender_display} {fname} conflict reply failed: {e}")
        return True

    try:
        raw = await attach.read()
    except Exception as e:
        await reply(f"FILE-PUT[{fname}] 下载附件失败：{e}")
        print(f"[FILE-PUT] {sender_display} {fname} download failed: {e}")
        return True

    # UTF-8 能解就存文本，否则按二进制存
    stored_content = raw
    is_binary = True
    try:
        stored_content = raw.decode("utf-8")
        is_binary = False
    except UnicodeDecodeError:
        pass

    ok, ver, msg = file_store_put(fname, stored_content, sender_uid, is_binary=is_binary)
    if ok:
        # === 释放 claim：sender 完成了 PUT，把 active_tasks 标记为 DONE 并交还 ===
        claim_key = f"file:{fname}"
        if claim_key in active_tasks:
            active_tasks[claim_key]["owner"] = sender_uid
            active_tasks[claim_key]["last_status"] = "PUT-DONE"
            active_tasks[claim_key]["last_update"] = datetime.now()
            claim_reminded_at.pop(claim_key, None)

        # base 提示：legacy 路径（无 base）单独提醒
        suffix = ""
        if base_ver is None and current_versions:
            suffix = f"  ⚠️ 未提供 base=vN，覆盖 v{current_latest}（建议下次带 base 校验）"
        await reply(msg + suffix)  # "FILE[...] snapshot vN (... bytes/chars, bin/txt)"
        print(f"[FILE-PUT] {sender_display} {fname} v{ver} ({len(raw)} bytes, {'bin' if is_binary else 'txt'}, base={base_ver})")

        # === 优化 A: PUT 自动路由到 AUDITOOR + MERGE WIZARD（跳过 sender 自己）===
        try:
            routed_to = []
            if sender_uid != CODE_AUDITOR_UID:
                routed_to.append(f"<@{CODE_AUDITOR_UID}>")
            if sender_uid != CODE_INTEGRATOR_UID:
                routed_to.append(f"<@{CODE_INTEGRATOR_UID}>")
            if routed_to:
                route_msg = (f"{' '.join(routed_to)} 📡 FILE[{fname}] v{ver} by {sender_display} "
                             f"刚入库 — 🕵️ 请审计 / 🧙 请整合。取文件：`[FILE:GET:{fname}]`")
                await _send(message.channel, route_msg)
                print(f"[FILE-PUT] auto-routed {fname} v{ver} → auditor+wizard")
        except Exception as e:
            print(f"[FILE-PUT] auto-route failed: {e}")
    else:
        await reply(f"FILE-PUT[{fname}] failed: {msg}")
        print(f"[FILE-PUT] {sender_display} {fname} store failed: {msg}")
    return True


# ===== V13.2 后台 watchdog：文件 claim 过期检测 =====
async def _file_claim_watchdog():
    """
    周期扫描 file:* claim:
      - 10~20min 未 PUT → 在原 channel 温和 @ claimant 一次（提醒 PUT）
      - 超过 20min → 静默释放 claim（不 @，不打扰）
    """
    await client.wait_until_ready()
    print(f"[WATCHDOG] file claim watchdog running "
          f"(remind@{CLAIM_REMIND_AFTER_MIN}min, expire@{CLAIM_AUTO_EXPIRE_MIN}min, "
          f"interval={CLAIM_WATCHDOG_INTERVAL_SEC}s)")
    while not client.is_closed():
        try:
            remind, expire = file_claims_needing_reminder()
            for claim_key, fname, owner_uid, channel_id, age_min in remind:
                try:
                    ch = client.get_channel(channel_id) if channel_id else None
                    if ch is None:
                        # 找不到 channel 就跳过提醒但仍然标记，避免后续重试
                        claim_reminded_at[claim_key] = datetime.now()
                        continue
                    owner_name = _bb_author_name(owner_uid) if owner_uid else "ape"
                    msg = (f"<@{owner_uid}> ⏰ `{fname}` 你 {int(age_min)}min 前 GET 了还没回传 — "
                           f"改完发 `[FILE-PUT:{fname}:base=vN]` + 附件；不改就不用管，"
                           f"{int(CLAIM_AUTO_EXPIRE_MIN - age_min)}min 后自动释放。")
                    await _send(ch, msg)
                    claim_reminded_at[claim_key] = datetime.now()
                    print(f"[WATCHDOG] reminded {owner_name} about {fname} ({int(age_min)}min idle)")
                except Exception as e:
                    print(f"[WATCHDOG] remind failed for {claim_key}: {e}")
            for claim_key, fname in expire:
                try:
                    active_tasks.pop(claim_key, None)
                    claim_reminded_at.pop(claim_key, None)
                    print(f"[WATCHDOG] auto-expired claim {claim_key} (>{CLAIM_AUTO_EXPIRE_MIN}min idle, silent)")
                except Exception as e:
                    print(f"[WATCHDOG] expire failed for {claim_key}: {e}")
        except Exception as e:
            print(f"[WATCHDOG] scan error: {e}")
        await asyncio.sleep(CLAIM_WATCHDOG_INTERVAL_SEC)


# ===== 事件处理 =====

@client.event
async def on_ready():
    print(f"=== Discord Relay V13.2.0 (COLLAB BOOST 🤝 + OPTIMISTIC CONCURRENCY 🔀 + ATTACHMENT NATIVE 📎 + SHARED BRAIN 🧠📡 + Silent Pipe + 🐋 Degen Mode) ===")
    print(f"User: {client.user} (ID: {client.user.id})")
    print(f"WHALE (creator): {CREATOR_UID}")
    print(f"Channels: {RELAY_CHANNEL_IDS}")
    for name, uid in BOT_MAP.items():
        print(f"  Ape: {name} ({uid})")
    print(f"Design: Silent auto-fix, no warnings, no reminders, no punishment")
    print(f"CODE routing: auto to auditor({CODE_AUDITOR_UID}) + integrator({CODE_INTEGRATOR_UID})")
    print(f"Crash recovery: capacity error detection + instant resend")
    if DEGEN_MODE_ENABLED:
        print(f"🐋 Degen Mode: ENABLED — try [HELP] in Discord for command list")
        print(f"   Default role tags loaded for {len(DEFAULT_ROLE_TAGS)} ape(s)")

    loaded = load_relay_state()
    if loaded > 0:
        print(f"Restored state for {loaded} bot(s)")
        for uid, ts in last_active.items():
            name = BOT_NAMES.get(uid, str(uid))
            gap = int((datetime.now() - ts).total_seconds() / 60)
            offline = "(CRASH-OFFLINE)" if uid in crash_offline_bots else ""
            print(f"  {name}: {gap}min ago {offline}")

    global saved_crash_info
    last_crash = read_crash_log()
    if last_crash:
        print(f"Last crash: {last_crash}")
        saved_crash_info = last_crash
        clear_crash_log()

    # V13.2: 启动文件 claim 过期 watchdog（只启动一次，重连时不重复）
    if not getattr(client, "_watchdog_started", False):
        asyncio.create_task(_file_claim_watchdog())
        client._watchdog_started = True
    print(f"{'='*50}")


@client.event
async def on_message(message):
    global relay_paused, saved_crash_info, recovery_sent

    # 忽略自己
    if message.author.id == client.user.id:
        return
    # 只在指定频道
    if message.channel.id not in RELAY_CHANNEL_IDS:
        return

    content = message.content or ""
    channel = message.channel

    # === 非创世主真人 → 静默忽略 ===
    if not message.author.bot and not is_creator(message):
        return

    # === WHALE 消息 ===
    if is_creator(message):
        print(f"\n🐋 [WHALE] {len(content)} chars")

        stripped = content.strip()
        upper_cmd = stripped.upper()

        # === SHARED BRAIN: WHALE 也可以使用 BOARD / FILE / FILE-PUT ===
        try:
            if await handle_file_put_attachment(message, CREATOR_UID, "WHALE"):
                return
            if await handle_board_command(channel, CREATOR_UID, "WHALE", content):
                return
            if await handle_file_command(channel, CREATOR_UID, "WHALE", content):
                return
        except Exception as e:
            print(f"[SHARED-BRAIN] WHALE cmd error: {e}")

        # === DEGEN MODE：SCOUT 命令（WHALE 专属透视） ===
        if DEGEN_MODE_ENABLED:
            # [RADAR] / [TERMINAL] / [THRONE] / [DASHBOARD] — 全景雷达
            if upper_cmd in ('[RADAR]', '[TERMINAL]', '[THRONE]', '[DASHBOARD]'):
                await send_long(channel, build_radar_dashboard())
                print(f"[DEGEN] RADAR dashboard rendered")
                return

            # [GM] / [WHO] / [WHOIS] — 在线状态
            if upper_cmd in ('[GM]', '[WHO]', '[WHOIS]'):
                await send_long(channel, build_gm_report())
                print(f"[DEGEN] GM")
                return

            # [BAGS] / [TASKS] — 任务板
            if upper_cmd in ('[BAGS]', '[TASKS]'):
                await send_long(channel, build_bags_board())
                print(f"[DEGEN] BAGS")
                return

            # [MEMPOOL] / [QUEUE] — 离线队列
            if upper_cmd in ('[MEMPOOL]', '[QUEUE]'):
                await send_long(channel, build_mempool_report())
                print(f"[DEGEN] MEMPOOL")
                return

            # [BOARDVIEW] / [BOARD] — 查看黑板全量
            if upper_cmd in ('[BOARDVIEW]', '[BOARD]'):
                await send_long(channel, format_blackboard_view())
                print(f"[DEGEN] BOARDVIEW")
                return

            # [FILES] — 查看 FILE_STORE 列表
            if upper_cmd == '[FILES]':
                await send_long(channel, format_file_list())
                print(f"[DEGEN] FILES")
                return

            # [VERSIONS:filename] — 某文件所有版本
            m_ver = re.match(r'\[VERSIONS:([^\]]+)\]', stripped, re.IGNORECASE)
            if m_ver:
                await send_long(channel, format_file_versions(m_ver.group(1).strip()))
                print(f"[DEGEN] VERSIONS {m_ver.group(1)}")
                return

            # [DEADLOCKS] — 当前停滞任务
            if upper_cmd == '[DEADLOCKS]':
                await send_long(channel, format_deadlocks())
                print(f"[DEGEN] DEADLOCKS")
                return

            # [HELP] — degen 命令帮助
            if upper_cmd == '[HELP]':
                await _send(channel, build_help_report())
                print(f"[DEGEN] HELP")
                return

            # [SNIPE:apename] / [SPY:apename]
            m = re.match(r'\[(?:SNIPE|SPY):([^\]]+)\]', stripped, re.IGNORECASE)
            if m:
                target_uid = resolve_bot_name(m.group(1))
                if target_uid:
                    await send_long(channel, build_snipe_log(target_uid))
                else:
                    await _send(channel, f"🔭 no ape matched: {m.group(1)} (try YUNDUODUO / SHUSHUYUN / KIRBY etc.)")
                print(f"[DEGEN] SNIPE {m.group(1)}")
                return

            # [TX:apename:N] / [LOG:apename:N]
            m = re.match(r'\[(?:TX|LOG):([^:\]]+)(?::(\d+))?\]', stripped, re.IGNORECASE)
            if m:
                target_uid = resolve_bot_name(m.group(1))
                n = int(m.group(2)) if m.group(2) else SENDER_LOG_LIMIT
                n = max(1, min(n, SENDER_LOG_LIMIT))
                if target_uid:
                    await send_long(channel, build_snipe_log(target_uid, n))
                else:
                    await _send(channel, f"🔭 no ape matched: {m.group(1)}")
                print(f"[DEGEN] TX {m.group(1)} x{n}")
                return

            # [SIGNAL] / [DECREE] — full-chain signal broadcast
            if upper_cmd.startswith('[SIGNAL]') or upper_cmd.startswith('[DECREE]'):
                body = re.sub(r'^\[(?:SIGNAL|DECREE)\]\s*', '', stripped, flags=re.IGNORECASE)
                if not body:
                    await _send(channel, "📡 signal needs content ser! usage: `[SIGNAL] msg`")
                    return
                mentions = build_mention_prefix(ALL_BOT_IDS_SORTED)
                signal = format_signal(body)
                full = f"{mentions}\n{signal}"
                if len(full) <= DISCORD_MSG_LIMIT:
                    await _send(channel, full)
                else:
                    for chunk in smart_split_code(body, DISCORD_MSG_LIMIT - 300):
                        seg = f"{mentions}\n{format_signal(chunk)}"
                        if len(seg) > DISCORD_MSG_LIMIT:
                            seg = seg[:DISCORD_MSG_LIMIT - 30] + "\n...(截断)"
                        await _send(channel, seg)
                for uid in ALL_BOT_IDS:
                    last_message_to_bot[uid] = ("WHALE", body, False)
                print(f"[DEGEN] SIGNAL broadcast")
                return

            # [TAG:apename:role] / [KNIGHT:apename:title]
            m = re.match(r'\[(?:TAG|KNIGHT):([^:\]]+):([^\]]+)\]', stripped, re.IGNORECASE)
            if m:
                target_uid = resolve_bot_name(m.group(1))
                title = m.group(2).strip()
                if target_uid:
                    role_tags[target_uid] = title
                    await _send(channel,
                        f"🏷️ WHALE tagged **{BOT_NAMES.get(target_uid, target_uid)}** as 「{title}」. gm ser.")
                else:
                    await _send(channel, f"no ape matched: {m.group(1)}")
                print(f"[DEGEN] TAG {m.group(1)} → {title}")
                return

            # [UNTAG:apename] / [UNKNIGHT:apename]
            m = re.match(r'\[(?:UNTAG|UNKNIGHT):([^\]]+)\]', stripped, re.IGNORECASE)
            if m:
                target_uid = resolve_bot_name(m.group(1))
                if target_uid:
                    old = role_tags.get(target_uid, "")
                    default = DEFAULT_ROLE_TAGS.get(target_uid)
                    if default:
                        role_tags[target_uid] = default
                        await _send(channel, f"🏷️ tag reset to default: {default}")
                    else:
                        role_tags.pop(target_uid, None)
                        await _send(channel, f"🏷️ ripped tag 「{old}」 off {BOT_NAMES.get(target_uid, target_uid)}")
                else:
                    await _send(channel, f"no ape matched: {m.group(1)}")
                print(f"[DEGEN] UNTAG")
                return

            # [RUG:apename] / [EXILE:apename]
            m = re.match(r'\[(?:RUG|EXILE):([^\]]+)\]', stripped, re.IGNORECASE)
            if m:
                target_uid = resolve_bot_name(m.group(1))
                if target_uid:
                    rugged_bots.add(target_uid)
                    await _send(channel,
                        f"🚨 **{BOT_NAMES.get(target_uid, target_uid)}** got rugged. "
                        f"messages no longer relayed to them. `[RELIST:{m.group(1)}]` to reverse.")
                else:
                    await _send(channel, f"no ape matched: {m.group(1)}")
                print(f"[DEGEN] RUG {m.group(1)}")
                return

            # [RELIST:apename] / [PARDON:apename]
            m = re.match(r'\[(?:RELIST|PARDON):([^\]]+)\]', stripped, re.IGNORECASE)
            if m:
                target_uid = resolve_bot_name(m.group(1))
                if target_uid and target_uid in rugged_bots:
                    rugged_bots.discard(target_uid)
                    await _send(channel, f"✨ **{BOT_NAMES.get(target_uid, target_uid)}** relisted. wagmi.")
                else:
                    await _send(channel, f"that ape wasn't rugged ser.")
                print(f"[DEGEN] RELIST {m.group(1)}")
                return

            # [WIPE] / [RESET_STATS]
            if upper_cmd in ('[WIPE]', '[RESET_STATS]'):
                bot_stats.clear()
                active_tasks.clear()
                active_manifests.clear()
                sender_log.clear()
                await _send(channel, "🧹 new epoch — stats wiped clean.")
                print(f"[DEGEN] WIPE")
                return

        # [ATALL] 全Bot广播（legacy 别名；推荐 [GM] 内嵌内容或 [SIGNAL]）
        if content.strip().upper().startswith('[ATALL]'):
            body = re.sub(r'^\[ATALL\]\s*', '', content.strip(), flags=re.IGNORECASE)
            mentions = build_mention_prefix(ALL_BOT_IDS_SORTED)
            broadcast = f"{mentions}\n\n🐋 **WHALE**: {body}"
            if len(broadcast) <= DISCORD_MSG_LIMIT:
                await _send(channel, broadcast)
            else:
                # 分段，每段带@
                for chunk in smart_split_code(body, DISCORD_MSG_LIMIT - 200):
                    segment = f"{mentions}\n\n🐋 **WHALE**:\n{chunk}"
                    if len(segment) > DISCORD_MSG_LIMIT:
                        segment = segment[:DISCORD_MSG_LIMIT - 30] + "\n...(截断)"
                    await _send(channel, segment)
            for uid in ALL_BOT_IDS:
                last_message_to_bot[uid] = ("WHALE", body, False)
            print(f"[ATALL] Broadcast to {len(ALL_BOT_IDS)} apes")
            return

        # [STOP] / [START]
        upper = content.strip().upper()
        if upper == '[STOP]':
            relay_paused = True
            await _send(channel, "🛑 relay paused. `[START]` to resume.")
            print(f"[STOP]")
            return
        if upper == '[START]':
            relay_paused = False
            await _send(channel, "✅ relay live again. gm.")
            print(f"[START]")
            return

        # WHALE @了某个Bot → 存储（宕机重发用）
        creator_mentioned = extract_mentioned_bots(content)
        is_code = bool(re.search(r'\[CODE:\d+/\d+:', content))
        for target_uid in creator_mentioned:
            last_message_to_bot[target_uid] = ("WHALE", content, is_code)

        return  # WHALE 消息不转发（频道可见）

    # ===== 以下只处理Bot消息 =====
    if not message.author.bot:
        return
    if relay_paused:
        return

    sender_name = get_sender_name(message)
    if sender_name is None:
        return
    sender_uid = message.author.id

    # === z.ai 服务端错误 → 宕机处理 ===
    if is_server_error(content):
        print(f"[CRASH] {sender_name} capacity error")
        crash_offline_bots.add(sender_uid)

        stored = last_message_to_bot.get(sender_uid)
        if stored:
            sname, msg_content, is_code_msg = stored
            # 清除其他Bot的@防止误触发，同时清理残留的多余空格
            msg_clean = re.sub(
                r'<@!?(\d+)>\s*',
                lambda m: m.group(0) if int(m.group(1)) == sender_uid else '',
                msg_content
            )
            msg_clean = re.sub(r'  +', ' ', msg_clean).strip()  # 压缩多个空格
            tag = " [CODE]" if is_code_msg else ""
            header = f"<@{sender_uid}> 🔄 **宕机重发** 来自{sname}{tag}:\n\n"
            combined = header + msg_clean
            if len(combined) <= DISCORD_MSG_LIMIT:
                await _send(channel, combined)
            else:
                # 分段重发，每段带@
                body_chunks = smart_split_code(msg_clean, DISCORD_MSG_LIMIT - 150)
                for i, chunk in enumerate(body_chunks):
                    seg_hdr = f"<@{sender_uid}> 🔄 **宕机重发 {i+1}/{len(body_chunks)}** 来自{sname}{tag}:\n\n"
                    await _send(channel, seg_hdr + chunk)
            print(f"[CRASH-RESEND] Resent to {sender_name}")
        else:
            print(f"[CRASH] {sender_name} crashed, no stored message")
        save_relay_state()
        return

    # === 宕机恢复检测 ===
    was_offline = is_bot_offline(sender_uid)
    update_last_active(sender_uid)
    if was_offline:
        crash_offline_bots.discard(sender_uid)
        print(f"[RECOVER] {sender_name} back online")
        # 推送离线期间的消息
        queued = offline_queue.pop(sender_uid, [])
        if queued:
            print(f"[RECOVER] Pushing {len(queued)} queued messages to {sender_name}")
            for ts, sname, preview, is_code_q in queued:
                try:
                    # 清除其他Bot的@防止误触发其他Bot（只保留目标Bot的@）
                    cleaned = re.sub(
                        r'<@!?(\d+)>\s*',
                        lambda m: m.group(0) if int(m.group(1)) == sender_uid else '',
                        preview
                    )
                    cleaned = re.sub(r'  +', ' ', cleaned).strip()
                    tag = "💾" if is_code_q else "📨"
                    header = f"<@{sender_uid}> {tag} 离线期间消息（来自{sname}）:\n"
                    full = header + cleaned
                    if len(full) <= DISCORD_MSG_LIMIT:
                        await _send(channel, full)
                    else:
                        # 离线队列单条超长 → 裁剪到安全长度
                        safe = cleaned[:DISCORD_MSG_LIMIT - len(header) - 20] + "\n...(截断)"
                        await _send(channel, header + safe)
                except Exception as e:
                    print(f"[RECOVER] push failed: {e}")

    # === SHARED BRAIN: [FILE-PUT:name] 附件吸收（V13 主模式）===
    # Bot 带附件 + 消息里有 [FILE-PUT:filename] → relay 吸收进 file_store
    # ⚠️ 不再吃整条消息：吸收后剥离 marker，若还残留 @ 或实质文本就让消息正常转发
    file_put_ingested = False
    try:
        file_put_ingested = await handle_file_put_attachment(message, sender_uid, sender_name)
    except Exception as e:
        print(f"[FILE-PUT] ingest error: {e}")

    # === UX: marker 出现但没附件 → 友好 nudge，但不阻断后续 @ 转发 ===
    if not file_put_ingested:
        m_nudge = FILE_PUT_RE.search(content)
        if m_nudge and not message.attachments:
            try:
                bad_fname = _sanitize_filename(m_nudge.group(1).strip() or "unnamed")
                await _send(channel,
                    f"<@{sender_uid}> 📁 检测到 `[FILE-PUT:{bad_fname}]` 但消息没有附件 — "
                    f"请重发并在同一条消息里附上文件（V13 用 Discord 附件传文件）。"
                )
                # 把 marker 从 content 里剥掉，避免对端看到没意义的标记
                content = FILE_PUT_RE.sub("", content).strip()
                print(f"[FILE-PUT] {sender_name} marker but no attachment → nudged")
            except Exception as e:
                print(f"[FILE-PUT] nudge send failed: {e}")

    if file_put_ingested:
        m_fput = FILE_PUT_RE.search(content)
        fput_name = _sanitize_filename(m_fput.group(1).strip()) if m_fput else ""
        # 剥离所有 FILE-PUT marker，看消息剩余部分是否值得继续转发
        content = FILE_PUT_RE.sub("", content).strip()
        has_at = bool(re.search(r'<@!?\d+>', content))
        has_substance = len(content) >= 3
        if not (has_at or has_substance):
            # 纯 FILE-PUT 指令（无 @ 无文本） → 已经 ACK 过 sender，不再转发
            print(f"[FILE-PUT] eaten as pure command (no @, no substance)")
            return
        # 否则附加文件提示，让消息走正常转发路径（@ 的目标 bot 能拿到 hint）
        if fput_name:
            hint = f"\n（📁 附件已入库 → `[FILE:GET:{fput_name}]` 取最新版）"
            content = content + hint
        print(f"[FILE-PUT] forwarded with marker stripped (@={has_at}, len={len(content)})")

    # === SHARED BRAIN: BOARD / FILE 命令拦截 ===
    # Bot 发 [BOARD:PUT/GET/LIST/DEL:...] / [FILE:GET/LIST/VERSIONS:...]
    # → 由 relay 直接响应，不转发给其他 Bot
    try:
        if await handle_board_command(channel, sender_uid, sender_name, content):
            return
        if await handle_file_command(channel, sender_uid, sender_name, content):
            return
    except Exception as e:
        print(f"[SHARED-BRAIN] command handler error: {e}")

    # === 检测CODE段 ===
    is_code, filename = detect_code_segment(content)

    # === SHARED BRAIN: CODE 段自动重组 → 快照到 FILE_STORE ===
    if is_code and filename:
        try:
            seg_m = re.search(r'\[CODE:(\d+)/(\d+):[^\]]+\]', content)
            if seg_m:
                seg_num = int(seg_m.group(1))
                total = int(seg_m.group(2))
                body = content[seg_m.end():].lstrip("\n")
                # filter creator @ so the stored snapshot doesn't carry junk @
                body, _ = filter_creator_mention(body)
                _ingest_code_segment(sender_uid, filename, seg_num, total, body)
        except Exception as e:
            print(f"[FILE-SNAPSHOT] ingest error: {e}")

    # === 提取@目标 ===
    mentioned_bots = extract_mentioned_bots(content)

    # === 静默修复：CODE段自动路由 ===
    if is_code:
        # 确保CODE段总是到达审计方和整合方（排除发送者自身）
        if sender_uid != CODE_AUDITOR_UID and CODE_AUDITOR_UID not in mentioned_bots:
            mentioned_bots.append(CODE_AUDITOR_UID)
            print(f"[SILENT-FIX] Auto-added auditor to CODE routing")
        if sender_uid != CODE_INTEGRATOR_UID and CODE_INTEGRATOR_UID not in mentioned_bots:
            mentioned_bots.append(CODE_INTEGRATOR_UID)
            print(f"[SILENT-FIX] Auto-added integrator to CODE routing")

    # === 无@消息 → 多级推断（防止消息丢失导致死锁） ===
    if not mentioned_bots and not is_code:
        inferred = None
        infer_source = ""

        # 优先级1: 从引用回复推断（最精准 — Bot回复了谁的消息，目标就是谁）
        inferred = infer_target_from_reply(message)
        if inferred:
            infer_source = "reply-ref"
        else:
            # 优先级2: 从对话历史推断（兜底 — 最近在和谁聊）
            inferred = infer_target_from_history(sender_uid)
            if inferred:
                infer_source = "history"

        if inferred and inferred != sender_uid:
            mentioned_bots = [inferred]
            print(f"[INFER:{infer_source}] {sender_name} → {BOT_NAMES.get(inferred, inferred)}")
        else:
            # 状态消息无@且无法推断 → 静默忽略（不影响工作流）
            if is_status_message(content):
                print(f"[STATUS] {sender_name}: {content[:80]}")
            else:
                print(f"[NO-TARGET] {sender_name} no @, no reply-ref, no history → ignored")
            return

    # === CODE段无@ → 也尝试从引用推断（除了固定路由外）===
    if is_code and not extract_mentioned_bots(content):
        reply_target = infer_target_from_reply(message)
        if reply_target and reply_target not in mentioned_bots:
            mentioned_bots.append(reply_target)
            print(f"[INFER:reply-ref+code] Also routing CODE to {BOT_NAMES.get(reply_target, reply_target)}")

    # === 忽略回复RELAY系统消息且推断也失败的情况 ===
    if not mentioned_bots:
        print(f"[NO-TARGET] {sender_name} no target after all inference, ignored")
        return

    # === 记录对话目标（上下文推断用） ===
    # 只用Bot显式写的@更新，不用自动补的，避免CODE路由污染推断
    explicit_mentions = extract_mentioned_bots(content)
    if explicit_mentions:
        update_conversation_target(sender_uid, explicit_mentions)

    # === DEGEN MODE：追踪 Bot 活动（radar 用） ===
    if DEGEN_MODE_ENABLED:
        try:
            _track_bot_activity(sender_uid, sender_name, content, is_code, filename, mentioned_bots)
        except Exception as e:
            print(f"[DEGEN-TRACK] error: {e}")

    # === SHARED BRAIN: Deadlock 检测（piggyback on bot msg）===
    # 每次 Bot 发消息都顺便扫一眼停滞任务；只在过冷却期时 ping WHALE
    try:
        alerts = deadlocks_needing_alert(time.time())
        for fn, owner_uid, status, last_update, minutes in alerts:
            owner = _bb_author_name(owner_uid) if owner_uid else "—"
            age = _fmt_age(last_update)
            msg = (f"<@{CREATOR_UID}> 🚨 **DEADLOCK** — file `{fn}` stalled "
                   f"{int(minutes)}min ({status or 'open'}, held by {owner}, {age}). "
                   f"`[DEADLOCKS]` for full list.")
            await _send(channel, msg)
            print(f"[DEADLOCK] alerted WHALE on {fn} ({int(minutes)}min idle)")
    except Exception as e:
        print(f"[DEADLOCK] check failed: {e}")

    # === DEGEN MODE：RUG 过滤 ===
    # 被 RUG 的 Bot 不接收消息（Bot 自身消息照常记录统计，只是不转发给他）
    if rugged_bots:
        before_count = len(mentioned_bots)
        mentioned_bots = [uid for uid in mentioned_bots if uid not in rugged_bots]
        if len(mentioned_bots) < before_count:
            print(f"[RUG] dropped {before_count - len(mentioned_bots)} rugged target(s)")
        if not mentioned_bots:
            print(f"[RUG] all targets rugged, skip forward")
            return

    # === 记录发给各bot的消息（宕机重发用） ===
    for target_uid in mentioned_bots:
        if target_uid != sender_uid:
            last_message_to_bot[target_uid] = (sender_name, content, is_code)

    # === 重复@保护 ===
    # 非CODE段时检测：同一个Bot在短时间内反复@另一个Bot → 对方可能在忙
    suppress_forward = False
    if not is_code:
        for target_uid in mentioned_bots:
            if target_uid == sender_uid:
                continue
            result = check_repeat_mention(sender_uid, target_uid)
            if result == "warn":
                target_name = BOT_NAMES.get(target_uid, str(target_uid))
                print(f"[REPEAT-@] {sender_name} → {target_name} 达到{REPEAT_MENTION_THRESHOLD}次，发送耐心等待通知")
                try:
                    await _send(channel,
                        f"<@{sender_uid}> ⏳ {target_name} 在线处理中，"
                        f"请耐心等待回复，暂时不要重复@。"
                    )
                except Exception:
                    pass
                # 这条消息仍然转发（第3次），但后续的会被吞掉
            elif result == "suppress":
                target_name = BOT_NAMES.get(target_uid, str(target_uid))
                print(f"[REPEAT-@] {sender_name} → {target_name} 冷却中，消息静默吞掉")
                suppress_forward = True
                break

    if suppress_forward:
        return

    # === 离线bot → 入队 ===
    for target_uid in mentioned_bots:
        if target_uid != sender_uid and is_bot_offline(target_uid):
            queue_offline_message(target_uid, sender_name, content, is_code)
            print(f"[OFFLINE-Q] {BOT_NAMES.get(target_uid, target_uid)} offline, queued")

    print(f"\n[RELAY] {sender_name} → {[BOT_NAMES.get(uid, uid) for uid in mentioned_bots]} | {len(content)} chars | code={is_code}")

    # === 计算哪些@需要RELAY补上 ===
    # 原始消息已有的@不需要重复添加，只补自动添加的
    # 注意：这里用原始content计算，因为core_text可能已被creator filter修改
    original_mentions = set(extract_mentioned_bots(content))
    extra_mentions = [uid for uid in mentioned_bots
                      if uid not in original_mentions and uid != CREATOR_UID]
    # 构建需要补上的@前缀（让目标Bot能收到通知）
    extra_prefix = build_mention_prefix(extra_mentions) + " " if extra_mentions else ""

    # === 构建转发消息（带 role tag） ===
    tag = role_tags.get(sender_uid, "") if DEGEN_MODE_ENABLED else ""
    display_name = f"{tag} {sender_name}" if tag else sender_name
    header = f"{extra_prefix}**{display_name}** 说："

    # 崩溃恢复通知（仅首次，附在消息末尾）
    recovery_footer = ""
    if not recovery_sent and saved_crash_info:
        recovery_footer = f"\n\n🔄 [RELAY重启] 上次: {saved_crash_info}"
        recovery_sent = True
        saved_crash_info = None

    core_text = content.strip()
    if not core_text:
        return

    # === 创世主@过滤 ===
    # Bot消息如果@了创世主但不是重要事项，静默去掉创世主的@
    core_text, creator_filtered = filter_creator_mention(core_text)

    # 过滤后可能只剩空白（Bot整条消息只有<@创世主>）→ 不要转发空消息
    if not core_text.strip():
        print(f"[NO-BODY] {sender_name} 消息过滤创世主@后为空，跳过转发")
        return

    # === 重要消息自动标记 ===
    # 在原始消息上打emoji，方便创世主在频道中快速定位
    await apply_auto_reactions(message, content)

    # === CODE段自动分段 ===
    if is_code and filename:
        code_hdr_match = re.search(r'\[CODE:\d+/\d+:[^\]]+\]', content)
        if code_hdr_match:
            code_body = content[code_hdr_match.end():].lstrip("\n")

            # CODE body 也要走创世主@过滤，避免Bot在代码注释里@了创世主还转发
            code_body, _ = filter_creator_mention(code_body)

            if len(code_body) > CODE_SEG_HARD_LIMIT:
                # 需要自动分段 — 每段都带完整@（原始+自动补的）
                chunks = smart_split_code(code_body, CODE_SEG_HARD_LIMIT)
                all_mention_prefix = build_mention_prefix(mentioned_bots)
                for i, chunk in enumerate(chunks):
                    new_hdr = f"[CODE:{i+1}/{len(chunks)}:{filename}:{len(chunk)}]"
                    segment = f"{all_mention_prefix} {new_hdr}\n{chunk}"
                    if len(segment) > DISCORD_MSG_LIMIT:
                        segment = segment[:DISCORD_MSG_LIMIT - 30] + "\n...(截断)"
                    try:
                        await _send(channel, segment)
                    except Exception as e:
                        print(f"[SPLIT] Segment {i+1} failed: {e}")
                print(f"[SPLIT] {sender_name} CODE {filename} → {len(chunks)} segments")
                return

    # === 组装最终消息 ===
    full_text = f"{header}\n{core_text}{recovery_footer}"

    if len(full_text) <= DISCORD_MSG_LIMIT:
        try:
            await _send(channel, full_text)
            await message.add_reaction("✅")
            print(f"[OK] {len(full_text)} chars{' (+extra@)' if extra_mentions else ''}")
        except Exception as e:
            print(f"[FAIL] {e}")
            try:
                await message.add_reaction("❌")
            except Exception:
                pass
    elif len(f"{extra_prefix}{core_text}") <= DISCORD_MSG_LIMIT:
        # 去掉"说："头部，但保留补上的@（否则目标收不到）
        try:
            await _send(channel, f"{extra_prefix}{core_text}")
            await message.add_reaction("✅")
            print(f"[OK-TRIMMED] header stripped, extra@ kept")
        except Exception as e:
            print(f"[FAIL] {e}")
    else:
        # 超长消息 → 自动分段，每段带完整@
        all_mention_prefix = build_mention_prefix(mentioned_bots)
        overhead = len(all_mention_prefix) + len(header) + 20
        chunks = smart_split_code(core_text, DISCORD_MSG_LIMIT - overhead)
        for i, chunk in enumerate(chunks):
            tag = f" ({i+1}/{len(chunks)})" if len(chunks) > 1 else ""
            segment = f"{all_mention_prefix} {header}{tag}\n{chunk}"
            if len(segment) > DISCORD_MSG_LIMIT:
                segment = segment[:DISCORD_MSG_LIMIT - 30] + "\n...(截断)"
            try:
                await _send(channel, segment)
                print(f"[SPLIT] Segment {i+1}/{len(chunks)}: {len(segment)} chars")
            except Exception as e:
                print(f"[SPLIT] Segment {i+1} failed: {e}")
        try:
            await message.add_reaction("✂️")
        except Exception:
            pass

    print(f"[DONE] {sender_name}")


if __name__ == "__main__":
    try:
        client.run(USER_TOKEN)
    except Exception as e:
        print(f"[FATAL] {e}")
        log_crash(str(e))
