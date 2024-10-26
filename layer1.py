from web3 import Web3

# 连接到以太坊 Sepolia 测试网
rpc_url = "https://sepolia.infura.io/v3/a7ebd0bf015b48a697850cbf4cbc44a8"
w3 = Web3(Web3.HTTPProvider(rpc_url))

# 检查连接状态
if not w3.is_connected():
    raise ConnectionError("无法连接到以太坊网络")

# Layer1 合约部署地址（转换为校验和格式）
contract_address = Web3.to_checksum_address("0xecc354307ac2c7728968e38e23dbe60127ae1cd0")

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

# 创建合约实例
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# 设置交易参数
sender_address = Web3.to_checksum_address("0xa2F14D1f80c5fca498b74400f65679738C64B43d")
private_key = "ae37b21a71fbd88c0105e828e9286ce465368843f75c5900d50a8f329926abee"
message = "call from layer1"
gas_fee = w3.to_wei(0.06, "ether")  # 设置gas费，单位为ETH

# 构造交易
transaction = contract.functions.sendMessageToL2(message).build_transaction({
    "from": sender_address,
    "value": gas_fee,
    "gas": 800000,
    "gasPrice": w3.to_wei("10", "gwei"),
    "nonce": w3.eth.get_transaction_count(sender_address),
})

# 签署交易
signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# 发送交易
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

# 等待交易完成
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Transaction receipt:", tx_receipt)
