# syve-swap-parser

Ensure to install the dependencies in `requirements.txt`.

`run.py` fetches raw logs and returns parsed swap data.

Example raw logs:

```
[
  {
    "record_index": 7200000000000000,
    "block_number": 18000000,
    "timestamp": 1693066895,
    "transaction_hash": "0x16e199673891df518e25db2ef5320155da82a3dd71a677e7d84363251885d133",
    "transaction_index": 0,
    "log_index": 0,
    "address": "0xfd14567eaf9ba941cb8c8a94eec14831ca7fd1b4",
    "data": "0x01e14e6ce75f248c88ee1187bcf6c75f8aea18fbd3d927fe2d63947fcd8cb18c641569e8ee18f93c861576fe0c882e5c61a310ae8e400be6629561160d2a901f0619e35040579fa202bc3f84077a72266b2a4e744baa92b433497bc23d6aeda4",
    "topic_0": "0xb8b9c39aeba1cfd98c38dfeebe11c2f7e02b334cbe9f05f22b442a5d9c1ea0c5"
  },
  {
    "record_index": 7200000000000001,
    "block_number": 18000000,
    "timestamp": 1693066895,
    "transaction_hash": "0x6742cd57e6aefce4b96887bb3090371ac49414c6b45a21e43d9e41e0ea9ed5ab",
    "transaction_index": 1,
    "log_index": 1,
    "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "data": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "topic_0": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
    "topic_1": "0x0000000000000000000000000865dfee215af901c0ff9e0db44b96074e434c63",
    "topic_2": "0x000000000000000000000000811b105d5d5d9e0b709fbf9ce0fbb11ce4b1c093"
  },
  {
    "record_index": 7200000000000002,
    "block_number": 18000000,
    "timestamp": 1693066895,
    "transaction_hash": "0x6742cd57e6aefce4b96887bb3090371ac49414c6b45a21e43d9e41e0ea9ed5ab",
    "transaction_index": 1,
    "log_index": 2,
    "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "data": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "topic_0": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
    "topic_1": "0x0000000000000000000000004226ef7a6e061053a9fcadf09f4a1f04570ec29b",
    "topic_2": "0x0000000000000000000000008c5942f23f55601a311569d29c4698d0a9be6288"
  }
]
```

Example parsed swap data:

```
[
  {
    "block_number": 18000000,
    "transaction_hash": "0xb243a19756f159a6f80a5b972596957cfbd671970ab414a7cac4f895b892dca6",
    "log_index": 61,
    "pool_address": "0x102ca530f96c0f9135df4fb8e0ea8f7c7216e6a1",
    "token_0_address": "0x6541e93492d87a2b6b896e0086c2814a3dda4990",
    "token_1_address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "token_0_symbol": "QUIRK",
    "token_1_symbol": "WETH",
    "token_0_name": "QuokkaCoin",
    "token_1_name": "Wrapped Ether",
    "amount_0_base": "-109382250728836",
    "amount_1_base": "40000000000000000",
    "amount_0_token": -1093822.5,
    "amount_1_token": 0.04,
    "price_0_1": -3.6569004568840007e-08,
    "price_1_0": -27345562.5,
    "protocol_name": "uniswap_v2"
  },
  {
    "block_number": 18000000,
    "transaction_hash": "0x6ffdaee7a47cd177c5280bb91cb2b82186c26056e7ade387a5c70b8137fd434e",
    "log_index": 71,
    "pool_address": "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc",
    "token_0_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "token_1_address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "token_0_symbol": "USDC",
    "token_1_symbol": "WETH",
    "token_0_name": "USD Coin",
    "token_1_name": "Wrapped Ether",
    "amount_0_base": "95000000",
    "amount_1_base": "-57414644167788278",
    "amount_0_token": 95.0,
    "amount_1_token": -0.05741464416778828,
    "price_0_1": -0.0006043646754504029,
    "price_1_0": -1654.63012750497,
    "protocol_name": "uniswap_v2"
  },
  {
    "block_number": 18000000,
    "transaction_hash": "0x6ffdaee7a47cd177c5280bb91cb2b82186c26056e7ade387a5c70b8137fd434e",
    "log_index": 75,
    "pool_address": "0x62931a522e998fecc1df96656054bace35e3ec7c",
    "token_0_address": "0x7721a4cb6190edb11d47f51c20968436eccdafb8",
    "token_1_address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "token_0_symbol": "GUISE",
    "token_1_symbol": "WETH",
    "token_0_name": "GUISE",
    "token_1_name": "Wrapped Ether",
    "amount_0_base": "-120727887081455806622",
    "amount_1_base": "57414644167788278",
    "amount_0_token": -120.7278870814558,
    "amount_1_token": 0.05741464416778828,
    "price_0_1": -0.00047557068673827023,
    "price_1_0": -2102.736833631525,
    "protocol_name": "uniswap_v2"
  }
]
```