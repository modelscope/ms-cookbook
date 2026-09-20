<!-- Generated from ../source-html/chapter-27.html; do not edit independently. -->

# MCP：让模型连接外部工具

大模型可以根据训练中学到的知识回答问题，也可以根据当前对话中的材料完成摘要、分类和内容生成。但是，模型通常不知道企业数据库里刚刚更新的订单状态，也不能只凭一段 Prompt 就真正读取本地文件、创建日程或者修改项目任务。要完成这些工作，模型需要通过应用连接外部数据和工具。

过去，为每一种模型应用连接文件系统、数据库和办公软件，往往都要单独编写一套适配代码。换一个 Agent 工具，原来的接口还可能无法直接复用。MCP 提供了一种标准化的连接方式，使支持该协议的应用能够发现外部能力、了解参数要求并调用这些能力。

重点介绍 MCP 的基本概念、架构、配置和调用过程，同时说明连接外部系统后必须建立的权限与安全边界。

<a id="c27-s1"></a>

## <strong>MCP 是什么</strong>

MCP（Model Context Protocol），即模型上下文协议。它是一套面向大模型应用的开放协议，用来规范应用怎样连接外部数据源、工具和系统，以及双方怎样描述能力、传递参数和返回结果。这里所谓的“连接模型”，实际执行协议的通常不是模型参数本身，而是承载模型的应用。用户在聊天界面、编程工具或 Agent 平台中提出任务，应用根据需要连接一个或多个 MCP Server，再把可用工具和返回结果提供给模型。模型负责理解任务和决定下一步，Host 与 Client 负责协议通信、权限控制和结果转交，Server 负责执行具体能力。MCP 可以协助开发者能够<strong>以一致的方式将各种数据源、工具和功能连接到 AI 模型</strong>，就像 USB-C 让不同设备能够通过相同的接口连接一样，相关样例如下图所示。

![正文配图](<../../assets/manuscript-20260914/c25-8d70af57c23ef8.webp>)

MCP Server 可以向应用提供三类常见能力，分别是 Resources、Prompts 和 Tools。Resources 主要用于向应用提供可读取并放入上下文的数据，例如文件内容、数据库记录和代码仓库信息；Prompts 主要由服务端提供可复用的提示模板或交互入口，例如代码审查模板、日报生成模板等；Tools 则用于提供可以被应用调用并实际执行操作的函数能力，例如搜索网页、读取文件、创建日程或更新任务。

一个 MCP 工具通常会说明工具名称、功能描述、输入参数结构以及可能的返回内容。应用不需要预先把每个工具写死在代码中，而是可以先询问 Server 有哪些工具，再根据返回的结构调用其中一个工具。

<p></p>

<a id="c27-s2"></a>

## <strong>MCP 解决什么问题</strong>

以一个项目管理 MCP 服务为例，可能提供下面三个工具 list&#95;projects、get&#95;project&#95;tasks 和 get&#95;project&#95;tasks。其中，list&#95;projects 和 get&#95;project&#95;tasks 工具主要用于读取信息，update&#95;task&#95;status 工具会改变外部系统。它们都可以通过 MCP 暴露，在用户运行和相关授权的情况下，模型可以自动调用、组织和决策。其中 MCP 解决的是怎样连接和调用的问题，利用 MCP，大模型或 Agent 就不再需要关心后面连接的是文件、数据库、搜索引擎还是企业系统，只要通过 MCP 就能发现并调用这些能力。因此，可以把 MCP 理解成大模型连接外部世界的“通用插口”，集合 MCP 系统可以进一步降低了不同模型、工具和业务系统之间反复适配的开发成本。是否采用 MCP 结构间的差异如下图所示。

![正文配图](<../../assets/manuscript-20260914/c25-bc760b9d03689e.webp>)

例如，我们构建的 3 种 Agent 应用，可能需要连接文件系统、知识库、数据库、项目管理和邮件系统等外部能力，采用 MCP 后，外部能力可以通过 MCP Server 按照统一方式暴露。支持 MCP 的 Host 只需要实现协议客户端，就可以连接不同 Server。这样做主要减少了下面几类重复工作：

1\. <strong>能力发现，</strong>Host 可以获取 Server 提供的工具列表，不必为每个工具单独编写固定菜单。

2\. <strong>参数描述，</strong>工具可以使用结构化 Schema 说明必填字段、字段类型和可选值，便于 Host 校验，也便于模型选择正确参数。

3\. <strong>调用与返回，</strong>不同工具使用统一的协议消息完成请求、响应、错误和通知，不需要每个应用重新定义一套交互格式。

4\. <strong>复用与替换，</strong>同一个 MCP Server 可以被多个兼容应用使用；更换底座模型时，只要 Host 仍然支持 MCP，外部工具层通常不需要全部重写。

5\. <strong>边界集中管理，</strong>Host 可以在统一位置管理 Server 连接、用户确认、日志、超时和可用范围，Server 也可以在执行侧再次检查身份和权限。

当然，MCP 并没有消除外部系统原有的开发工作。结合实际业务场景，数据库仍然需要表结构和查询权限，业务系统仍然需要 API，邮件服务仍然需要身份认证。

<a id="c27-s3"></a>

## <strong>MCP 的基本架构</strong>

MCP 采用 Host、Client 和 Server 组成的架构。一个 Host 可以连接多个 Server，通常会为每个 Server 建立相对独立的 Client 连接。不同 Server 不应该默认看到完整对话，也不应该直接读取其他 Server 的返回内容；需要共享哪些上下文，由 Host 决定，架构的相关样例如下图所示。

![正文配图](<../../assets/manuscript-20260914/c25-63e7cae9c84caa.webp>)

<a id="c27-s4"></a>

### <strong>Host：承载模型并控制整体过程</strong>

Host 是用户实际使用的应用，例如魔搭 Notebook 中运行的 Agent 应用、魔搭创空间中的在线助手或支持 MCP 的企业智能助手。Host 主要负责承载大模型并接收用户任务，同时管理一个或多个 MCP Client，根据当前任务决定向模型提供哪些工具和资源。Host 还会负责用户授权、确认提示和安全策略，并把工具调用结果重新加入当前任务上下文，让模型可以继续完成后续推理和生成。

因此，Host 并不只是一个简单的聊天窗口，而是整个 MCP 调用过程的协调者。它负责把模型、用户、MCP 连接和权限策略组织在一起，同时记录调用过程，并处理失败、取消和超时等情况。即使某个 MCP Server 声明自己具备删除文件等高风险能力，Host 仍然可以选择不向模型暴露该工具，或者要求用户在真正执行操作前再次确认，从而对整个调用过程进行统一控制。

<a id="c27-s5"></a>

### <strong>Client：维护与单个 Server 的协议连接</strong>

Client 位于 Host 内部，负责与某个 MCP Server 通信。它会按照协议建立连接、交换支持的能力、发送工具发现与调用请求，并把 Server 返回的结果交给 Host。用户通常不会直接操作 Client，但连接失败、协议版本不兼容和响应超时等问题，往往发生在这一层。

为了保持边界清楚，一个 Client 通常只对应一个 Server。Host 可以同时创建多个 Client，例如一个连接文件系统 Server，一个连接数据库 Server，另一个连接项目管理 Server。Host 负责决定哪些信息可以在这些连接之间传递，而不是让多个 Server 自行共享全部上下文。

<p></p>

<a id="c27-s6"></a>

### <strong>Server：把外部能力封装成标准接口</strong>

Server 负责向 Client 提供工具（Tools）、外部资源（Resources）或提示词（Prompts）。它既可以作为应用运行环境中的进程提供能力，也可以独立部署为通过网络访问的服务。再魔搭中搭建和托管 Server，可以利用魔搭 Notebook 中的 Client 发起请求。Server 内部还可以继续调用普通 API、数据库驱动或其他业务服务。例如，订单 MCP Server 收到`query_order`工具调用后，可以使用企业已有的订单 API 查询数据，再把必要字段整理成工具结果返回。MCP Server 不需要替代原有订单系统，它负责把原有能力转换成模型应用容易发现和调用的形式。

MCP Server 能够访问的信息并不是由 MCP 协议自动决定的，而是由具体的调用方式和权限边界决定。通常情况下，Server 只会收到 Host 为完成当前任务而传递的参数和上下文，以及在相关权限下的其他资源。

结合上述介绍的 MCP 相关结构，MCP 本身提供的是标准化连接和调用机制，并不会自动扩大 Server 的权限范围，一个 MCP Server 最终能做什么，主要取决于三方面：Host 实际传给它什么信息、Server 运行环境本身拥有什么系统权限，以及它连接外部系统时使用了什么账号或令牌<strong>。</strong>

<p></p>

<a id="c27-s7"></a>

### <strong>两种常见连接方式</strong>

MCP 中，Client 和 Server 之间通常使用 JSON-RPC 交换消息，而这些消息需要通过具体的连接方式传输。最常见的两种方式是 stdio 和 Streamable HTTP。stdio 适合本地场景，Client 会直接启动 MCP Server，并通过标准输入输出进行通信，通常用于本地工具、命令行程序或桌面应用。它的特点是部署简单、通信直接，但需要注意本地运行环境、进程权限和文件访问范围。

Streamable HTTP 更适合远程或共享服务。MCP Server 可以独立部署在服务器上，Client 通过 HTTP 与它通信，适合团队共用工具、云端服务和企业内部系统。由于需要经过网络访问，因此要重点考虑 HTTPS、身份认证和访问权限。部分旧版本 MCP 服务可能仍使用 SSE，但目前应优先根据实际客户端和服务端支持情况选择 stdio 或 Streamable HTTP。

<p></p>

<a id="c27-s8"></a>

## <strong>MCP 与 API 的区别</strong>

API 和 MCP 不是互相替代的两种技术，它们解决的问题不一样。API 主要是给程序调用的，通常定义某个具体系统可以提供什么接口，比如查询订单、提交审批、发送邮件；而 MCP 更关注怎么把这些能力以大模型容易理解和调用的方式提供出来。也就是说，API 更像是底层能力接口，MCP 更像是在这些能力外面加了一层统一的说明和调用规范，让 Host 或 Agent 能自动发现有哪些工具、每个工具需要什么参数，以及应该怎样调用。以订单查询为例，企业可能本来就有一个“根据订单号查询订单状态”的 API。传统程序需要开发人员先阅读接口文档，再按照接口要求写代码调用；如果接入 MCP，可以由 MCP Server 在内部调用这个 API，同时把它包装成一个模型可理解的工具，比如“查询订单状态”，并说明需要传入“订单号”这个参数。这样，大模型不需要直接理解各种复杂接口，只需要按照 MCP 提供的工具描述进行调用即可。以下是一个工具的相关样例：

```json
{
  "name": "query_order",
  "description": "根据订单编号查询订单状态和预计发货时间",
  "inputSchema": {
    "type": "object",
    "properties": {
      "order_id": {
        "type": "string",
        "description": "完整订单编号"
      }
    },
    "required": ["order_id"]
  }
}
```

<p></p>

参考上述样例，业务 API 负责真正查询订单，MCP Server 负责把该能力描述成标准工具，MCP Client 负责发现并调用工具，Host 负责把工具提供给模型并控制权限。原有 API 不需要因为接入 MCP 而取消，如果某个程序或服务只需要固定调用一个 API，并不需要模型发现工具或根据任务选择操作，直接使用 API 通常更简单。MCP 则更适合需要让多个模型应用动态连接多种能力的场景。

<p></p>

<a id="c27-s9"></a>

## <strong>在魔搭中配置 MCP</strong>

魔搭社区提供 MCP 广场、Notebook、MS-Agent 等与 MCP 相关的能力。MCP 广场用于查找和了解已经发布的 Server，Notebook 提供云端实验环境，MS-Agent 则负责把大模型与 MCP 工具连接起来。除了使用广场中的现成 Server，开发者也可以将自己的业务函数封装成 MCP 工具。本节采用后一种方式：在魔搭 GPU Notebook 中启动 Qwen3-4B，并自建一个天气查询 MCP Server，完整验证模型发现和调用外部工具的过程。

<p></p>

<a id="c27-s10"></a>

### <strong>实验目标与运行流程</strong>

本实验要求用户只用自然语言提出“查询杭州明天的天气”，由 Qwen3-4B 选择天气工具并生成参数。天气 MCP 根据地区和日期调用公开天气 API，再把结构化结果返回给模型。整个实验均在同一个魔搭 GPU Notebook 实例中完成。

```text
用户提出天气问题
    ↓
Qwen3-4B判断是否需要调用工具
    ↓
MS-Agent向天气MCP发送工具名称和参数
    ↓
天气MCP调用Open-Meteo公开天气API
    ↓
MCP返回结构化数据，Qwen3-4B组织最终回答
```

在这条链路中，魔搭 Notebook 是运行环境，MS-Agent 承担 Host 和 Client 侧的工作，自建的天气服务是 MCP Server，Open-Meteo 则是 Server 在执行工具时访问的外部 API。模型不直接请求天气网站，也不凭训练数据猜测天气，而是根据 MCP 返回的本次查询结果作答。

<p></p>

<a id="c27-s11"></a>

### <strong>准备魔搭 Notebook 实验环境</strong>

<p></p>

创建魔搭 Notebook 实例时，配置相关环境，本次实验验证时使用的主要版本如下：

<table><tbody><tr><td><p>组件</p></td><td><p>实验版本</p></td></tr><tr><td><p>Python</p></td><td><p>3.12.13</p></td></tr><tr><td><p>ms-agent</p></td><td><p>1.6.0</p></td></tr><tr><td><p>ms-swift</p></td><td><p>4.4.2</p></td></tr><tr><td><p>vLLM</p></td><td><p>0.19.1</p></td></tr><tr><td><p>OmegaConf</p></td><td><p>2.3.0</p></td></tr><tr><td><p>requests</p></td><td><p>2.34.2</p></td></tr></tbody></table>

在 Notebook 中运行下面的代码，可以记录当前实验环境：

```python
import sys
import importlib.metadata as metadata

def installed_version(package):
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return "未安装"

print("Python：", sys.version.split()[0])
for package in ["ms-agent", "ms-swift", "vllm", "omegaconf", "requests"]:
    print(f"{package}：{installed_version(package)}")
```

<p></p>

本次实验中的相关环境如下：

![正文配图](<../../assets/manuscript-20260914/c25-9092e50e383de4.webp>)

![正文配图](<../../assets/manuscript-20260914/c25-e125e27203ef7a.webp>)

<p></p>

<a id="c27-s12"></a>

### <strong>启动 Qwen3-4B 推理服务</strong>

<p></p>

在魔搭 GPU Notebook 中打开一个终端，执行以下命令启动 Qwen3-4B。模型服务需要在后续实验期间持续运行，因此不要关闭这个终端。

<p></p>

```bash
CUDA_VISIBLE_DEVICES=0 swift deploy \
  --model Qwen/Qwen3-4B \
  --load_args false \
  --infer_backend vllm \
  --enable_thinking false \
  --host 0.0.0.0 \
  --port 18002 \
  --api_key 123 \
  --vllm_gpu_memory_utilization 0.8 \
  --vllm_max_model_len 8000 \
  --max_new_tokens 2000
```

其中，`--infer_backend vllm`指定使用 vLLM 推理，`--port 18002`指定服务端口，`--enable_thinking false`关闭本次实验不需要展示的思考输出。示例中的密钥只用于同一 Notebook 实例内的课堂实验；如果服务需要对外提供，应改用随机生成的高强度密钥，并结合网络访问控制。模型启动后，在 Notebook 代码单元中访问 OpenAI 兼容的模型列表接口：

```python
import requests

MODEL_API_BASE = "http://127.0.0.1:18002/v1"
MODEL_API_KEY = "123"
MODEL_ID = "Qwen3-4B"

response = requests.get(
    MODEL_API_BASE + "/models",
    headers={"Authorization": "Bearer " + MODEL_API_KEY},
    timeout=(10, 30),
)
response.raise_for_status()
available_models = [item["id"] for item in response.json()["data"]]
print("模型服务连接成功")
print("模型：", available_models[0])
```

启动服务及实验结果如下：

![正文配图](<../../assets/manuscript-20260914/c25-8521b88bcf4abc.webp>)

![正文配图](<../../assets/manuscript-20260914/c25-e6d2b273260778.webp>)

实验中得到的结果为：

![正文配图](<../../assets/manuscript-20260914/c25-c96ea9b457168c.webp>)

<p></p>

<a id="c27-s13"></a>

### <strong>编写天气查询 MCP 工具</strong>

<p></p>

天气 MCP 使用 Open-Meteo 提供的公开接口，不需要申请第三方 API Key。Server 先调用地理编码接口，把地区名称解析为经纬度和时区，再调用预报接口获取指定日期的天气。实验将工具查询范围限制为当地今天至未来十五天，`target_date`可以填写`today`、`tomorrow`或`YYYY-MM-DD`。下面是工具的核心代码。完整的天气代码、天气现象代码表和异常处理保存在本章配套 Notebook 中。

```python
import socket
import requests
from mcp.server.fastmcp import FastMCP

with socket.socket() as port_probe:
    port_probe.bind(("127.0.0.1", 0))
    WEATHER_MCP_PORT = port_probe.getsockname()[1]

weather_mcp = FastMCP(
    "Public Weather MCP",
    host="127.0.0.1",
    port=WEATHER_MCP_PORT,
    stateless_http=True,
    json_response=True,
)

@weather_mcp.tool()
def get_weather(area: str, target_date: str) -> dict:
    """查询某个地区在指定日期的天气预报。area应为城市或“城市,省份/国家”；target_date支持today、tomorrow或YYYY-MM-DD。"""
    location = resolve_area(area)
    day = parse_target_date(target_date, location["timezone"])
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "start_date": day.isoformat(),
            "end_date": day.isoformat(),
            "daily": ("weather_code,temperature_2m_max,temperature_2m_min,"
                      "precipitation_probability_max,wind_speed_10m_max"),
            "timezone": location["timezone"],
        },
        timeout=20,
    )
    response.raise_for_status()
    daily = response.json()["daily"]
    weather_code = daily["weather_code"][0]
    place = "，".join(filter(None, [
        location.get("name"), location.get("admin1"), location.get("country")
    ]))
    return {
        "requested_area": area,
        "resolved_area": place,
        "date": daily["time"][0],
        "timezone": location["timezone"],
        "weather_code": weather_code,
        "weather": WMO_WEATHER.get(weather_code, f"未知代码 {weather_code}"),
        "temperature_max_c": daily["temperature_2m_max"][0],
        "temperature_min_c": daily["temperature_2m_min"][0],
        "precipitation_probability_max_percent": daily["precipitation_probability_max"][0],
        "wind_speed_max_kmh": daily["wind_speed_10m_max"][0],
        "data_source": "Open-Meteo",
    }
```

其中，`@weather_mcp.tool()`把普通 Python 函数注册为 MCP 工具。FastMCP 会根据函数名、类型标注和说明文字生成工具 Schema，因此`area`和`target_date`的含义必须写清楚。`resolve_area`负责地区解析，`parse_target_date`负责日期格式和查询范围校验，函数最后把 API 结果整理为稳定字段。拆分这些职责，可以让错误发生时更容易判断是地区、日期还是天气接口出了问题。

需要注意，不同版本 FastMCP 的启动参数可能不同。本实验使用的版本要求在创建`FastMCP`对象时填写`host`和`port`，而不是把这两个参数传给`run()`。否则会出现`FastMCP.run() got an unexpected keyword argument 'host'`。

<p></p>

<a id="c27-s14"></a>

### <strong>启动并注册天气 MCP Server</strong>

完成工具定义后，在 Notebook 后台线程中启动 Streamable HTTP 服务。后台线程使 MCP Server 能够持续响应请求，同时不阻塞后续代码单元。

```python
import threading

def run_weather_server():
    weather_mcp.run(transport="streamable-http")

weather_server_thread = threading.Thread(
    target=run_weather_server,
    daemon=True,
    name="weather-mcp",
)
weather_server_thread.start()

WEATHER_MCP_URL = f"http://127.0.0.1:{WEATHER_MCP_PORT}/mcp"
weather_mcp_config = {
    "mcpServers": {
        "weather": {
            "type": "streamable_http",
            "url": WEATHER_MCP_URL,
        }
    }
}
```

这里的`weather`是 MS-Agent 内部使用的 Server 连接名称，`get_weather`才是模型能够调用的工具名称。配置中的`streamable_http`必须与 Server 启动时使用的`streamable-http`传输方式对应，地址末尾的`/mcp`也不能遗漏。实验中服务成功启动后输出如下：

```text
Application startup complete.
Uvicorn running on http://127.0.0.1:58545
天气 MCP Server 已启动： http://127.0.0.1:58545/mcp
```

端口由 Notebook 在每次实验时动态选择，因此重新运行后出现不同端口属于正常现象，不应把示例中的`58545`固定写入配置。平台注册后的结果如下。

![正文配图](<../../assets/manuscript-20260914/c25-9fff9add06d11f.webp>)

<a id="c27-s15"></a>

### <strong>使用 MCP 广场中的托管服务</strong>

自建天气 MCP 适合解释 Server 的实现过程，但并非每次使用 MCP 都要重新开发服务。魔搭 MCP 广场（https://modelscope.cn/mcp）集中展示了社区发布的 MCP Server，服务页面通常会提供工具说明、源码信息、运行参数和可用的连接配置。MS-Agent 的官方示例也使用广场中的`fetch`服务演示 Streamable HTTP 连接。本次择 MCP 广场中的[`@modelcontextprotocol/fetch`](<https://modelscope.cn/mcp/servers/@modelcontextprotocol/fetch>)。它提供一个名为`fetch`的只读工具，可以根据 URL 获取公开网页内容。实际操作步骤如下：

<p></p>

1. 登录魔搭社区并进入 MCP 广场，在搜索框中输入`fetch`；
2. 进入`@modelcontextprotocol/fetch`服务页面，检查发布者、源码、工具说明和所需参数；
3. 在页面提供的托管入口启动服务，传输方式选择 Streamable HTTP；
4. 等待服务状态变为可用，再复制页面生成的完整连接地址；
5. 回到魔搭 Notebook，把地址填入`MCP_SERVER_URL`，不要自行拼接用户标识或端点路径。

魔搭 MCP 广场中的 fetch 页面如下：

![正文配图](<../../assets/manuscript-20260914/c25-fca24d3413997d.webp>)

随后按照 MS-Agent 要求建立`mcpServers`配置：

```python
mcp_config = {
    "mcpServers": {
        "fetch": {
            "type": "streamable_http",
            "url": MCP_SERVER_URL,
        }
    }
}
```

外层的`fetch`是当前 Agent 使用的 Server 连接名称，`type`必须与托管时选择的传输方式相符，`url`必须使用服务页面生成的完整地址。配置完成只说明客户端已经知道连接信息，服务是否真正可用还要通过工具发现和调用来验证。注册成功结果如下：

![正文配图](<../../assets/manuscript-20260914/c25-6f1b45f76f4910.webp>)

<a id="c27-s16"></a>

## <strong>调用 MCP 工具</strong>

<p></p>

MCP Server 启动后，不应立即把所有问题都交给大模型。更稳妥的验证顺序是先用 MCP Client 完成工具发现和直接调用，确认 Server 及外部 API 正常，再让 Qwen3-4B 自主选择工具。这样可以把协议连接故障、工具自身故障和模型调用问题分开排查，整体流程如下图所示。

![正文配图](<../../assets/manuscript-20260914/c25-d16b20c5ebe28a.webp>)

<p></p>

<a id="c27-s17"></a>

### <strong>发现并直接验证工具</strong>

<p></p>

下面的代码建立 MCP 会话，先调用`list_tools()`读取 Server 公开的工具列表，再以确定参数直接调用`get_weather`。这一步不经过 Qwen3-4B。

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def check_weather_mcp():
    async with streamable_http_client(WEATHER_MCP_URL) as streams:
        read_stream, write_stream, _ = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("发现的工具：", [tool.name for tool in tools.tools])
            result = await session.call_tool(
                "get_weather",
                arguments={"area": "杭州,浙江", "target_date": "today"},
            )
            if result.isError:
                raise RuntimeError(str(result.content))
            for block in result.content:
                if getattr(block, "type", None) == "text":
                    print(block.text)

await check_weather_mcp()
```

运行上述逻辑，执行结果如下：<br>


![正文配图](<../../assets/manuscript-20260914/c25-5e3021e752014b.webp>)

<p></p>

<a id="c27-s18"></a>

### <strong>让 Qwen3-4B 调用天气 MCP</strong>

<p></p>

结合上述才注册的工具，可以继续把启动的 Qwen3-4B 配置给 MS-Agent。模型接口和天气 MCP 分别配置：前者负责推理，后者负责提供工具。

```python
from omegaconf import OmegaConf
from ms_agent import LLMAgent

agent_config = OmegaConf.create({
    "llm": {
        "service": "modelscope",
        "model": MODEL_ID,
        "modelscope_api_key": MODEL_API_KEY,
        "modelscope_base_url": MODEL_API_BASE,
    },
    "generation_config": {
        "temperature": 0.0,
        "max_tokens": 2000,
        "stream": False,
        "extra_body": {"enable_thinking": False},
    },
    "max_chat_round": 6,
})

weather_agent = LLMAgent(
    config=agent_config,
    tag="weather-demo",
    mcp_config=weather_mcp_config,
)

await weather_agent.run(
    "请调用天气查询工具，查询杭州明天的天气。"
    "请说明工具实际匹配的地区、日期、天气状况、最高和最低气温、"
    "最高降水概率与最大风速。只使用本次工具返回的数据；调用失败时如实说明。"
)
```

运行时，MS-Agent 先连接名为`weather`的 Server 并发现`get_weather`。Qwen3-4B 根据用户问题和工具 Schema 生成了下面的调用：

```json
{
  "name": "weather---get_weather",
  "arguments": {
    "area": "杭州",
    "target_date": "tomorrow"
  }
}
```

<p></p>

其中，`weather---get_weather`是 MS-Agent 组合 Server 连接名称和工具名称后显示的标识。`area`与`target_date`不是预先写死的调用参数，而是 Qwen3-4B 根据“杭州明天”生成的结构化参数。相关注册结果如下图所示。

![正文配图](<../../assets/manuscript-20260914/c25-8672cb597435bf.webp>)

<p></p>

<a id="c27-s19"></a>

### <strong>处理工具返回与最终回答</strong>

天气 MCP 收到参数后，将“杭州”解析为“杭州，浙江，中国”，根据当地时区把`tomorrow`转换为 2026 年 9 月 7 日，并返回：

```json
{
  "requested_area": "杭州",
  "resolved_area": "杭州，浙江，中国",
  "date": "2026-09-07",
  "timezone": "Asia/Shanghai",
  "weather_code": 51,
  "weather": "小毛毛雨",
  "temperature_max_c": 29.0,
  "temperature_min_c": 21.6,
  "precipitation_probability_max_percent": 31,
  "wind_speed_max_kmh": 13.0,
  "data_source": "Open-Meteo"
}
```

Qwen3-4B 随后依据这组结果生成自然语言回答，列出了实际匹配地区、日期、天气状况、最高和最低气温、降水概率及最大风速。至此，“理解问题—选择工具—生成参数—执行工具—处理结果”的调用链路完成。结合大模型执行结果如下：

![正文配图](<../../assets/manuscript-20260914/c25-cdd5202f43a4b6.webp>)

<a id="c27-s20"></a>

### <strong>调用 MCP 广场中的 fetch 服务</strong>

完成托管和配置后，先直接连接服务并检查工具列表。下面的测试样例网站信息`https://example.com`。

```python
async def direct_fetch_check():
    async with streamable_http_client(MCP_SERVER_URL) as streams:
        read_stream, write_stream, _ = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Server返回的工具：", [tool.name for tool in tools.tools])
            result = await session.call_tool(
                "fetch",
                arguments={
                    "url": "https://example.com",
                    "max_length": 1000,
                    "start_index": 0,
                    "raw": False,
                },
            )
            if result.isError:
                raise RuntimeError(str(result.content))
            for block in result.content:
                if getattr(block, "type", None) == "text":
                    print(block.text)

await direct_fetch_check()
```

实际运行时，Server 公开了`fetch`工具，并返回了目标网页的正文片段和链接。这说明魔搭托管服务、Streamable HTTP 连接以及网页抓取工具本身均可工作。直接连接魔搭托管 fetch 服务、发现工具并返回网页内容如下图所示。

![正文配图](<../../assets/manuscript-20260914/c25-327d9bc6ee4c29.webp>)

直接调用成功后，再复用前面配置好的 Qwen3-4B，让模型自主选择工具：

<p></p>

```python
fetch_agent = LLMAgent(
    config=agent_config,
    tag="fetch-demo",
    mcp_config=mcp_config,
)

await fetch_agent.run(
    "请使用网页抓取工具读取https://example.com。"
    "调用时将max_length设为1000，并返回网页正文说明的主要用途和第一个链接。"
    "只能使用本次工具返回的内容；调用失败时请明确说明，不要补写。"
)
```

实验日志显示，MS-Agent 成功连接名为`fetch`的 Server，Qwen3-4B 选择了`fetch---fetch`并生成以下参数：

```json
{
  "url": "https://example.com",
  "max_length": 1000
}
```

工具返回网页内容后，模型据此说明该域名用于文档示例，并给出工具返回的第一个链接。检查这类结果时，应分别核对模型生成的参数、工具原始返回和最终回答。利用 Qwen3-4B 生成 fetch 工具调用参数、工具返回内容及最终回答，执行结果如下：

![正文配图](<../../assets/manuscript-20260914/c25-ffeaaa9aac2717.webp>)

直接使用魔搭 MCP 广场中的应用服务与自建天气 MCP 的区别在于，Server 的实现和运行环境由魔搭托管能力负责，Notebook 只需要保存连接配置并发起调用。无论使用现成服务还是自建服务，验证顺序都相同：检查服务状态、发现工具、直接测试，再让模型自主调用。

<p></p>

<a id="c27-s21"></a>

## <strong>MCP 权限管理</strong>

MCP 的权限管理不能只停留在“这个 Server 能不能连接”这一层，更重要的是明确三个问题：当前用户能访问哪些资源，模型能够调用哪些工具，以及每次调用会对外部系统产生什么影响。因此，权限控制应该从 Host、MCP Server 到后端业务系统逐层落实，并始终遵循最小权限原则。即使是只读工具，也不能默认认为没有风险，因为它仍然可能读取客户信息、源代码、访问令牌等敏感内容，所以需要限制可访问的目录、库表、字段和返回范围，并结合 Server 的实际实现确认是否存在额外的数据记录、缓存或外传行为。

对于会修改外部状态的操作，权限控制应随着风险逐步加强。创建文件、修改记录、发送邮件、添加日程等写入操作，最好在执行前向用户展示目标对象和关键参数，能够生成草稿或显示差异的，应优先让用户确认后再执行。同时还要避免网络超时、自动重试造成重复写入，可以通过幂等键、唯一约束或状态检查来降低风险。对于删除数据、转账、批量发送、公开发布、修改权限、执行命令和生产环境变更等高风险操作，则应默认限制自动执行，并保留明确的人工确认、二次审批和完整审计。

除了工具本身的权限，凭据和账号也需要单独控制。API Key、访问令牌等敏感信息不应出现在 Prompt、聊天记录、代码仓库或普通日志中，MCP Server 访问后端系统时应使用范围受限的专用账号和凭据，而不是直接继承过大的权限。对于敏感系统，还可以进一步把查询和修改能力拆分到不同 Server、不同账号甚至不同网络区域中。总体来说，MCP 权限管理的核心原则是：工具可以被发现，不代表就可以直接执行；一次授权也不代表以后所有操作都自动获得权限，权限应根据访问范围和操作风险逐级控制。

<p></p>

<a id="c27-s22"></a>

## <strong>MCP 安全风险</strong>

MCP 让模型不仅能够生成内容，还可以读取文件、查询数据库、调用网络服务，甚至修改外部系统，因此它带来的安全风险也比普通聊天模型更复杂。风险来源不仅包括用户输入，还包括网页、文档、数据库记录、工具返回结果、Server 代码以及第三方依赖。其中最典型的是 Prompt 注入：外部内容中可能隐藏恶意指令，诱导模型继续调用文件、网络或消息工具，形成危险的跨系统操作链。对此，不能只依赖模型“识别恶意提示”，而应该把所有外部内容都视为不可信数据，严格区分用户目标、系统规则和工具返回结果，并限制外部内容可以继续触发的工具范围。

另一类核心风险是越权访问和敏感信息泄漏。模型生成的参数不能被当作授权依据，Host 可以控制向模型暴露哪些工具，但 Server 仍然需要在每次调用时根据真实用户身份检查资源归属和访问权限，不能只在建立连接时验证一次。与此同时，还要控制数据在不同系统之间如何流动，只向 Server 传递完成当前任务所需的字段，对密钥、身份证号、手机号等敏感信息进行脱敏或拦截，远程连接使用 HTTPS，日志中避免保存完整凭据和敏感正文。尤其要注意，模型从一个 Server 读取到的数据，不应在没有明确授权的情况下自动发送到另一个外部 Server。

MCP 还存在恶意工具和供应链风险，因此生产环境不能只关注单次调用，而应建立完整的多层安全机制。接入 Server 前要检查来源、代码、依赖和所需权限；连接时使用受限账号、受限凭据和受控网络；工具发现后按只读、写入和高风险分类，只向模型开放真正需要的能力；执行前校验参数，对删除、发送、上传、修改权限等敏感操作要求人工确认；执行过程中限制超时、并发、返回量和网络范围；执行结束后检查工具返回内容，并保留必要的审计日志。对于正式环境，最好维护经过审核的 Server 白名单和版本清单，工具或版本发生变化后重新评估权限，并确保出现异常时能够快速停用 Server、撤销令牌和追溯操作记录。

<p></p>

<a id="c27-s23"></a>

## <strong>MCP 适合的场景</strong>

<p></p>

MCP 更适合这样的场景：外部工具和数据源比较多，希望这些能力能够被不同模型或 Agent 重复使用，同时又希望模型根据当前任务动态决定调用什么工具。 常见应用包括文件访问、数据库查询和搜索检索。例如，文件类 MCP Server 可以让模型浏览、读取和搜索项目文件，数据库类 Server 可以查询库存、订单和运营数据，搜索类 Server 则可以连接互联网、企业知识库或专业资料库。实际使用时，应尽量只开放完成任务所需的数据范围，文件访问优先采用只读方式，数据库优先使用只读账号或受控查询，并对查询范围、返回字段和结果数量进行限制；网页和搜索结果则应视为不可信输入，重要信息还需要保留来源并进行必要的交叉验证。

MCP 也很适合连接邮件、日历、网盘、项目管理系统以及企业已有的业务 API，让模型从“查询信息”进一步扩展到“完成操作”。例如，模型可以查询会议时间、整理项目进度、生成邮件草稿，也可以调用客服、物流、审批、工单和设备管理等业务能力。设计这类工具时，最好把能力拆成边界清楚的业务动作，例如分别提供“查询工单”“添加工单备注”和“关闭工单”，而不是直接给模型一个可以调用任意接口的万能工具。查询和修改也应尽量分开设置权限，对于发送邮件、修改共享权限、关闭工单、批量更新等会改变外部状态的操作，应保留必要的人工确认和审计记录。

但并不是所有接口都需要改造成 MCP。如果业务流程固定、调用关系明确、对延迟要求很高，而且根本不需要模型判断“下一步应该使用什么工具”，直接调用普通 API 往往更加简单可靠。对于删除数据、资金操作、生产环境变更等高风险任务，如果还没有完善的权限控制、人工审批、审计和回滚机制，也不应该仅仅因为 MCP 能够接入就立即实现自动化。简单来说，MCP 的价值主要体现在让模型能够灵活选择和组合多种外部能力，而固定、确定的系统调用仍然可以继续使用传统 API。

<p></p>

本章节所有实验数据和代码，可参考：

https://modelscope.cn/gallery/liucong/fae5791c-a024-412f-97c3-5fb93fee708e

<p></p>
