# 🌉 基于 Retryable Ticket 的 Layer1 ➔ Layer2 跨链消息系统
#### 用户通过 Layer1 合约操作，使用 Retryable Ticket 更新 Layer2 上的合约状态

> **概述**：实现一个支持跨链消息的系统，其中用户在 Layer1 合约中操作后，通过调用 `retryable ticket`（Greeter）来修改 Layer2 上的合约状态。



# 📜 Layer1 合约: `layer1.sol`

### 合约概述
该合约用于在 Layer1 向 Layer2 发送跨链消息，借助 Arbitrum 的 **Retryable Ticket** 系统，将用户的操作同步至 Layer2 上的目标合约。

---

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Arbitrum Inbox 接口，用于创建 Retryable Ticket
interface IArbitrumInbox {
    function createRetryableTicket(
        address to,
        uint256 l2CallValue,
        uint256 maxSubmissionCost,
        address excessFeeRefundAddress,
        address callValueRefundAddress,
        uint256 gasLimit,
        uint256 maxFeePerGas,
        bytes calldata data
    ) external payable returns (uint256);
}

contract L1ToL2Message {
    address public l2Target;                  // Layer2 合约地址
    address public inboxAddress = 0xaAe29B0366299461418F5324a79Afc425BE5ae21;  // Arbitrum Sepolia Inbox 地址

    event RetryableTicketCreated(uint256 indexed ticketId);

    constructor(address _l2Target) {
        l2Target = _l2Target;
    }

    // 向 L2 发送消息，通过 Arbitrum 的 Retryable Ticket 系统更新目标合约状态
    function sendMessageToL2(string memory _message) external payable {
        IArbitrumInbox inbox = IArbitrumInbox(inboxAddress);
        
        // 使用 `updateMessage` 函数编码消息数据
        bytes memory data = abi.encodeWithSignature("updateMessage(string)", _message);

        // 创建 Retryable Ticket
        uint256 ticketId = inbox.createRetryableTicket{value: msg.value}(
            l2Target,
            0,                     // L2 调用的数值
            0.01 ether,            // 最大提交费用
            msg.sender,            // 超额费用退款地址
            msg.sender,            // 调用值退款地址
            1_000_000,             // Gas 限额
            800 gwei,              // 每单位 Gas 的最大费用
            data
        );

        emit RetryableTicketCreated(ticketId);  // 发出事件，记录 Ticket ID
    }
}
```


# 📜 Layer2 合约: `layer2.sol`

### 合约概述
此合约用于接收来自 Layer1 的跨链消息更新。合约中的 `updateMessage` 函数会接收 Layer1 发送的消息内容并更新本地状态。 

---

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract L2MessageReceiver {
    string public message;  // 存储 Layer1 发来的消息

    // 消息更新事件
    event MessageUpdated(string newMessage);

    // 构造函数：初始化 message 默认值为 "no message"
    constructor() {
        message = "no message";
    }

    // 更新消息内容并触发事件
    function updateMessage(string memory _newMessage) external {
        message = _newMessage;
        emit MessageUpdated(_newMessage);
    }

    // 展示当前的 message 值
    function getMessage() external view returns (string memory) {
        return message;
    }
}
```



### scan.py
#### 使用 Python 的 Web3 库，查询 Arbitrum Sepolia 上已部署的 layer2.sol 合约中 `message` 字段的初始状态

```python
from web3 import Web3

# 配置 Arbitrum Sepolia 网络的 RPC URL
arb_sepolia_rpc = "https://arbitrum-sepolia.infura.io/v3/..."
web3 = Web3(Web3.HTTPProvider(arb_sepolia_rpc))

# -----------------------------
# 合约信息
# -----------------------------
contract_address = "0x12fBAf906c3c4af268976bF855B2159813909D69"  # 部署在 Arbitrum Sepolia 上的合约地址

# 合约 ABI，定义了合约的方法和事件
contract_abi = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "string",
                "name": "newMessage",
                "type": "string"
            }
        ],
        "name": "MessageUpdated",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "getMessage",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "message",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_newMessage",
                "type": "string"
            }
        ],
        "name": "updateMessage",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# -----------------------------
# 合约实例化
# -----------------------------
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# -----------------------------
# 获取 `message` 的当前状态
# -----------------------------
def get_message():
    """
    调用合约的 `getMessage` 方法以获取当前存储的消息内容。
    """
    try:
        message = contract.functions.getMessage().call()  # 获取 `message` 字段的值
        print("🌐 当前消息内容:", message)
    except Exception as e:
        print("❗ 获取消息时出错:", e)

# 执行查询
if __name__ == "__main__":
    print("🔍 正在查询合约中存储的消息状态...")
    get_message()
```

### layer1.py
#### 使用 Python Web3 库，调用以太坊 Sepolia 网络上的 Layer1 合约以向 Arbitrum Sepolia 上的 Layer2 合约发送消息 `"call from layer1"`

```python
from web3 import Web3

# 连接到以太坊 Sepolia 测试网
rpc_url = "https://sepolia.infura.io/v3/..."
w3 = Web3(Web3.HTTPProvider(rpc_url))

# -----------------------------
# 连接状态检查
# -----------------------------
if not w3.is_connected():
    raise ConnectionError("无法连接到以太坊网络")

# -----------------------------
# Layer1 合约地址与 ABI
# -----------------------------
contract_address = Web3.to_checksum_address("0xecc354307ac2c7728968e38e23dbe60127ae1cd0")  # 部署在以太坊 Sepolia 网络的 Layer1 合约地址

# 合约 ABI
contract_abi = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_l2Target",
                "type": "address"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "ticketId",
                "type": "uint256"
            }
        ],
        "name": "RetryableTicketCreated",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_message",
                "type": "string"
            }
        ],
        "name": "sendMessageToL2",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "inboxAddress",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "l2Target",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# -----------------------------
# 创建合约实例
# -----------------------------
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# -----------------------------
# 交易参数设置
# -----------------------------
sender_address = Web3.to_checksum_address("0xa2F14D1f80c5fca498b74400f65679738C64B43d")
private_key = "ae3..."  # 请妥善保管私钥信息
message = "call from layer1"  # 要发送的消息
gas_fee = w3.to_wei(0.06, "ether")  # gas 费，单位为 ETH

# -----------------------------
# 构造交易
# -----------------------------
transaction = contract.functions.sendMessageToL2(message).build_transaction({
    "from": sender_address,
    "value": gas_fee,
    "gas": 800000,
    "gasPrice": w3.to_wei("10", "gwei"),
    "nonce": w3.eth.get_transaction_count(sender_address),
})

# -----------------------------
# 签署与发送交易
# -----------------------------
signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)  # 签署交易
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)  # 发送交易

# -----------------------------
# 等待交易完成并打印回执
# -----------------------------
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Transaction receipt:", tx_receipt)
```

#### 成功执行交易的回执🏅
Transaction receipt: 
{
  'blockHash': HexBytes('0x09ef4706780ac189f9a3806f61b53fadeca717ca2a0df2ed8b585abbb973e5c2'),
  'blockNumber': 6946820,
  'contractAddress': None,
  'cumulativeGasUsed': 501002,
  'effectiveGasPrice': 10000000000,
  'from': '0xa2F14D1f80c5fca498b74400f65679738C64B43d',
  'gasUsed': 116348,
  'logs': [
    AttributeDict({
      'address': '0x38f918D0E9F1b721EDaA41302E399fa1B79333a9',
      'blockHash': HexBytes('0x09ef4706780ac189f9a3806f61b53fadeca717ca2a0df2ed8b585abbb973e5c2'),
      'blockNumber': 6946820,
      'data': HexBytes('0x...'),
      'logIndex': 3,
      'removed': False,
      'topics': [
        HexBytes('0x5e3c1311ea442664e8b1611bfabef659120ea7a0a2cfc0667700bebc69cbffe1'),
        HexBytes('0x00000000000000000000000000000000000000000000000000000000000f9edc'),
        HexBytes('0xf02c5a71f4c51012effde095068c09947f8116dea0fa36ee6f416bee404d2db2')
      ],
      'transactionHash': HexBytes('0x4d310ba7d415bd4322e86da90c242b5243709c7ac8173e8f07f7069fe71d2965'),
      'transactionIndex': 3
    }),
    AttributeDict({
      'address': '0xaAe29B0366299461418F5324a79Afc425BE5ae21',
      'blockHash': HexBytes('0x09ef4706780ac189f9a3806f61b53fadeca717ca2a0df2ed8b585abbb973e5c2'),
      'blockNumber': 6946820,
      'data': HexBytes('0x...'),
      'logIndex': 4,
      'removed': False,
      'topics': [
        HexBytes('0xff64905f73a67fb594e0f940a8075a860db489ad991e032f48c81123eb52d60b'),
        HexBytes('0x00000000000000000000000000000000000000000000000000000000000f9edc')
      ],
      'transactionHash': HexBytes('0x4d310ba7d415bd4322e86da90c242b5243709c7ac8173e8f07f7069fe71d2965'),
      'transactionIndex': 3
    }),
    AttributeDict({
      'address': '0xecC354307aC2C7728968e38e23Dbe60127aE1CD0',
      'blockHash': HexBytes('0x09ef4706780ac189f9a3806f61b53fadeca717ca2a0df2ed8b585abbb973e5c2'),
      'blockNumber': 6946820,
      'data': HexBytes('0x'),
      'logIndex': 5,
      'removed': False,
      'topics': [
        HexBytes('0xde92b5b7839f4a2c640f5e3bbb66d415458dadc57a487b0c7fa562ed7c9c896f'),
        HexBytes('0x00000000000000000000000000000000000000000000000000000000000f9edc')
      ],
      'transactionHash': HexBytes('0x4d310ba7d415bd4322e86da90c242b5243709c7ac8173e8f07f7069fe71d2965'),
      'transactionIndex': 3
    })
  ],
  'logsBloom': HexBytes('0x...'),
  'status': 1,
  'to': '0xecC354307aC2C7728968e38e23Dbe60127aE1CD0',
  'transactionHash': HexBytes('0x4d310ba7d415bd4322e86da90c242b5243709c7ac8173e8f07f7069fe71d2965'),
  'transactionIndex': 3
}

###### 可以看到status = 1，交易成功执行了

#### 接下来使用scan.py再次查询arbitrum sepolia链上的layer2.sol的合约中message的字段

layer2.sol
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract L2MessageReceiver {
    string public message;

    event MessageUpdated(string newMessage);

    // 构造函数设置默认值为 "no message"
    constructor() {
        message = "no message";
    }

    // 更新消息内容
    function updateMessage(string memory _newMessage) external {
        message = _newMessage;
        emit MessageUpdated(_newMessage);
    }

    // 展示当前的 message 值
    function getMessage() external view returns (string memory) {
        return message;
    }
}
```
可以看到message字段被成功修改了
```txt
myenvzhenhao@zhenhaos-MacBook-Air arbrige % python3 scan.py
Current message: call from layer1
```

#### 总结
通过retriable ticket这种方式，实现了跨链系统中 Layer 1 与 Layer 2 间消息的顺利传递，验证了系统在多层链间的交互效果。

