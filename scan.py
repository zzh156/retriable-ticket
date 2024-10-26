from web3 import Web3

# Arbitrum Sepolia RPC URL (替换为您的实际 RPC URL)
arb_sepolia_rpc = "https://arbitrum-sepolia.infura.io/v3/a7ebd0bf015b48a697850cbf4cbc44a8"
web3 = Web3(Web3.HTTPProvider(arb_sepolia_rpc))

# 合约地址
contract_address = "0x12fBAf906c3c4af268976bF855B2159813909D69"

# 合约 ABI
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

# 合约实例
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# 调用 getMessage 方法来获取 message 值
def get_message():
    try:
        message = contract.functions.getMessage().call()
        print("Current message:", message)
    except Exception as e:
        print("Error fetching message:", e)

# 执行查询
if __name__ == "__main__":
    get_message()
