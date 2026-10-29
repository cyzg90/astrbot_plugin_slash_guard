# AstrBot QQ 官方机器人 Slash Guard

一个轻量的 AstrBot 插件，在 LLM 请求阶段静默拦截 QQ 官方机器人群聊中以 `/` 开头的消息，避免未知斜杠输入触发 LLM 回复。

## 适用范围

- 平台：`qq_official`（WebSocket）和 `qq_official_webhook`（Webhook）。
- 仅处理群聊，不处理私聊或其他平台。
- 判断文本时会忽略开头的空白，因此 `  /abc` 也在拦截范围内。
- 不发送拦截提示；命中时会记录一条 `[SlashGuard] Blocked slash-prefixed LLM request` 日志。

## 安装与使用

本插件没有额外配置项，也不需要额外的第三方 Python 依赖。启用后自动生效，禁用或卸载即可停止拦截。

安装入口及管理方式参见 [AstrBot 官方插件文档](https://docs.astrbot.app/use/plugin.html)。

### 从仓库链接安装

1. 打开 AstrBot WebUI → 插件 → 安装插件（+）→ 从链接安装。
2. 输入仓库地址：`https://github.com/cyzg90/astrbot_plugin_slash_guard`。
3. 安装后，在“已安装”页面确认插件已启用且没有加载错误，并确认当前会话配置允许使用此插件。

### 从 ZIP 安装

在 AstrBot WebUI → 插件 → 安装插件（+）→ 从文件安装，上传包含 `main.py`、`metadata.yaml` 等完整插件文件的 ZIP 包。安装后同样检查加载状态。

## 使用示例

以下示例假设插件已启用，消息来自支持平台的群聊，并已满足 AstrBot 的唤醒及会话配置条件：

| 消息或场景 | 本插件的行为 |
| --- | --- |
| `/sid`、`/provider` 等由指令处理器正常处理的命令 | 通常在 LLM 请求阶段之前已被处理，本插件不影响这部分处理 |
| `/abc` 等未知斜杠输入，最终进入 LLM 请求阶段 | 静默拦截该次请求 |
| `  /abc`，最终进入 LLM 请求阶段 | 忽略开头空白后识别 `/`，静默拦截 |
| `@机器人 你好` | 不因斜杠规则拦截，继续由 AstrBot 处理 |
| 私聊中的 `/abc`，或其他平台的消息 | 不处理 |
| 其他插件将 `/xxx` 主动提交给 LLM，且经过同一事件钩子 | 原事件文本仍可识别为斜杠开头时，也可能被拦截 |

## 工作阶段与局限

本插件使用 `on_llm_request` 钩子，在调用 LLM 前检查消息，命中规则时调用 `event.stop_event()` 停止事件。钩子说明参见 [AstrBot 官方消息事件文档](https://docs.astrbot.app/dev/star/guides/listen-message-event.html)。

为尽量保留可能已被唤醒处理移除的斜杠前缀，插件会检查消息链中的纯文本、原始字典消息的 `content`、消息对象的 `message_str` 和事件的 `message_str`。任一候选文本去掉开头空白后以 `/` 开头，就会命中规则；判断依据是事件消息，而不是 LLM 请求中的 prompt。

- 这是 LLM 请求阶段的拦截，不是消息入口过滤；已经执行的指令、插件操作或已发送的消息不会被撤销。
- 不区分未知命令与其他插件有意交给 LLM 的斜杠命令。后者经过此钩子时也可能被拦截。
- 其他插件若直接调用模型接口、绕过此钩子，本插件无法拦截。
- 只检查半角 `/`，不匹配全角 `／`。若所有候选文本的斜杠前都保留了非空白字符（例如原始提及标记），也可能无法识别。
- 实际表现受 AstrBot 版本、适配器提供的消息字段和其他插件处理方式影响。安装后应在实际群聊中验证；插件在 AstrBot v4.29.3 版本进行了验证。

## 许可证

[MIT License](LICENSE)
