from decimal import Decimal, getcontext
import json
import os
import requests
from web3 import Web3
from eth_abi import abi
from dotenv import load_dotenv


load_dotenv()


UNISWAP_V2_SWAP_SIGNATURE = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
SUSHISWAP_SWAP_SIGNATURE = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
UNISWAP_V3_SWAP_SIGNATURE = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"


def load_token_metadata(token_metadata_path=None):
    if token_metadata_path is None:
        raise Exception("token_metadata_path is None")
    if not os.path.exists(token_metadata_path):
        return {}
    token_metadata = {}
    with open(token_metadata_path, "r") as file:
        for line in file:
            token_info = line.strip().split("\t")
            if len(token_info) == 4:
                token_address, token_name, token_symbol, token_decimals = token_info
                token_metadata[token_address] = {
                    "token_name": token_name if token_name != "<None>" else None,
                    "token_symbol": token_symbol if token_symbol != "<None>" else None,
                    "token_decimals": int(token_decimals),
                }
    return token_metadata


def load_pool_metadata_map(pool_metadata_path=None):
    if pool_metadata_path is None:
        raise Exception("pool_metadata_path is None")
    if not os.path.exists(pool_metadata_path):
        return {}
    pool_metadata_map = {}
    pool_addresses = set()
    with open(pool_metadata_path, "r") as file:
        for line in file:
            pool_info = line.strip().split("\t")
            if len(pool_info) == 6:
                protocol_name = pool_info[0]
                timestamp_created = int(pool_info[1])
                block_number_created = int(pool_info[2])
                pool_address = pool_info[3]
                token_0_address = pool_info[4]
                token_1_address = pool_info[5]
                pool_metadata_map[pool_address] = {
                    "protocol_name": protocol_name,
                    "timestamp_created": timestamp_created,
                    "block_number_created": block_number_created,
                    "pool_address": pool_address,
                    "token_0_address": token_0_address,
                    "token_1_address": token_1_address,
                }
                pool_addresses.add(pool_address)
    return pool_metadata_map


def apply_decimals_conversion(base_balance, decimals):
    getcontext().prec = max(decimals, 1)  # Ensures division is accurate
    output = Decimal(base_balance) / Decimal(10**decimals)
    return output


class SwapDataParser(object):
    def __init__(self):
        pass

    def decode_sushiswap_amounts(self, raw_log):
        return self.decode_v2_uniswap_amounts(raw_log)

    def decode_v2_uniswap_amounts(self, raw_log: dict):
        data_values = abi.decode(
            types=["uint256", "uint256", "uint256", "uint256"], data=bytes.fromhex(raw_log["data"][2:])
        )
        amount_0_in = data_values[0]
        amount_0_out = data_values[2]
        amount_1_in = data_values[1]
        amount_1_out = data_values[3]
        amount_0_base = str(amount_0_in - amount_0_out)
        amount_1_base = str(amount_1_in - amount_1_out)
        return (amount_0_base, amount_1_base)

    def decode_v3_uniswap_amounts(self, raw_log: dict):
        """
        Note: The difference between V3 and V2 is that amounts are int256 which can be negative.
        """
        types = ["int256", "int256", "uint160", "uint128", "int24"]
        data = bytes.fromhex(raw_log["data"][2:])
        data_values = abi.decode(types=types, data=data)
        amount_0_base = str(data_values[0])
        amount_1_base = str(data_values[1])
        return amount_0_base, amount_1_base

    def get_formatted_log(self, raw_log):
        return raw_log

    def parse_log(self, raw_log, token_metadata_map, pool_metadata_map):
        """
        NOTE: Input 'raw_log' is discarded if:
        1. "removed" is True
        2. pool not in metadata
        """
        formatted_log = self.get_formatted_log(raw_log)
        if formatted_log is None:
            return
        if formatted_log["topic_0"] not in {
            UNISWAP_V2_SWAP_SIGNATURE,
            UNISWAP_V3_SWAP_SIGNATURE,
            SUSHISWAP_SWAP_SIGNATURE,
        }:
            return

        pool_address = formatted_log["address"]
        if pool_address not in pool_metadata_map:
            return

        tx_hash = formatted_log["transaction_hash"]
        log_index = formatted_log["log_index"]
        block_number = formatted_log["block_number"]

        token_0_address = pool_metadata_map[pool_address]["token_0_address"]
        token_1_address = pool_metadata_map[pool_address]["token_1_address"]
        protocol_name = pool_metadata_map[pool_address]["protocol_name"]

        if protocol_name == "uniswap_v2":
            amount_0_base, amount_1_base = self.decode_v2_uniswap_amounts(formatted_log)
        elif protocol_name == "uniswap_v3":
            amount_0_base, amount_1_base = self.decode_v3_uniswap_amounts(formatted_log)
        elif protocol_name == "sushiswap":
            amount_0_base, amount_1_base = self.decode_sushiswap_amounts(formatted_log)
        else:
            return

        if token_0_address not in token_metadata_map:
            return
        if token_1_address not in token_metadata_map:
            return

        token_0_decimals = token_metadata_map[token_0_address]["token_decimals"]
        token_1_decimals = token_metadata_map[token_1_address]["token_decimals"]
        amount_0_token = apply_decimals_conversion(amount_0_base, decimals=token_0_decimals)
        amount_1_token = apply_decimals_conversion(amount_1_base, decimals=token_1_decimals)

        try:
            price_0_1 = float(amount_1_token / amount_0_token)
            price_1_0 = float(amount_0_token / amount_1_token)
        except Exception:
            return

        token_0_name = token_metadata_map[token_0_address].get("token_name")
        token_1_name = token_metadata_map[token_1_address].get("token_name")
        token_0_symbol = token_metadata_map[token_0_address].get("token_symbol")
        token_1_symbol = token_metadata_map[token_1_address].get("token_symbol")

        record = {
            "block_number": block_number,
            "transaction_hash": tx_hash,
            "log_index": log_index,
            "pool_address": pool_address,
            "token_0_address": token_0_address,
            "token_1_address": token_1_address,
            "token_0_symbol": token_0_symbol,
            "token_1_symbol": token_1_symbol,
            "token_0_name": token_0_name,
            "token_1_name": token_1_name,
            "amount_0_base": amount_0_base,
            "amount_1_base": amount_1_base,
            "amount_0_token": float(amount_0_token),
            "amount_1_token": float(amount_1_token),
            "price_0_1": price_0_1,
            "price_1_0": price_1_0,
            "protocol_name": protocol_name,
        }
        return record

    def parse(self, raw_logs, token_metadata_map, pool_metadata_map):
        parsed_swaps = []
        for raw_log in raw_logs:
            parsed_log = self.parse_log(raw_log, token_metadata_map, pool_metadata_map)
            if parsed_log is not None:
                parsed_swaps.append(parsed_log)
        return parsed_swaps


if __name__ == "__main__":
    block_number = 18_000_000
    size = 500
    key = os.environ.get("SYVE_API_KEY", None)
    if key is None:
        raise Exception("Missing API key. Make sure to set SYVE_API_KEY in .env file")

    url = "https://api.syve.ai/v1/filter-api/logs"
    params = {
        "eq:block_number": block_number,
        "size": size,
        "sort": "asc",
        "key": key,
    }
    res = requests.get(url, params=params)
    raw_logs = res.json()
    print(json.dumps(raw_logs[:3], indent=2))

    token_metadata_map = load_token_metadata(token_metadata_path="data/token_metadata.tsv")
    pool_metadata_map = load_pool_metadata_map(pool_metadata_path="data/pool_metadata.tsv")

    parser = SwapDataParser()
    swaps = parser.parse(
        raw_logs=raw_logs,
        token_metadata_map=token_metadata_map,
        pool_metadata_map=pool_metadata_map,
    )
    print(json.dumps(swaps[:3], indent=2))
